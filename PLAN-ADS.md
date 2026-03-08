# Instamedia AI — ADs Intelligence Feature (Bedrock API Key Auth)
## Agent Implementation Prompt v2

---

## CONTEXT & PROJECT OVERVIEW

You are working on **Instamedia AI** — an AI-driven marketing agency assistant built with a **Flask backend**. The existing system already handles ideation, content planning, AI writing, content calendar, and AI image/carousel/video generation.

You are now implementing the **ADs Intelligence Module** — three tightly integrated sub-systems:

1. **AD Scraping & Retrieval Pipeline** — Real-time best-performing ads from META + YouTube
2. **RAG-Powered AD Recommendation Engine** — Semantic retrieval + LLM campaign copy generation
3. **Amazon Bedrock Marketing Intelligence** — Market research + campaign tuning + analytics

**CRITICAL AUTH NOTE:**
This implementation uses **Amazon Bedrock API Key authentication** (the newer bearer token method),
NOT the traditional boto3 IAM credential method. Do NOT use `boto3` for Bedrock calls anywhere.
All Bedrock calls are made via direct HTTP requests with an `Authorization: Bearer <key>` header.

---

## BEDROCK API KEY AUTH — HOW IT WORKS

Amazon Bedrock now supports API Key authentication as an alternative to AWS IAM credentials.
Instead of `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` passed into boto3, you use a single
bearer token in the HTTP Authorization header — similar to OpenAI's auth pattern.

### Base Bedrock Endpoint Pattern:
```
POST https://bedrock-runtime.{REGION}.amazonaws.com/model/{MODEL_ID}/invoke
Headers:
  Authorization: Bearer {BEDROCK_API_KEY}
  Content-Type: application/json
  Accept: application/json
```

### Model ID to use throughout:
```
amazon.nova-pro-v1:0
```
(Use Nova Pro — it's Bedrock-native, cost-effective, and supports the API Key auth flow well.
You can also swap to `anthropic.claude-3-sonnet-20240229-v1:0` if your key has access to it.)

### Request body format (Bedrock Converse-compatible):
```json
{
  "messages": [
    { "role": "user", "content": [{ "text": "your prompt here" }] }
  ],
  "inferenceConfig": {
    "maxTokens": 1500,
    "temperature": 0.7
  }
}
```

### Response parsing:
```python
response_json = response.json()
text = response_json["output"]["message"]["content"][0]["text"]
```

---

## BEDROCK CLIENT WRAPPER — BUILD THIS FIRST

**File to create:** `services/bedrock/bedrock_client.py`

```python
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
```

---

## CONFIGURATION

**File to update:** `config.py`

```python
import os

class Config:
    # ── META Ad Library ──────────────────────────────────────────────
    META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")

    # ── SerpAPI (YouTube scraping) ────────────────────────────────────
    SERPAPI_KEY = os.getenv("SERPAPI_KEY")

    # ── Amazon Bedrock (API Key auth — NOT boto3/IAM) ─────────────────
    BEDROCK_API_KEY   = os.getenv("BEDROCK_API_KEY")   # Bearer token key
    BEDROCK_REGION    = os.getenv("BEDROCK_REGION", "us-east-1")
    BEDROCK_MODEL_ID  = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")

    # ── ChromaDB (local vector store) ────────────────────────────────
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_ads_db")
```

**.env file template** (never commit this):

```env
META_ACCESS_TOKEN=your_meta_ad_library_token_here
SERPAPI_KEY=your_serpapi_key_here
BEDROCK_API_KEY=your_fresh_rotated_bedrock_api_key_here
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
CHROMA_DB_PATH=./chroma_ads_db
```

---

## LAYER 1 — AD SCRAPING PIPELINE

### 1A. META Ad Library Scraper

**File to create:** `services/ad_scraper/meta_scraper.py`

```python
import requests
from typing import List, Dict
from datetime import datetime

META_AD_LIBRARY_BASE = "https://graph.facebook.com/v19.0/ads_archive"


class MetaAdScraper:
    def __init__(self, access_token: str):
        self.access_token = access_token

    def fetch_ads(self, keyword: str, niche: str, limit: int = 50) -> List[Dict]:
        """
        Fetch active, best-performing ads from META Ad Library API.

        Performance proxy used: impressions / spend = efficiency score.
        Higher efficiency = more eyeballs per dollar = well-optimized ad.
        Ads are sorted by efficiency score descending before returning.
        """
        params = {
            "access_token": self.access_token,
            "search_terms": keyword,
            "ad_type": "ALL",
            "ad_reached_countries": ["US"],
            "fields": (
                "id,ad_creative_body,ad_creative_link_caption,"
                "ad_delivery_start_time,impressions,spend,"
                "page_name,ad_snapshot_url"
            ),
            "limit": limit,
        }

        response = requests.get(META_AD_LIBRARY_BASE, params=params, timeout=15)
        response.raise_for_status()
        raw_ads = response.json().get("data", [])
        return self._normalize(raw_ads, niche=niche)

    def _normalize(self, raw_ads: List[Dict], niche: str) -> List[Dict]:
        normalized = []
        for ad in raw_ads:
            impressions = ad.get("impressions", {})
            spend = ad.get("spend", {})
            impression_score = int(impressions.get("lower_bound", 0))
            spend_lower = int(spend.get("lower_bound", 0))
            efficiency = impression_score / max(spend_lower, 1)

            normalized.append({
                "platform": "META",
                "ad_id": ad.get("id", ""),
                "headline": ad.get("ad_creative_link_caption", ""),
                "body": ad.get("ad_creative_body", ""),
                "page_name": ad.get("page_name", ""),
                "preview_url": ad.get("ad_snapshot_url", ""),
                "impressions_lower": impression_score,
                "spend_lower": spend_lower,
                "efficiency_score": round(efficiency, 4),
                "niche": niche,
                "scraped_at": datetime.utcnow().isoformat(),
                "run_days": self._calc_run_days(ad.get("ad_delivery_start_time")),
            })

        return sorted(normalized, key=lambda x: x["efficiency_score"], reverse=True)

    def _calc_run_days(self, start_time: str) -> int:
        if not start_time:
            return 0
        start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        return (datetime.utcnow().replace(tzinfo=start.tzinfo) - start).days
```

---

### 1B. YouTube Ad Scraper via SerpAPI

**File to create:** `services/ad_scraper/youtube_scraper.py`

```python
import requests
from typing import List, Dict
from datetime import datetime

SERPAPI_BASE = "https://serpapi.com/search"


class YouTubeAdScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_ads(self, keyword: str, niche: str, limit: int = 20) -> List[Dict]:
        """
        Fetch YouTube video ads via SerpAPI.
        Search strategy: "{keyword} advertisement" surfaces sponsored content.
        Performance proxy: raw view count (higher views = proven engagement).
        """
        params = {
            "engine": "youtube",
            "search_query": f"{keyword} advertisement",
            "api_key": self.api_key,
        }

        response = requests.get(SERPAPI_BASE, params=params, timeout=15)
        response.raise_for_status()
        videos = response.json().get("video_results", [])[:limit]
        return self._normalize(videos, niche=niche)

    def _normalize(self, videos: List[Dict], niche: str) -> List[Dict]:
        normalized = []
        for v in videos:
            views_raw = v.get("views", "0").replace(",", "").replace(" views", "")
            try:
                views = int(views_raw)
            except ValueError:
                views = 0

            video_id = v.get("id", {}).get("videoId", "")
            normalized.append({
                "platform": "YOUTUBE",
                "ad_id": video_id,
                "headline": v.get("title", ""),
                "body": v.get("description", ""),
                "channel_name": v.get("channel", {}).get("name", ""),
                "preview_url": v.get("thumbnail", {}).get("static", ""),
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "views": views,
                "efficiency_score": round(views / 1_000_000, 4),
                "duration": v.get("length", ""),
                "niche": niche,
                "scraped_at": datetime.utcnow().isoformat(),
                "run_days": 0,
            })

        return sorted(normalized, key=lambda x: x["views"], reverse=True)
```

---

### 1C. Ingestion Service (Scraper Orchestrator + ChromaDB Interface)

**File to create:** `services/ad_scraper/ingestion_service.py`

```python
"""
Orchestrates META + YouTube scrapers and manages the ChromaDB vector store.

Architecture note:
- ChromaDB stores ad text as embeddings (semantic vectors)
- Embeddings allow similarity search: "fitness ads" finds "gym nutrition" too
- This is the RAG retrieval layer — retrieved ads become LLM context
"""

import chromadb
from chromadb.utils import embedding_functions
from services.ad_scraper.meta_scraper import MetaAdScraper
from services.ad_scraper.youtube_scraper import YouTubeAdScraper
from config import Config


class ADIngestionService:
    def __init__(self):
        # PersistentClient = ChromaDB stores to disk between app restarts
        self.chroma_client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)

        # all-MiniLM-L6-v2: fast, free, local — good semantic similarity
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Single cross-platform collection, filtered at query time by niche/platform
        self.collection = self.chroma_client.get_or_create_collection(
            name="best_performing_ads",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

        self.meta_scraper = MetaAdScraper(Config.META_ACCESS_TOKEN)
        self.yt_scraper = YouTubeAdScraper(Config.SERPAPI_KEY)

    def scrape_and_ingest(
        self, keyword: str, niche: str, platforms: list = ["META", "YOUTUBE"]
    ) -> dict:
        """
        Full pipeline: scrape → normalize → embed → upsert into ChromaDB.

        Upsert (not insert) means re-running for the same keyword refreshes
        existing data rather than duplicating it. This is how we keep the
        vector store current without manual cleanup.
        """
        all_ads = []

        if "META" in platforms:
            all_ads.extend(self.meta_scraper.fetch_ads(keyword, niche))

        if "YOUTUBE" in platforms:
            all_ads.extend(self.yt_scraper.fetch_ads(keyword, niche))

        if not all_ads:
            return {"status": "no_ads_found", "count": 0}

        # ChromaDB requires: documents (text to embed), metadatas, ids
        documents = [f"{ad['headline']} {ad['body']}" for ad in all_ads]
        metadatas = all_ads
        ids = [f"{ad['platform']}_{ad['ad_id']}_{ad['scraped_at']}" for ad in all_ads]

        self.collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        return {"status": "success", "ingested_count": len(all_ads)}

    def query_similar_ads(
        self, campaign_brief: str, niche: str, top_k: int = 8
    ) -> list:
        """
        RAG RETRIEVAL — core of the recommendation system.

        Embeds the campaign brief → finds top-K semantically similar ads
        in the vector store → returns them with similarity scores attached.

        These retrieved ads become the CONTEXT block fed to Bedrock LLM.
        This is why results are relevant: LLM sees real high-performing ads,
        not just its training data.
        """
        results = self.collection.query(
            query_texts=[campaign_brief],
            n_results=top_k,
            where={"niche": niche},
            include=["documents", "metadatas", "distances"]
        )

        ads = results["metadatas"][0]
        distances = results["distances"][0]

        # Cosine distance → similarity: similarity = 1 - distance
        for ad, dist in zip(ads, distances):
            ad["similarity_score"] = round(1 - dist, 4)

        return ads
```

---

## LAYER 2 — RAG-POWERED AD RECOMMENDATION ENGINE

**File to create:** `services/rag/ad_recommendation_engine.py`

```python
"""
RAG pipeline for generating tailored AD campaign recommendations.

Flow:
1. User submits campaign brief (keyword, goal, audience, budget, tone)
2. Brief is embedded → top-K similar performing ads retrieved from ChromaDB
3. Retrieved ads formatted as context block
4. Context + brief sent to Bedrock (via BedrockClient, API Key auth)
5. Bedrock returns structured campaign recommendations as JSON
"""

import json
from services.ad_scraper.ingestion_service import ADIngestionService
from services.bedrock.bedrock_client import BedrockClient


class ADRecommendationEngine:
    def __init__(self):
        self.ingestion_service = ADIngestionService()
        self.bedrock = BedrockClient()

    def generate_ad_recommendations(self, user_input: dict) -> dict:
        """
        Full RAG pipeline entry point.

        user_input schema:
        {
            "keyword":         str,  e.g. "fitness supplements"
            "niche":           str,  e.g. "health & wellness"
            "platforms":       list, e.g. ["META", "YOUTUBE"]
            "campaign_goal":   str,  e.g. "drive product page visits"
            "target_audience": str,  e.g. "men 25-40 interested in fitness"
            "budget":          str,  e.g. "$500/month"
            "tone":            str,  e.g. "energetic and motivational"
        }
        """
        # Step 1: Compose semantic brief for vector search
        campaign_brief = (
            f"Campaign for {user_input['keyword']} "
            f"targeting {user_input['target_audience']}. "
            f"Goal: {user_input['campaign_goal']}. "
            f"Tone: {user_input['tone']}."
        )

        # Step 2: Retrieve top-K similar high-performing ads (RAG retrieval)
        similar_ads = self.ingestion_service.query_similar_ads(
            campaign_brief=campaign_brief,
            niche=user_input["niche"],
            top_k=8
        )

        # Step 3: Format retrieved ads as readable context for LLM
        context_block = self._format_ads_as_context(similar_ads)

        # Step 4: Build full RAG prompt
        prompt = self._build_rag_prompt(user_input, context_block)

        # Step 5: Call Bedrock (API Key auth via BedrockClient)
        recommendations = self.bedrock.invoke_json(prompt, max_tokens=2000)

        return {
            "recommendations": recommendations,
            "retrieved_ads": similar_ads,
            "brief_used": campaign_brief
        }

    def _format_ads_as_context(self, ads: list) -> str:
        lines = ["=== REAL-TIME BEST PERFORMING ADS (Retrieved Context) ===\n"]
        for i, ad in enumerate(ads, 1):
            lines.append(
                f"AD #{i} | Platform: {ad['platform']} | "
                f"Efficiency Score: {ad.get('efficiency_score', 'N/A')} | "
                f"Similarity: {ad.get('similarity_score', 'N/A')}\n"
                f"Headline: {ad.get('headline', '')}\n"
                f"Body: {ad.get('body', '')}\n"
                "---"
            )
        return "\n".join(lines)

    def _build_rag_prompt(self, user_input: dict, context_block: str) -> str:
        return f"""You are an expert digital marketing strategist for Instamedia AI,
an AI-powered marketing agency assistant.

You have been provided with real-time data of the best-performing ads
in the {user_input['niche']} niche. Use this as grounding context.

{context_block}

=== USER CAMPAIGN BRIEF ===
Keyword/Product: {user_input['keyword']}
Niche: {user_input['niche']}
Platforms: {', '.join(user_input['platforms'])}
Campaign Goal: {user_input['campaign_goal']}
Target Audience: {user_input['target_audience']}
Budget: {user_input['budget']}
Desired Tone: {user_input['tone']}

=== YOUR TASK ===
Based on the real-time best-performing ads above AND the campaign brief,
generate a complete campaign recommendation package.

Return ONLY valid JSON (no markdown, no explanation) with these exact keys:

{{
  "headlines": ["option1", "option2", "option3"],
  "body_copies": {{
    "short": "...",
    "medium": "...",
    "long": "..."
  }},
  "hooks": ["hook1", "hook2", "hook3", "hook4", "hook5"],
  "ctas": ["cta1", "cta2", "cta3"],
  "creative_direction": {{
    "visuals": "...",
    "colors": "...",
    "formats": "...",
    "inspiration_from_top_ads": "..."
  }},
  "targeting_suggestions": {{
    "interests": [],
    "behaviors": [],
    "demographics": "",
    "lookalike_seed": ""
  }},
  "budget_allocation": {{
    "META": "...",
    "YOUTUBE": "...",
    "rationale": "..."
  }}
}}"""
```

---

## LAYER 3 — AMAZON BEDROCK MARKETING INTELLIGENCE (3 Parallel Agents)

**File to create:** `services/bedrock/marketing_intelligence.py`

```python
"""
Three marketing intelligence agents running in parallel via ThreadPoolExecutor.

Why parallel?
- Each agent is independent (no data dependency between them)
- Sequential would take ~9-12s (3 × 3-4s per Bedrock call)
- Parallel takes ~3-4s (longest single call)
- ThreadPoolExecutor is ideal here: I/O-bound tasks (HTTP calls to Bedrock)
  release the GIL, so threads run truly concurrently in Python

Agents:
1. Market Research Agent   — keyword → industry landscape + competitor intel
2. Campaign Tuning Agent   — draft ad → specific rewrites + A/B test ideas
3. Analytics Agent         — metrics input → chart data + prioritized actions
"""

import concurrent.futures
from typing import Dict
from services.bedrock.bedrock_client import BedrockClient


class MarketingIntelligenceService:
    def __init__(self):
        # Each agent gets its own BedrockClient instance
        # (separate HTTP sessions for true parallel requests)
        self.research_client  = BedrockClient()
        self.tuning_client    = BedrockClient()
        self.analytics_client = BedrockClient()

    def get_full_intelligence(self, request: Dict) -> Dict:
        """
        Run all 3 agents in parallel and merge results.

        request schema:
        {
            "keyword":   str,
            "niche":     str,
            "ad_draft":  str,   # current draft ad copy for tuning agent
            "metrics": {        # current campaign metrics for analytics agent
                "impressions": int,
                "clicks":      int,
                "conversions": int,
                "spend":       float,
                "ctr":         float,
                "cpc":         float,
                "roas":        float
            }
        }
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_research  = executor.submit(self._market_research_agent, request)
            future_tuning    = executor.submit(self._campaign_tuning_agent, request)
            future_analytics = executor.submit(self._analytics_agent, request)

            # .result() blocks until each future completes
            # All 3 run simultaneously — total time = slowest single call
            research_result  = future_research.result()
            tuning_result    = future_tuning.result()
            analytics_result = future_analytics.result()

        return {
            "market_research":    research_result,
            "campaign_tuning":    tuning_result,
            "analytics_insights": analytics_result
        }

    def _market_research_agent(self, request: Dict) -> Dict:
        prompt = f"""You are a market research analyst for a digital marketing agency.

Keyword: {request['keyword']}
Niche: {request['niche']}

Return ONLY valid JSON (no markdown) with this exact structure:
{{
  "market_size_trends": "...",
  "competitor_analysis": [
    {{ "brand": "...", "strategy": "...", "weakness": "..." }}
  ],
  "audience_insights": {{
    "demographics": "...",
    "psychographics": "...",
    "pain_points": [],
    "motivations": []
  }},
  "seasonal_patterns": "...",
  "content_angles": ["angle1", "angle2", "angle3", "angle4", "angle5"],
  "emerging_opportunities": ["opp1", "opp2", "opp3"]
}}"""
        return self.research_client.invoke_json(prompt)

    def _campaign_tuning_agent(self, request: Dict) -> Dict:
        ad_draft = request.get("ad_draft", "No draft provided yet.")
        prompt = f"""You are a performance marketing expert specializing in ad optimization.

Current Ad Draft:
{ad_draft}

Niche: {request['niche']}
Keyword: {request['keyword']}

Return ONLY valid JSON (no markdown) with this exact structure:
{{
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "rewrites": [
    {{ "original": "...", "improved": "...", "reason": "..." }}
  ],
  "ab_tests": [
    {{ "element": "...", "variant_a": "...", "variant_b": "...", "hypothesis": "..." }}
  ],
  "platform_tweaks": {{
    "META": "...",
    "YOUTUBE": "..."
  }},
  "compliance_notes": ["note1", "note2"]
}}"""
        return self.tuning_client.invoke_json(prompt)

    def _analytics_agent(self, request: Dict) -> Dict:
        m = request.get("metrics", {})
        prompt = f"""You are a data analytics expert for digital advertising campaigns.

Campaign Metrics:
- Impressions:   {m.get('impressions', 0):,}
- Clicks:        {m.get('clicks', 0):,}
- Conversions:   {m.get('conversions', 0):,}
- Total Spend:   ${m.get('spend', 0):,.2f}
- CTR:           {m.get('ctr', 0)}%
- CPC:           ${m.get('cpc', 0)}
- ROAS:          {m.get('roas', 0)}x

Industry Benchmarks for {request['niche']}:
- Average CTR (META): 0.9% | (YouTube): 0.4%
- Average CPC: $0.50–$2.00
- Average ROAS: 2–4x

Return ONLY valid JSON (no markdown) with this exact structure:
{{
  "performance_diagnosis": {{
    "overall_grade": "A/B/C/D/F",
    "summary": "...",
    "metric_breakdown": [
      {{ "metric": "CTR", "status": "above/below/at benchmark", "note": "..." }}
    ]
  }},
  "optimization_priority": {{
    "top_priority": "...",
    "reason": "...",
    "expected_impact": "..."
  }},
  "chart_data": {{
    "funnel": [
      {{ "stage": "Impressions", "value": {m.get('impressions', 0)} }},
      {{ "stage": "Clicks",      "value": {m.get('clicks', 0)} }},
      {{ "stage": "Conversions", "value": {m.get('conversions', 0)} }}
    ],
    "benchmark_comparison": [
      {{ "metric": "CTR",  "yours": {m.get('ctr', 0)},  "benchmark": 0.9 }},
      {{ "metric": "ROAS", "yours": {m.get('roas', 0)}, "benchmark": 3.0 }},
      {{ "metric": "CPC",  "yours": {m.get('cpc', 0)},  "benchmark": 1.25 }}
    ]
  }},
  "action_items": [
    {{ "priority": 1, "action": "...", "timeline": "this week", "expected_result": "..." }},
    {{ "priority": 2, "action": "...", "timeline": "next week", "expected_result": "..." }},
    {{ "priority": 3, "action": "...", "timeline": "this month", "expected_result": "..." }}
  ],
  "projections": {{
    "30_day_optimized": {{
      "ctr": "...", "cpc": "...", "roas": "...", "note": "..."
    }}
  }}
}}"""
        return self.analytics_client.invoke_json(prompt)
```

---

## LAYER 4 — FLASK ROUTES

**File to create:** `routes/ads_intelligence.py`

```python
from flask import Blueprint, request, jsonify
from services.ad_scraper.ingestion_service import ADIngestionService
from services.rag.ad_recommendation_engine import ADRecommendationEngine
from services.bedrock.marketing_intelligence import MarketingIntelligenceService

ads_bp = Blueprint("ads", __name__, url_prefix="/api/ads")

# Instantiate services once at module level (not per-request)
ingestion_service    = ADIngestionService()
recommendation_engine = ADRecommendationEngine()
intelligence_service  = MarketingIntelligenceService()


@ads_bp.route("/scrape", methods=["POST"])
def scrape_ads():
    """
    Trigger on-demand ad scraping for a keyword + niche.
    Populates ChromaDB vector store. Call before /recommend.

    Body: { "keyword": str, "niche": str, "platforms": ["META", "YOUTUBE"] }
    """
    data = request.json
    result = ingestion_service.scrape_and_ingest(
        keyword=data["keyword"],
        niche=data["niche"],
        platforms=data.get("platforms", ["META", "YOUTUBE"])
    )
    return jsonify(result)


@ads_bp.route("/recommend", methods=["POST"])
def get_recommendations():
    """
    RAG-powered ad recommendations.
    Requires vector store to have been populated via /scrape first.

    Body: {
        "keyword": str, "niche": str, "platforms": list,
        "campaign_goal": str, "target_audience": str,
        "budget": str, "tone": str
    }
    """
    data = request.json
    result = recommendation_engine.generate_ad_recommendations(data)
    return jsonify(result)


@ads_bp.route("/intelligence", methods=["POST"])
def get_intelligence():
    """
    Run all 3 Bedrock intelligence agents in parallel.

    Body: {
        "keyword": str, "niche": str,
        "ad_draft": str,
        "metrics": { impressions, clicks, conversions, spend, ctr, cpc, roas }
    }
    """
    data = request.json
    result = intelligence_service.get_full_intelligence(data)
    return jsonify(result)


@ads_bp.route("/full-campaign", methods=["POST"])
def full_campaign_pipeline():
    """
    MASTER ENDPOINT — runs the entire pipeline in sequence:
    1. Scrape fresh ads into vector store
    2. RAG retrieval + Bedrock recommendation generation
    3. All 3 intelligence agents in parallel

    Use this for the main campaign creation flow in the UI.

    Body: {
        "keyword": str, "niche": str, "platforms": list,
        "campaign_goal": str, "target_audience": str,
        "budget": str, "tone": str,
        "ad_draft": str,
        "metrics": { ... }
    }
    """
    data = request.json

    scrape_result    = ingestion_service.scrape_and_ingest(
        keyword=data["keyword"],
        niche=data["niche"],
        platforms=data.get("platforms", ["META", "YOUTUBE"])
    )
    recommendations  = recommendation_engine.generate_ad_recommendations(data)
    intelligence     = intelligence_service.get_full_intelligence(data)

    return jsonify({
        "scrape_summary":         scrape_result,
        "ad_recommendations":     recommendations,
        "marketing_intelligence": intelligence
    })
```

---

## LAYER 5 — REGISTER BLUEPRINT IN MAIN APP

**File to update:** `app.py`

```python
from routes.ads_intelligence import ads_bp
app.register_blueprint(ads_bp)
```

---

## DEPENDENCIES

**Add to `requirements.txt`:**

```
chromadb>=0.4.0
sentence-transformers>=2.2.0
requests>=2.31.0
python-dotenv>=1.0.0
```

**Install:**
```bash
pip install chromadb sentence-transformers requests python-dotenv
```

Note: `boto3` is NOT required. All Bedrock calls use `requests` with bearer token auth.

---

## FILE STRUCTURE

```
instamedia-ai/
├── app.py                               ← Register ads_bp
├── config.py                            ← Add Bedrock API Key env vars
├── .env                                 ← NEVER commit — add to .gitignore
├── requirements.txt                     ← Add new deps
├── chroma_ads_db/                       ← Auto-created by ChromaDB (gitignore this)
├── services/
│   ├── bedrock/
│   │   ├── __init__.py
│   │   ├── bedrock_client.py            ← Reusable HTTP client (API Key auth)
│   │   └── marketing_intelligence.py   ← 3 parallel Bedrock agents
│   ├── ad_scraper/
│   │   ├── __init__.py
│   │   ├── meta_scraper.py              ← META Ad Library scraper
│   │   ├── youtube_scraper.py           ← SerpAPI YouTube scraper
│   │   └── ingestion_service.py        ← Orchestrator + ChromaDB interface
│   └── rag/
│       ├── __init__.py
│       └── ad_recommendation_engine.py ← RAG pipeline + Bedrock recommendations
└── routes/
    └── ads_intelligence.py             ← Flask API routes + blueprints
```

---

## BUILD ORDER FOR YOUR AGENT

Strict dependency order — build exactly in this sequence:

```
1.  config.py                        (env vars — everything depends on this)
2.  services/bedrock/bedrock_client.py    (Bedrock HTTP client — built first, used everywhere)
3.  services/ad_scraper/meta_scraper.py
4.  services/ad_scraper/youtube_scraper.py
5.  services/ad_scraper/ingestion_service.py  (depends on both scrapers)
6.  services/rag/ad_recommendation_engine.py  (depends on ingestion + bedrock_client)
7.  services/bedrock/marketing_intelligence.py (depends on bedrock_client)
8.  routes/ads_intelligence.py               (depends on all services)
9.  app.py                                   (register blueprint)
10. requirements.txt → pip install
11. Test: POST /api/ads/full-campaign end-to-end
```

---

## TEST PAYLOAD (use for end-to-end verification)

```json
POST /api/ads/full-campaign
{
  "keyword": "fitness supplements",
  "niche": "health & wellness",
  "platforms": ["META", "YOUTUBE"],
  "campaign_goal": "drive product page visits",
  "target_audience": "men 25-40 interested in gym and fitness",
  "budget": "$500/month",
  "tone": "energetic and motivational",
  "ad_draft": "Fuel your gains with ProMax Whey. 30g protein per scoop. Shop now.",
  "metrics": {
    "impressions": 50000,
    "clicks": 450,
    "conversions": 18,
    "spend": 320.00,
    "ctr": 0.9,
    "cpc": 0.71,
    "roas": 2.8
  }
}
```

---

## KEY ARCHITECTURAL DECISIONS

**Why `requests` instead of `boto3` for Bedrock?**
Bedrock API Key auth uses a simple bearer token passed in the HTTP `Authorization` header.
`boto3` uses AWS Signature V4 signing with IAM credentials — a completely different auth flow.
Since you have a Bedrock API Key (not IAM credentials), direct HTTP with `requests` is correct.

**Why ChromaDB over Pinecone?**
ChromaDB runs locally with zero extra infra cost and persists to disk between app restarts.
Right for a startup-phase project. Migrate to Pinecone when you need multi-user horizontal scale.

**Why RAG instead of fine-tuning the LLM?**
AD performance data changes daily. RAG keeps the knowledge base fresh by re-scraping and
re-embedding without any model retraining. Just re-call `scrape_and_ingest()` on a schedule.

**Why 3 separate BedrockClient instances in MarketingIntelligenceService?**
Each instance has its own `requests.Session`. For parallel HTTP calls via ThreadPoolExecutor,
sharing one session across threads can cause race conditions. Separate instances = thread-safe.

**Why `invoke_json()` uses temperature 0.3?**
Structured JSON output requires low creativity/randomness. Temperature 0.3 produces
consistent, parseable JSON. `invoke()` uses 0.7 for more creative text like headlines/hooks.

---

*Instamedia AI — ADs Intelligence Module v2*
*Stack: Flask + ChromaDB + SerpAPI + META Ad Library + Amazon Bedrock (API Key Auth)*
*Auth method: Bearer token via HTTP Authorization header — NO boto3 required*
