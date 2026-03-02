"""
Test real scraping with simple keywords
"""
import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

APIFY_API_KEY = os.getenv("APIFY_API_KEY", "")
client = ApifyClient(APIFY_API_KEY)

print("🔍 Testing real scraping...\n")

# Test 1: Instagram with simple hashtag
print("1. Testing Instagram with #sustainability...")
try:
    run_input = {
        "hashtags": ["sustainability"],
        "resultsLimit": 3
    }
    
    run = client.actor("apify/instagram-hashtag-scraper").call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    print(f"✅ Found {len(items)} Instagram posts")
    if items:
        print(f"   Sample caption: {items[0].get('caption', '')[:100]}")
        print(f"   Likes: {items[0].get('likesCount', 0)}")
except Exception as e:
    print(f"❌ Instagram error: {e}")

# Test 2: Try a different LinkedIn approach
print("\n2. Testing LinkedIn scraper...")
try:
    # Try the simpler apify/linkedin-scraper
    run_input = {
        "startUrls": [
            {"url": "https://www.linkedin.com/search/results/content/?keywords=sustainability"}
        ],
        "maxResults": 3
    }
    
    print(f"   Trying: apify/linkedin-scraper")
    run = client.actor("apify/linkedin-scraper").call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    print(f"✅ Found {len(items)} LinkedIn items")
    if items:
        print(f"   Sample keys: {list(items[0].keys())[:10]}")
except Exception as e:
    print(f"❌ LinkedIn error: {e}")

# Test 3: Twitter
print("\n3. Testing Twitter scraper...")
try:
    run_input = {
        "searchTerms": ["sustainability"],
        "maxItems": 3
    }
    
    run = client.actor("apify/twitter-scraper").call(run_input=run_input)
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    
    print(f"✅ Found {len(items)} Twitter posts")
    if items:
        print(f"   Sample text: {items[0].get('text', '')[:100]}")
except Exception as e:
    print(f"❌ Twitter error: {e}")

print("\n✅ Test complete!")
