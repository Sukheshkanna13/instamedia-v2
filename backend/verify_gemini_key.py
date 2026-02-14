import os
import requests
from dotenv import load_dotenv

# Force reload of .env
load_dotenv(override=True)

KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"
print(f"🔑 Testing API Key: {KEY[:5]}...{KEY[-5:]}")
print(f"🤖 Testing Model: {MODEL}...")

payload = {
    "contents": [{"parts": [{"text": "Hello, explain AI in 5 words."}]}]
}

try:
    response = requests.post(URL, json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! Key is valid.")
        print(response.json())
    else:
        print("❌ FAILED.")
        print(response.text)

except Exception as e:
    print(f"❌ Error: {e}")
