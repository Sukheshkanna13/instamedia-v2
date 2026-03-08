"""
Reusable Google Gemini API client specifically for ADs Intelligence fallback.
Acts as a fallback when the AWS Bedrock client returns 400 Operation Not Allowed.
Uses the official google-genai library.
"""

import os
import json
from google import genai
from google.genai import types
from config import Config
from services.bedrock.bedrock_client import BedrockInvokeError

class GeminiAdsClient:
    def __init__(self):
        self.api_key = Config.GEMINI_ADS_API_KEY
        # Set environment variable specifically for the genai client initialization
        os.environ["GEMINI_API_KEY"] = self.api_key
        self.client = genai.Client()
        self.model = "gemini-2.5-flash"

    def invoke(self, prompt: str, max_tokens: int = 1500, temperature: float = 0.7) -> str:
        """
        Send a prompt to Google Gemini API.
        Mirrors the BedrockClient methodology.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            return response.text

        except Exception as e:
            raise BedrockInvokeError(f"Gemini API error: {str(e)}") from e

    def invoke_json(self, prompt: str, max_tokens: int = 1500) -> dict:
        """
        Same as invoke() but critically resilient for JSON parsing on Free Models.
        Mirrors BedrockClient exactly so it can be swapped effortlessly.
        Use Gemini's system instructions to guarantee JSON format + aggressive regex cleanup.
        """
        import re
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3, # Keep low for structured output consistency
                    max_output_tokens=max_tokens,
                    response_mime_type="application/json"
                )
            )
            raw = response.text
            
            # The API should return pure JSON since we requested application/json,
            # but free tier models sometimes hallucinate preamble text or markdown anyway.
            cleaned = raw.strip()
            
            # Remove Markdown Fences
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            cleaned = cleaned.strip()
            
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                # Fallback: Aggressive Regex Search to find the first '{' and last '}'
                try:
                    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                    if match:
                        return json.loads(match.group(0))
                except Exception:
                    pass

                print(f"⚠️ Extreme JSON Parse Failure on Gemini Fallback:\n{raw}")
                return {
                    "error": "JSON parse failed from Gemini ADs fallback even after aggressive regex.",
                    "raw_response": raw if 'raw' in locals() else "Unknown"
                }

        except Exception as e:
            raise BedrockInvokeError(f"Gemini API JSON invoke error: {str(e)}") from e
