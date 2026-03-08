import requests
import json

payload = {
    "keyword": "luxury electric bikes",
    "niche": "premium transportation",
    "platforms": ["META", "YOUTUBE"],
    "campaign_goal": "drive test ride bookings",
    "target_audience": "high income professionals aged 35-55",
    "budget": "$5000/month",
    "tone": "elegant and thrilling",
    "ad_draft": "Experience the thrill of the city with zero sweat."
}

res = requests.post("http://localhost:5001/api/ads/full-campaign", json=payload)
data = res.json()

print("Status Code:", res.status_code)
print("Brief Used:", data.get("ad_recommendations", {}).get("brief_used"))
print("Headlines:")
try:
    print(json.dumps(data["ad_recommendations"]["recommendations"]["headlines"], indent=2))
except Exception as e:
    print(data.get("ad_recommendations", {}).get("recommendations", {}))

print("\n--- Marketing Intelligence ---")
try:
    print(json.dumps(data.get("marketing_intelligence", {}), indent=2))
except:
    print(data.get("marketing_intelligence", "None"))
