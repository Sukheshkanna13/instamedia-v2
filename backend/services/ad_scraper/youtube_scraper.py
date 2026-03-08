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
        if not self.api_key or self.api_key == "your_serpapi_key_here":
            print("⚠️ SERPAPI_KEY not configured. Using realistic mock data.")
            return self._mock_data(keyword, niche, limit)
            
        params = {
            "engine": "youtube",
            "search_query": f"{keyword} advertisement",
            "api_key": self.api_key,
        }

        try:
            response = requests.get(SERPAPI_BASE, params=params, timeout=15)
            response.raise_for_status()
            videos = response.json().get("video_results", [])[:limit]
            return self._normalize(videos, niche=niche)
        except Exception as e:
            print(f"⚠️ YouTube scraping failed: {e}. Falling back to mock data.")
            return self._mock_data(keyword, niche, limit)

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

    def _mock_data(self, keyword: str, niche: str, limit: int) -> List[Dict]:
        """Provides realistic mock data when API key is missing."""
        return [
            {
                "platform": "YOUTUBE",
                "ad_id": "yt_mock_1",
                "headline": f"How to master {keyword} in 2025 (NOT what you think)",
                "body": "Watch this before your competitors do. The exact playbook for explosive growth.",
                "channel_name": "Marketing Legends",
                "preview_url": "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0",
                "video_url": "https://www.youtube.com/watch?v=mock123",
                "views": 2500000,
                "efficiency_score": 2.5,
                "duration": "12:05",
                "niche": niche,
                "scraped_at": datetime.utcnow().isoformat(),
                "run_days": 0
            },
            {
                "platform": "YOUTUBE",
                "ad_id": "yt_mock_2",
                "headline": f"Why your {keyword} campaigns are failing",
                "body": "The 3 critical mistakes costing you thousands. Free training class inside.",
                "channel_name": "Ad Pros",
                "preview_url": "https://images.unsplash.com/photo-1533750516457-a7f992034fec",
                "video_url": "https://www.youtube.com/watch?v=mock456",
                "views": 850000,
                "efficiency_score": 0.85,
                "duration": "8:30",
                "niche": niche,
                "scraped_at": datetime.utcnow().isoformat(),
                "run_days": 0
            }
        ][:limit]
