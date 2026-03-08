"""
Reusable Hugging Face HTTP client.
Acts as a fallback when the AWS Bedrock client returns 400 Operation Not Allowed (or OpenAI runs out of quota).
Uses the native Hugging Face InferenceClient.
"""

import json
from huggingface_hub import InferenceClient
from config import Config
from services.bedrock.bedrock_client import BedrockInvokeError

class HuggingFaceClient:
    def __init__(self):
        self.api_key = Config.HF_TOKEN
        self.client = InferenceClient(api_key=self.api_key)
        self.model = "deepseek-ai/DeepSeek-V3.2-Exp:novita"

    def invoke(self, prompt: str, max_tokens: int = 1500, temperature: float = 0.7) -> str:
        """
        Send a prompt to native Hugging Face API.
        Mirrors the BedrockClient methodology.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )
            
            # Extract content from completion object directly
            return completion.choices[0].message.content

        except Exception as e:
            raise BedrockInvokeError(f"Hugging Face HTTP error: {str(e)}") from e

    def invoke_json(self, prompt: str, max_tokens: int = 1500) -> dict:
        """
        Same as invoke() but automatically parses the response as JSON.
        Mirrors BedrockClient exactly so it can be swapped effortlessly.
        """
        # Instruct model specifically to return JSON
        json_prompt = prompt + "\n\nIMPORTANT: Return ONLY valid JSON."
        raw = self.invoke(json_prompt, max_tokens=max_tokens, temperature=0.3)

        # Strip markdown fences if model wraps JSON in them
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Return structured error so callers don't crash
            return {
                "error": "JSON parse failed from Hugging Face fallback",
                "raw_response": raw
            }
