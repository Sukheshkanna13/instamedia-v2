from flask import Blueprint, request, jsonify
from services.ad_scraper.ingestion_service import ADIngestionService
from services.rag.ad_recommendation_engine import ADRecommendationEngine
from services.bedrock.marketing_intelligence import MarketingIntelligenceService

ads_bp = Blueprint("ads", __name__, url_prefix="/api/ads")

# Instantiate services once at module level (not per-request)
ingestion_service    = ADIngestionService()
recommendation_engine = ADRecommendationEngine(ingestion_service=ingestion_service)
intelligence_service  = MarketingIntelligenceService()


@ads_bp.route("/scrape", methods=["POST"])
def scrape_ads():
    """
    Trigger on-demand ad scraping for a keyword + niche.
    Populates ChromaDB vector store. Call before /recommend.

    Body: { "keyword": str, "niche": str, "platforms": ["META", "YOUTUBE"] }
    """
    data = request.json or {}
    keyword = data.get("keyword")
    niche = data.get("niche")
    platforms = data.get("platforms", ["META", "YOUTUBE"])
    
    if not keyword or not niche:
        return jsonify({"error": "Keyword and niche are required"}), 400
        
    result = ingestion_service.scrape_and_ingest(
        keyword=keyword,
        niche=niche,
        platforms=platforms
    )
    return jsonify(result)


@ads_bp.route("/recommend", methods=["POST"])
def get_recommendations():
    """
    RAG-powered ad recommendations.
    Requires vector store to have been populated via /scrape first.
    """
    data = request.json or {}
    if not data.get("keyword") or not data.get("niche"):
        return jsonify({"error": "Keyword and niche are required"}), 400
        
    result = recommendation_engine.generate_ad_recommendations(data)
    return jsonify(result)


@ads_bp.route("/intelligence", methods=["POST"])
def get_intelligence():
    """
    Run all 3 Bedrock intelligence agents in parallel.
    """
    data = request.json or {}
    if not data.get("keyword") or not data.get("niche"):
        return jsonify({"error": "Keyword and niche are required"}), 400
        
    result = intelligence_service.get_full_intelligence(data)
    return jsonify(result)


@ads_bp.route("/full-campaign", methods=["POST"])
def full_campaign_pipeline():
    """
    MASTER ENDPOINT (FREE TIER OPTIMIZED)
    Runs scraping, then uses a single merged RAG call via the Recommendation Engine
    to generate the core strategy without blowing up Free Tier LLM Limits.
    """
    data = request.json or {}
    if not data.get("keyword") or not data.get("niche"):
        return jsonify({"error": "Keyword and niche are required"}), 400

    scrape_result = ingestion_service.scrape_and_ingest(
        keyword=data["keyword"],
        niche=data["niche"],
        platforms=data.get("platforms", ["META", "YOUTUBE"])
    )
    
    # We only call ONE generation pipeline to preserve the 15 Req/Min & 20 Req/Day limits.
    # The frontend will display this data gracefully.
    recommendations = recommendation_engine.generate_ad_recommendations(data)

    return jsonify({
        "scrape_summary":         scrape_result,
        "ad_recommendations":     recommendations,
        "marketing_intelligence": {
            "analytics_insights": {"error": "Skipped to preserve Free Tier API quotas."},
            "campaign_tuning": {"error": "Skipped to preserve Free Tier API quotas."},
            "market_research": {"error": "Skipped to preserve Free Tier API quotas."}
        }
    })
