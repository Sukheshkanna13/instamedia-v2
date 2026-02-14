import requests
import json
import os

BASE_URL = "http://127.0.0.1:5001"
ENDPOINT = "/api/studio/generate"
FULL_URL = f"{BASE_URL}{ENDPOINT}"

payload = {
    "brand_id": "default",
    "platform": "instagram",
    "topic": "Sustainable Living",
    "style": "Expert, Education"
}

print(f"📡 Sending POST request to: {FULL_URL}")

try:
    response = requests.post(FULL_URL, json=payload, timeout=60)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!")
        if data.get("success"):
            print("Generated Content:")
            print(json.dumps(data.get("result"), indent=2))
        else:
            print(f"❌ Backend Error: {data.get('error')}")
    else:
        print(f"❌ FAILED: {response.text}")

except Exception as e:
    print(f"❌ Error: {e}")
