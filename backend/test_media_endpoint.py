"""
Test the /api/studio/generate-media endpoint
Phase 6, Days 10-11
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_endpoint():
    """Test the media generation endpoint"""
    
    print("=" * 80)
    print("TESTING /api/studio/generate-media ENDPOINT")
    print("=" * 80)
    print()
    
    # Test data
    test_cases = [
        {
            "name": "Single Image",
            "data": {
                "caption": "The mistake that almost ended our startup. Here's what we learned.",
                "hashtags": ["#startup", "#entrepreneurship", "#lessons"],
                "format": "image",
                "brand_id": "default"
            }
        },
        {
            "name": "Carousel (3-5 slides)",
            "data": {
                "caption": "5 lessons from failing 10 times before finding product-market fit.",
                "hashtags": ["#founder", "#startup", "#lessons", "#pmf"],
                "format": "carousel",
                "brand_id": "default"
            }
        },
        {
            "name": "Video Storyboard (5-8 scenes)",
            "data": {
                "caption": "Day in the life of a founder: From coffee to code to customer calls.",
                "hashtags": ["#founder", "#startup", "#dayinthelife"],
                "format": "video",
                "brand_id": "default"
            }
        }
    ]
    
    for test_case in test_cases:
        print("─" * 80)
        print(f"TEST: {test_case['name']}")
        print("─" * 80)
        print(f"Caption: {test_case['data']['caption']}")
        print(f"Format: {test_case['data']['format']}")
        print()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/studio/generate-media",
                json=test_case['data'],
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"Generation Time: {result['result'].get('generation_time_seconds')}s")
                print()
                print("Result:")
                print(json.dumps(result['result'], indent=2))
                print()
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(response.text)
                print()
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Is the Flask server running?")
            print("   Run: python app.py")
            print()
            return
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
    
    print("=" * 80)
    print("ALL ENDPOINT TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_endpoint()
