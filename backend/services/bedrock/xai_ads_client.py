import json
import re
from openai import OpenAI
from config import Config
from services.bedrock.bedrock_client import BedrockInvokeError

class XaiAdsClient:
    """
    Reusable xAI API client (using X.AI's OpenAI-compatible endpoint)
    Acts as a fallback when the AWS Bedrock client returns 400 Operation Not Allowed.
    """
    def __init__(self):
        import os
        self.api_key = Config.XAI_ADS_API_KEY or os.environ.get("XAI_ADS_API_KEY", "missing_key")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1",
        )
        self.model = "grok-2-latest"

    def invoke(self, prompt: str, max_tokens: int = 1500, temperature: float = 0.7) -> str:
        """
        Send a prompt to xAI API.
        Mirrors the BedrockClient methodology.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a top-tier digital marketing strategist. Follow all format constraints strictly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return completion.choices[0].message.content

        except Exception as e:
            raise BedrockInvokeError(f"xAI API error: {str(e)}") from e

    def invoke_json(self, prompt: str, max_tokens: int = 1500) -> dict:
        """
        Same as invoke() but critically resilient for JSON parsing.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data-driven digital marketer. You MUST return ONLY a rigid JSON dictionary object, and absolutely nothing else. No markdown fences. Start immediately with '{' and end with '}'."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3, # Keep low for structural consistency
                max_tokens=max_tokens,
            )
            raw = completion.choices[0].message.content
            
            cleaned = raw.strip()
            # Remove Markdown Fences if Grok adds them
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            cleaned = cleaned.strip()
            
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                # Fallback: Aggressive Regex Search
                try:
                    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                    if match:
                        return json.loads(match.group(0))
                except Exception:
                    pass

                print(f"⚠️ Extreme JSON Parse Failure on xAI Fallback:\n{raw}")
                return {
                    "error": "JSON parse failed from xAI ADs fallback even after aggressive regex.",
                    "raw_response": raw if 'raw' in locals() else "Unknown"
                }

        except Exception as e:
            raise BedrockInvokeError(f"xAI API JSON invoke error: {str(e)}") from e
