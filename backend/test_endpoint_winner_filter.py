"""
Test the /api/esg/scrape endpoint with winner filter
"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("🧪 Testing /api/esg/scrape with Winner Filter\n")

# Test 1: Without filter (baseline)
print("1️⃣ Test without filter (all posts)...")
test_request = {
    "target": "nike",
    "platform": "instagram",
    "count": 10,
    "filter_winners": False
}

try:
    response = requests.post(
        f"{BASE_URL}/api/esg/scrape",
        json=test_request,
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success: {len(data.get('posts', []))} posts returned")
        print(f"   Message: {data.get('message')}")
    else:
        print(f"   ❌ Error: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("   ⚠️  Backend not running - skipping endpoint test")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: With filter (top 20%)
print("\n2️⃣ Test with filter (top 20%)...")
test_request = {
    "target": "nike",
    "platform": "instagram",
    "count": 10,
    "filter_winners": True,
    "winner_percentile": 0.2
}

try:
    response = requests.post(
        f"{BASE_URL}/api/esg/scrape",
        json=test_request,
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success!")
        print(f"   All posts: {data.get('all_posts_count', 0)}")
        print(f"   Winners: {data.get('winner_count', 0)}")
        print(f"   Cutoff ERS: {data.get('cutoff_ers', 0):.2f}")
        print(f"   Message: {data.get('message')}")
        
        if data.get('stats'):
            stats = data['stats']
            print(f"\n   📊 Statistics:")
            print(f"      Winner avg ERS: {stats.get('winner_avg_ers', 0):.2f}")
            print(f"      Overall avg ERS: {stats.get('overall_avg_ers', 0):.2f}")
            print(f"      Improvement: {stats.get('improvement_ratio', 1):.2f}x")
    else:
        print(f"   ❌ Error: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("   ⚠️  Backend not running - skipping endpoint test")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: With filter (top 50%)
print("\n3️⃣ Test with filter (top 50%)...")
test_request = {
    "target": "nike",
    "platform": "instagram",
    "count": 10,
    "filter_winners": True,
    "winner_percentile": 0.5
}

try:
    response = requests.post(
        f"{BASE_URL}/api/esg/scrape",
        json=test_request,
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success!")
        print(f"   All posts: {data.get('all_posts_count', 0)}")
        print(f"   Winners: {data.get('winner_count', 0)}")
        print(f"   Message: {data.get('message')}")
    else:
        print(f"   ❌ Error: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("   ⚠️  Backend not running - skipping endpoint test")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n✅ Test complete!")
print("\nNote: Start backend with 'python backend/app.py' to run endpoint tests")
