"""
Reusable Bedrock HTTP client using API Key bearer token auth.
All Bedrock-dependent services import and use this class.
Never use boto3 for Bedrock calls in this project.
"""

import requests
import json
from config import Config


class BedrockClient:
    def __init__(self):
        self.api_key = Config.BEDROCK_API_KEY
        self.region = Config.BEDROCK_REGION
        self.model_id = Config.BEDROCK_MODEL_ID
        self.base_url = (
            f"https://bedrock-runtime.{self.region}.amazonaws.com"
            f"/model/{self.model_id}/invoke"
        )
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def invoke(self, prompt: str, max_tokens: int = 1500, temperature: float = 0.7) -> str:
        """
        Send a prompt to Bedrock and return the raw text response.

        Uses the Bedrock native /invoke endpoint with bearer token auth.
        The request body format follows the Bedrock Converse API schema.

        Args:
            prompt: The full prompt string to send
            max_tokens: Max output tokens (default 1500)
            temperature: Creativity level 0.0-1.0 (default 0.7)

        Returns:
            Raw text string from the model response

        Raises:
            BedrockInvokeError: If the HTTP call fails or response is malformed
        """
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature
            }
        }

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=body,
                timeout=30  # 30s timeout — Bedrock can be slow on cold starts
            )
            response.raise_for_status()
            data = response.json()

            # Bedrock native response shape:
            # data["output"]["message"]["content"][0]["text"]
            return data["output"]["message"]["content"][0]["text"]

        except requests.exceptions.HTTPError as e:
            raise BedrockInvokeError(
                f"Bedrock HTTP error {response.status_code}: {response.text}"
            ) from e
        except (KeyError, IndexError) as e:
            raise BedrockInvokeError(
                f"Unexpected Bedrock response shape: {data}"
            ) from e
        except requests.exceptions.Timeout:
            raise BedrockInvokeError("Bedrock request timed out after 30s")

    def invoke_json(self, prompt: str, max_tokens: int = 1500) -> dict:
        """
        Same as invoke() but automatically parses the response as JSON.
        Use this for all structured output calls (research, tuning, analytics).

        The prompt MUST instruct the model to return valid JSON only.
        Strips markdown code fences (```json ... ```) if model adds them.
        """
        raw = self.invoke(prompt, max_tokens=max_tokens, temperature=0.3)
        # Lower temperature for JSON to reduce hallucinated structure

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
                "error": "JSON parse failed",
                "raw_response": raw
            }


class BedrockInvokeError(Exception):
    """Raised when a Bedrock API call fails."""
    pass
