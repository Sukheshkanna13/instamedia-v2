import os
import requests
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GEMINI_API_KEY")
if not key:
    print("No GEMINI_API_KEY found in .env")
    exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
payload = {
    "contents": [{"parts": [{"text": "Generate 1 cool idea for a luxury electric bike brand."}]}],
    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024}
}

print(f"Testing Gemini API with key ending in ...{key[-4:] if key else 'None'}")
try:
    res = requests.post(url, json=payload, timeout=30)
    print("Status Code:", res.status_code)
    try:
        data = res.json()
        if res.status_code != 200:
            print("ERROR JSON:", data)
        else:
            print("SUCCESS! Output:")
            print(data["candidates"][0]["content"]["parts"][0]["text"])
    except Exception as e:
        print("Failed to parse JSON response:", e)
        print("Raw text:", res.text)
except Exception as e:
    print("Request crashed:", e)
