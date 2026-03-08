import os
from dotenv import load_dotenv

# Ensure env vars are loaded
load_dotenv(override=True)

class Config:
    # ── META Ad Library ──────────────────────────────────────────────
    META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")

    # ── SerpAPI (YouTube scraping) ────────────────────────────────────
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")

    # ── Amazon Bedrock (API Key auth — NOT boto3/IAM) ─────────────────
    BEDROCK_API_KEY   = os.getenv("BEDROCK_API_KEY")   # Bearer token key
    BEDROCK_REGION    = os.getenv("BEDROCK_REGION", "us-east-1")
    BEDROCK_MODEL_ID  = os.getenv("BEDROCK_LLM_MODEL_ID", "deepseek.v3.2")
    
    # ── Google Gemini API (Fallback for Bedrock ADs) ───────────────────────
    GEMINI_ADS_API_KEY = os.getenv("GEMINI_ADS_API_KEY")

    # ── ChromaDB (local vector store) ────────────────────────────────
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_ads_db")
