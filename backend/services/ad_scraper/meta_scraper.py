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
        if not self.access_token or self.access_token == "your_meta_ad_library_token_here":
            print("⚠️ META_ACCESS_TOKEN not configured. Using realistic mock data.")
            return self._mock_data(keyword, niche, limit)
            
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

        try:
            response = requests.get(META_AD_LIBRARY_BASE, params=params, timeout=15)
            response.raise_for_status()
            raw_ads = response.json().get("data", [])
            return self._normalize(raw_ads, niche=niche)
        except Exception as e:
            print(f"⚠️ META scraping failed: {e}. Falling back to mock data.")
            return self._mock_data(keyword, niche, limit)

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

    def _mock_data(self, keyword: str, niche: str, limit: int) -> List[Dict]:
        """Provides realistic mock data when API key is missing."""
        return [
            {
                "platform": "META",
                "ad_id": "meta_mock_1",
                "headline": f"Unlock 10x ROI with {keyword}",
                "body": "Stop wasting ad spend. Our proven framework drives consistent results. Click to learn how we scaled 50+ brands.",
                "page_name": "Growth Masters",
                "preview_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
                "impressions_lower": 150000,
                "spend_lower": 500,
                "efficiency_score": 300.0,
                "niche": niche,
                "scraped_at": datetime.utcnow().isoformat(),
                "run_days": 45
            },
            {
                "platform": "META",
                "ad_id": "meta_mock_2",
                "headline": f"The Secretariat of {keyword}",
                "body": "Simple, elegant, and highly effective. See why thousands are switching their strategy today.",
                "page_name": "Elite Strat",
                "preview_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f",
                "impressions_lower": 85000,
                "spend_lower": 400,
                "efficiency_score": 212.5,
                "niche": niche,
                "scraped_at": datetime.utcnow().isoformat(),
                "run_days": 21
            }
        ][:limit]
