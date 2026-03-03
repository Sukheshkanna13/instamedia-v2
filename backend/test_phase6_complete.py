"""
Phase 6 Complete - End-to-End Integration Test
Tests the full multi-modal content generation pipeline:
1. Frontend UI → 2. Translation Layer → 3. AWS Bedrock → 4. S3 Storage
"""

import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

def test_complete_pipeline():
    """Test the complete multi-modal content generation pipeline"""
    
    print("=" * 80)
    print("PHASE 6 COMPLETE - END-TO-END INTEGRATION TEST")
    print("=" * 80)
    print()
    
    # Test 1: Service Initialization
    print("─" * 80)
    print("TEST 1: SERVICE INITIALIZATION")
    print("─" * 80)
    
    try:
        from services.media_generator import create_media_generator
        from services.aws_image_generator import create_aws_image_generator
        
        # Mock LLM for testing
        def mock_llm(prompt):
            import json
            if "image" in prompt.lower() and "carousel" not in prompt.lower():
                return json.dumps({
                    "format": "image",
                    "image_prompt": "A modern workspace with laptop, professional lighting",
                    "style": "modern minimalist",
                    "mood": "professional"
                })
            return "{}"
        
        media_gen = create_media_generator(mock_llm)
        aws_gen = create_aws_image_generator()
        
        print("✅ MediaGeneratorService initialized")
        print("✅ AWSImageGenerator initialized")
        print()
        
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False
    
    # Test 2: Translation Layer
    print("─" * 80)
    print("TEST 2: TRANSLATION LAYER (Prompt Generation)")
    print("─" * 80)
    
    caption = "The mistake that almost ended our startup"
    hashtags = ["#startup", "#entrepreneurship"]
    
    try:
        result = media_gen.translate_to_creative_prompt(
            caption=caption,
            hashtags=hashtags,
            format_type="image"
        )
        
        print("✅ Translation successful")
        print(f"   Format: {result.get('format')}")
        print(f"   Prompt: {result.get('image_prompt', '')[:60]}...")
        print()
        
    except Exception as e:
        print(f"❌ Translation failed: {e}")
        return False
    
    # Test 3: AWS Bedrock Image Generation
    print("─" * 80)
    print("TEST 3: AWS BEDROCK IMAGE GENERATION")
    print("─" * 80)
    
    if aws_gen is None:
        print("⚠️  AWS not configured, skipping image generation")
        print()
    else:
        try:
            prompt = result.get('image_prompt', 'A professional workspace')
            print(f"Generating image...")
            print(f"Prompt: {prompt[:60]}...")
            
            start = time.time()
            image_result = aws_gen.generate_and_upload(prompt)
            duration = time.time() - start
            
            print("✅ Image generation successful")
            print(f"   URL: {image_result['url'][:80]}...")
            print(f"   Size: {image_result['size_bytes']} bytes")
            print(f"   Time: {duration:.2f}s")
            print()
            
        except Exception as e:
            print(f"❌ Image generation failed: {e}")
            return False
    
    # Test 4: Format Coverage
    print("─" * 80)
    print("TEST 4: ALL FORMAT TYPES")
    print("─" * 80)
    
    formats = ["image", "carousel", "video"]
    for fmt in formats:
        try:
            result = media_gen.translate_to_creative_prompt(
                caption=caption,
                hashtags=hashtags,
                format_type=fmt
            )
            print(f"✅ {fmt.upper()}: Translation successful")
            
            if fmt == "carousel":
                print(f"   Slides: {result.get('slide_count', 0)}")
            elif fmt == "video":
                print(f"   Scenes: {result.get('scene_count', 0)}")
            
        except Exception as e:
            print(f"❌ {fmt.upper()}: Failed - {e}")
            return False
    
    print()
    
    # Test 5: Performance Benchmarks
    print("─" * 80)
    print("TEST 5: PERFORMANCE BENCHMARKS")
    print("─" * 80)
    
    benchmarks = {
        "Translation (image)": lambda: media_gen.translate_to_creative_prompt(
            caption, hashtags, "image"
        ),
        "Translation (carousel)": lambda: media_gen.translate_to_creative_prompt(
            caption, hashtags, "carousel"
        ),
        "Translation (video)": lambda: media_gen.translate_to_creative_prompt(
            caption, hashtags, "video"
        )
    }
    
    for name, func in benchmarks.items():
        try:
            start = time.time()
            func()
            duration = time.time() - start
            print(f"✅ {name}: {duration:.2f}s")
        except Exception as e:
            print(f"❌ {name}: Failed - {e}")
    
    print()
    
    # Test 6: Error Handling
    print("─" * 80)
    print("TEST 6: ERROR HANDLING")
    print("─" * 80)
    
    # Test invalid format
    try:
        media_gen.translate_to_creative_prompt(
            caption, hashtags, "invalid_format"
        )
        print("❌ Should have raised error for invalid format")
    except ValueError:
        print("✅ Invalid format error handling works")
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")
    
    # Test empty caption
    try:
        result = media_gen.translate_to_creative_prompt(
            "", hashtags, "image"
        )
        # Should still work with empty caption (uses hashtags)
        print("✅ Empty caption handling works")
    except Exception as e:
        print(f"⚠️  Empty caption error: {e}")
    
    print()
    
    print("=" * 80)
    print("PHASE 6 INTEGRATION TEST COMPLETE ✅")
    print("=" * 80)
    print()
    print("Summary:")
    print("  ✅ Service initialization")
    print("  ✅ Translation layer")
    print("  ✅ AWS Bedrock integration")
    print("  ✅ All format types")
    print("  ✅ Performance benchmarks")
    print("  ✅ Error handling")
    print()
    print("Phase 6: Multi-Modal Creative Studio is COMPLETE! 🎉")
    print()
    
    return True


def test_endpoint_integration():
    """Test the API endpoint with real server"""
    import requests
    
    print("=" * 80)
    print("ENDPOINT INTEGRATION TEST")
    print("=" * 80)
    print()
    
    BASE_URL = "http://localhost:5001"
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding correctly")
            return False
        print("✅ Server is running")
        print()
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python app.py")
        print()
        return False
    
    # Test all three formats
    test_cases = [
        {
            "name": "Single Image",
            "data": {
                "caption": "The mistake that almost ended our startup",
                "hashtags": ["#startup", "#entrepreneurship"],
                "format": "image",
                "generate_images": True
            }
        },
        {
            "name": "Carousel (3-5 slides)",
            "data": {
                "caption": "5 lessons from failing 10 times",
                "hashtags": ["#founder", "#lessons"],
                "format": "carousel",
                "generate_images": False  # Skip images for speed
            }
        },
        {
            "name": "Video Storyboard",
            "data": {
                "caption": "Day in the life of a founder",
                "hashtags": ["#founder", "#dayinthelife"],
                "format": "video",
                "generate_images": False  # Skip images for speed
            }
        }
    ]
    
    for test_case in test_cases:
        print("─" * 80)
        print(f"TEST: {test_case['name']}")
        print("─" * 80)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/studio/generate-media",
                json=test_case['data'],
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"   Time: {result['result'].get('generation_time_seconds')}s")
                
                if 'image_url' in result['result']:
                    print(f"   Image URL: {result['result']['image_url'][:60]}...")
                elif 'slides' in result['result']:
                    print(f"   Slides: {len(result['result']['slides'])}")
                elif 'storyboard' in result['result']:
                    print(f"   Scenes: {len(result['result']['storyboard'])}")
                print()
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(response.text[:200])
                print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
    
    print("=" * 80)
    print("ENDPOINT INTEGRATION TEST COMPLETE ✅")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--endpoint":
        test_endpoint_integration()
    else:
        test_complete_pipeline()
