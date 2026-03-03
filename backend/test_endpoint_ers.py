"""
Test the /api/esg/scrape endpoint
"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("🧪 Testing /api/esg/scrape endpoint\n")

# Test data
test_request = {
    "target": "nike",
    "platform": "instagram",
    "count": 5
}

print(f"📤 Request:")
print(json.dumps(test_request, indent=2))

try:
    response = requests.post(
        f"{BASE_URL}/api/esg/scrape",
        json=test_request,
        timeout=60
    )
    
    print(f"\n📥 Response Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print(f"\n✅ Success!")
            print(f"   Posts scraped: {len(data.get('posts', []))}")
            print(f"   Platform: {data.get('platform')}")
            print(f"   Target: {data.get('target')}")
            
            if data.get("stats"):
                print(f"\n   📊 Statistics:")
                for key, value in data["stats"].items():
                    if isinstance(value, float):
                        print(f"      {key}: {value:.2f}")
                    else:
                        print(f"      {key}: {value}")
        else:
            print(f"\n❌ Failed: {data.get('error')}")
    else:
        print(f"\n❌ HTTP Error: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ Connection Error: Is the backend running?")
    print("   Start it with: python backend/app.py")
except Exception as e:
    print(f"\n❌ Error: {e}")
