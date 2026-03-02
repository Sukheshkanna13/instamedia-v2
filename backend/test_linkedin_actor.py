"""
Test LinkedIn actor to find the correct one
"""
import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

APIFY_API_KEY = os.getenv("APIFY_API_KEY", "")
client = ApifyClient(APIFY_API_KEY)

print("🔍 Testing LinkedIn actors...\n")

# Try different LinkedIn actor names
linkedin_actors = [
    "apify/linkedin-posts-scraper",
    "apify/linkedin-scraper",
    "voyager/linkedin-scraper",
    "curious_coder/linkedin-profile-scraper",
    "bebity/linkedin-posts-scraper"
]

for actor_name in linkedin_actors:
    try:
        print(f"Testing: {actor_name}")
        actor_info = client.actor(actor_name).get()
        print(f"✅ Found: {actor_name}")
        print(f"   Title: {actor_info.get('title', 'N/A')}")
        print(f"   Description: {actor_info.get('description', 'N/A')[:100]}")
        print()
    except Exception as e:
        print(f"❌ Not found: {str(e)[:80]}\n")

# List all available actors
print("\n📋 Searching Apify store for LinkedIn scrapers...")
try:
    # Search for LinkedIn scrapers
    search_results = client.actors().list(search="linkedin")
    print(f"Found {len(search_results.items)} LinkedIn-related actors:")
    for actor in search_results.items[:10]:
        print(f"  - {actor['username']}/{actor['name']}")
        print(f"    Title: {actor.get('title', 'N/A')}")
        print()
except Exception as e:
    print(f"Search failed: {e}")
