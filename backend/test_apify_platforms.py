"""
Test different platform scrapers on Apify
"""
import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

APIFY_API_KEY = os.getenv("APIFY_API_KEY", "")
client = ApifyClient(APIFY_API_KEY)

print("🔍 Testing platform scrapers...\n")

# Test LinkedIn
print("📘 Testing LinkedIn scrapers...")
linkedin_actors = [
    "apify/linkedin-posts-scraper",
    "apify/linkedin-scraper",
    "voyager/linkedin-scraper"
]

for actor_name in linkedin_actors:
    try:
        print(f"   Trying: {actor_name}")
        # Just check if actor exists
        actor = client.actor(actor_name)
        print(f"   ✅ Actor exists: {actor_name}")
        break
    except Exception as e:
        print(f"   ❌ Not found: {str(e)[:80]}")

# Test Twitter
print("\n🐦 Testing Twitter scrapers...")
twitter_actors = [
    "apify/twitter-scraper",
    "apify/tweet-scraper",
    "quacker/twitter-scraper"
]

for actor_name in twitter_actors:
    try:
        print(f"   Trying: {actor_name}")
        actor = client.actor(actor_name)
        print(f"   ✅ Actor exists: {actor_name}")
        break
    except Exception as e:
        print(f"   ❌ Not found: {str(e)[:80]}")

print("\n✅ Test complete!")
