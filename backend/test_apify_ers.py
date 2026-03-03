"""
Test Apify Ingestion Service with ERS Calculation
Phase 5, Day 4
"""
import os
from dotenv import load_dotenv
from apify_client import ApifyClient
from services.apify_ingestion import ApifyIngestionService

load_dotenv()

# Mock ChromaDB collection for testing
class MockCollection:
    def __init__(self):
        self.items = []
    
    def add(self, documents, metadatas, ids):
        for doc, meta, id in zip(documents, metadatas, ids):
            self.items.append({"doc": doc, "meta": meta, "id": id})
        print(f"✅ Added {len(documents)} items to ChromaDB")
    
    def count(self):
        return len(self.items)

# Mock embedder
def mock_embedder(text):
    return [0.1] * 384

print("🧪 Testing Apify Ingestion Service with ERS\n")

# Test ERS calculation
print("1️⃣ Testing ERS calculation...")
service = ApifyIngestionService(
    apify_client=None,
    collection=MockCollection(),
    embedder=mock_embedder
)

test_cases = [
    {"likes": 100, "comments": 10, "shares": 5, "expected": 29.0},
    {"likes": 1000, "comments": 50, "shares": 20, "expected": 241.0},
    {"likes": 0, "comments": 0, "shares": 0, "expected": 0.0},
]

for case in test_cases:
    ers = service.calculate_ers(case["likes"], case["comments"], case["shares"])
    expected = case["expected"]
    status = "✅" if abs(ers - expected) < 0.01 else "❌"
    print(f"   {status} Likes: {case['likes']}, Comments: {case['comments']}, Shares: {case['shares']}")
    print(f"      ERS: {ers:.2f} (expected: {expected:.2f})")

# Test with real Apify API (if key is available)
APIFY_API_KEY = os.getenv("APIFY_API_KEY", "")

if APIFY_API_KEY:
    print("\n2️⃣ Testing real Apify scraping...")
    print("   (This will use your Apify credits)")
    
    client = ApifyClient(APIFY_API_KEY)
    collection = MockCollection()
    
    service = ApifyIngestionService(
        apify_client=client,
        collection=collection,
        embedder=mock_embedder
    )
    
    # Test with a small scrape
    print("\n   Testing Instagram scrape (5 posts)...")
    result = service.scrape_and_score(
        target="nike",  # Public account
        platform="instagram",
        count=5
    )
    
    if result["success"]:
        print(f"   ✅ Successfully scraped {len(result['posts'])} posts")
        print(f"\n   📊 Statistics:")
        for key, value in result["stats"].items():
            print(f"      {key}: {value:.2f}" if isinstance(value, float) else f"      {key}: {value}")
        
        print(f"\n   📝 Sample post:")
        if result["posts"]:
            post = result["posts"][0]
            print(f"      ERS: {post.get('ers', 0):.2f}")
            print(f"      Likes: {post.get('likesCount', 0)}")
            print(f"      Comments: {post.get('commentsCount', 0)}")
            print(f"      Shares: {post.get('sharesCount', 0)}")
    else:
        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        print(f"      Message: {result.get('message', '')}")
else:
    print("\n2️⃣ Skipping real API test (no APIFY_API_KEY)")
    print("   Set APIFY_API_KEY in .env to test with real data")

print("\n✅ Test complete!")
