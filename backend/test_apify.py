"""
Test Apify integration to find correct actor names
"""
import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

APIFY_API_KEY = os.getenv("APIFY_API_KEY", "")

if not APIFY_API_KEY:
    print("❌ APIFY_API_KEY not found in .env")
    exit(1)

print(f"✅ Apify API Key found: {APIFY_API_KEY[:20]}...")

# Initialize client
client = ApifyClient(APIFY_API_KEY)

# Test 1: List available actors
print("\n📋 Testing Apify connection...")
try:
    # Try a simple Instagram scraper
    print("\n🔍 Testing Instagram scraper...")
    run_input = {
        "hashtags": ["sustainability"],
        "resultsLimit": 2
    }
    
    # Try different Instagram actor names
    instagram_actors = [
        "apify/instagram-hashtag-scraper",
        "apify/instagram-scraper",
        "zuzka/instagram-hashtag-scraper"
    ]
    
    for actor_name in instagram_actors:
        try:
            print(f"   Trying: {actor_name}")
            run = client.actor(actor_name).call(run_input=run_input)
            print(f"   ✅ SUCCESS with {actor_name}")
            
            # Get results
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            print(f"   Found {len(items)} items")
            if items:
                print(f"   Sample: {list(items[0].keys())}")
            break
        except Exception as e:
            print(f"   ❌ Failed: {str(e)[:100]}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n✅ Test complete!")
