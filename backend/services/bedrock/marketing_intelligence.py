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

import time
from typing import Dict
from services.bedrock.bedrock_client import BedrockClient, BedrockInvokeError
from services.bedrock.gemini_ads_client import GeminiAdsClient


class MarketingIntelligenceService:
    def __init__(self):
        # We only need 1 client now since we run synchronously
        self.master_client = BedrockClient()
        # Gemini Native Fallback client for ADs
        self.master_gemini = GeminiAdsClient()

    def get_full_intelligence(self, request: Dict) -> Dict:
        """
        Run the 3 Market Intelligence checks synchronously via a single merged prompt.
        Dodges Google Gemini Free Tier 429 quota block.
        """
        
        # Add a tiny 2s pad to let the AD_Recommendation inference clear the Gemini queue
        time.sleep(2)
        
        keyword = request.get('keyword', '')
        niche = request.get('niche', '')
        ad_draft = request.get("ad_draft", "No draft provided yet.")
        m = request.get("metrics", {})
        
        prompt = f"""You are a Master Performance Marketing & Analytics Expert for Instamedia AI.

We need 3 distinct intelligence reports for a campaign: Market Research, Campaign Tuning, and Analytics.

1. === MARKET RESEARCH DATA ===
Keyword: {keyword}
Niche: {niche}

2. === CAMPAIGN TUNING DATA ===
Current Ad Draft:
{ad_draft}

3. === ANALYTICS DATA ===
- Impressions:   {m.get('impressions', 0):,}
- Clicks:        {m.get('clicks', 0):,}
- Conversions:   {m.get('conversions', 0):,}
- Total Spend:   ${m.get('spend', 0):,.2f}
- CTR:           {m.get('ctr', 0)}%
- CPC:           ${m.get('cpc', 0)}
- ROAS:          {m.get('roas', 0)}x

Return ONLY valid JSON (no markdown fences) covering ALL THREE reports in this exact merged structure:
{{
  "market_research": {{
    "market_size_trends": "...",
    "competitor_analysis": [
      {{ "brand": "...", "strategy": "...", "weakness": "..." }}
    ],
    "audience_insights": {{
        "demographics": "...", "psychographics": "...", "pain_points": [], "motivations": []
    }},
    "seasonal_patterns": "...",
    "content_angles": ["angle1", "angle2", "angle3"],
    "emerging_opportunities": ["opp1", "opp2"]
  }},
  
  "campaign_tuning": {{
    "strengths": ["...", "..."],
    "weaknesses": ["...", "..."],
    "rewrites": [
      {{ "original": "...", "improved": "...", "reason": "..." }}
    ],
    "ab_tests": [
      {{ "element": "...", "variant_a": "...", "variant_b": "...", "hypothesis": "..." }}
    ],
    "platform_tweaks": {{ "META": "...", "YOUTUBE": "..." }},
    "compliance_notes": ["...", "..."]
  }},

  "analytics_insights": {{
    "performance_diagnosis": {{
      "overall_grade": "A/B/C/D/F",
      "summary": "...",
      "metric_breakdown": [
        {{ "metric": "CTR", "status": "above/below/at benchmark", "note": "..." }}
      ]
    }},
    "optimization_priority": {{
      "top_priority": "...", "reason": "...", "expected_impact": "..."
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
      {{ "priority": 1, "action": "...", "timeline": "this week", "expected_result": "..." }}
    ],
    "projections": {{
      "30_day_optimized": {{ "ctr": "...", "cpc": "...", "roas": "...", "note": "..." }}
    }}
  }}
}}"""
        
        try:
            return self.master_client.invoke_json(prompt, max_tokens=3000)
        except BedrockInvokeError as e:
            print(f"⚠️ [Total Intelligence] Bedrock failed: {e}. Falling back to Gemini Free Tier (Synchronous)...")
            try:
                return self.master_gemini.invoke_json(prompt, max_tokens=3000)
            except Exception as inner_e:
                err_dict = {"error": f"Both Bedrock and Gemini failed: {str(inner_e)}"}
                return {
                    "market_research": err_dict,
                    "campaign_tuning": err_dict,
                    "analytics_insights": err_dict
                }
        except Exception as e:
            err_dict = {"error": str(e)}
            return {
                "market_research": err_dict,
                "campaign_tuning": err_dict,
                "analytics_insights": err_dict
            }
