import requests
import json
import os

# --- Config ---
BASE_URL = "http://127.0.0.1:5001"
ENDPOINT = "/api/ideate"
FULL_URL = f"{BASE_URL}{ENDPOINT}"

# --- Payload ---
payload = {
    "brand_id": "default",
    "focus_area": "Launch of our new eco-friendly product line"
}

# --- Request ---
print(f"📡 Sending POST request to: {FULL_URL}")
print(f"📦 Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(FULL_URL, json=payload, timeout=30)
    
    print(f"\n⬅️ Response Status: {response.status_code}")
    
    try:
        data = response.json()
        print(f"📄 Response Body:\n{json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            if data.get("success"):
                ideas = data.get("result", {}).get("ideas", [])
                print(f"\n✅ SUCCESS! Received {len(ideas)} ideas.")
            else:
                print(f"\n❌ FAILED. Backend reported success=False.")
                print(f"Error: {data.get('error')}")
        else:
            print(f"\n❌ FAILED. HTTP Error.")
            
    except json.JSONDecodeError:
        print(f"⚠️  Response is not JSON:")
        print(response.text)

except Exception as e:
    print(f"\n❌ REQUEST FAILED: {e}")
