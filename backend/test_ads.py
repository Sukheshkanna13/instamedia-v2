import requests
import json

URL = "http://localhost:5001/api/ads/full-campaign"

payload = {
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

print("Testing AD Intelligence full pipeline...")
try:
    response = requests.post(URL, json=payload)
    print(f"Status Code: {response.status_code}")
    
    # We expect Bedrock API to fail since we don't have a real API key yet,
    # but the structure should be intact and scrapers should use mocks.
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except requests.exceptions.ConnectionError:
    print("Failed to connect to backend on port 5001. Is it running?")
