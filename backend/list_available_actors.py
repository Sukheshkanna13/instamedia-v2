"""
List available actors in Apify account
"""
import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

APIFY_API_KEY = os.getenv("APIFY_API_KEY", "")
client = ApifyClient(APIFY_API_KEY)

print("📋 Listing available actors in your Apify account...\n")

try:
    # Get user info
    user = client.user().get()
    print(f"User: {user.get('username', 'N/A')}")
    print(f"Email: {user.get('email', 'N/A')}\n")
    
    # List actors
    actors = client.actors().list()
    print(f"Total actors available: {actors.total}\n")
    
    # Show first 20
    print("Available actors:")
    for i, actor in enumerate(actors.items[:20], 1):
        print(f"{i}. {actor['id']}")
        print(f"   Name: {actor.get('name', 'N/A')}")
        print(f"   Title: {actor.get('title', 'N/A')}")
        print()
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTrying alternative approach...")
    
    # Try to access specific known actors
    known_actors = [
        "apify/instagram-hashtag-scraper",
        "apify/web-scraper",
        "apify/google-search-scraper"
    ]
    
    print("\nTesting known public actors:")
    for actor_id in known_actors:
        try:
            actor = client.actor(actor_id).get()
            if actor:
                print(f"✅ {actor_id} - accessible")
        except:
            print(f"❌ {actor_id} - not accessible")
