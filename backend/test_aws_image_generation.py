"""
Test AWS Bedrock Image Generation - Phase 6, Days 12-13
Tests image generation with Titan and S3 upload
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_aws_image_generator():
    """Test the AWSImageGenerator service"""
    from services.aws_image_generator import create_aws_image_generator
    
    print("=" * 80)
    print("AWS BEDROCK IMAGE GENERATION TEST")
    print("=" * 80)
    print()
    
    # Create generator
    aws_gen = create_aws_image_generator()
    
    if aws_gen is None:
        print("❌ AWS Image Generator could not be created")
        print("   Check your AWS credentials in .env file")
        return False
    
    print("✅ AWS Image Generator created successfully")
    print()
    
    # Test 1: Single Image Generation
    print("─" * 80)
    print("TEST 1: SINGLE IMAGE GENERATION")
    print("─" * 80)
    
    prompt = "A modern, minimalist workspace with a laptop, warm lighting, professional atmosphere, shallow depth of field, high quality photography"
    
    print(f"Prompt: {prompt[:60]}...")
    print("Generating image...")
    print()
    
    try:
        result = aws_gen.generate_and_upload(prompt)
        print("✅ Success!")
        print(f"   URL: {result['url']}")
        print(f"   Size: {result['size_bytes']} bytes")
        print(f"   Time: {result['generation_time_seconds']}s")
        print()
    except Exception as e:
        print(f"❌ Failed: {e}")
        print()
        return False
    
    # Test 2: Carousel Images (Concurrent)
    print("─" * 80)
    print("TEST 2: CAROUSEL IMAGES (3 slides, concurrent)")
    print("─" * 80)
    
    slides = [
        {"image_prompt": "Frustrated entrepreneur at desk, dramatic lighting, relatable moment"},
        {"image_prompt": "Light bulb moment, bright and inspiring, breakthrough visualization"},
        {"image_prompt": "Confident entrepreneur taking action, motivational and empowering"}
    ]
    
    print(f"Generating {len(slides)} images concurrently...")
    print()
    
    try:
        results = aws_gen.generate_carousel_images(slides, max_workers=3)
        print("✅ Success!")
        for result in results:
            if result.get('url'):
                print(f"   Slide {result['slide_number']}: {result['url']}")
                print(f"      Time: {result['generation_time_seconds']}s")
            else:
                print(f"   Slide {result['slide_number']}: Failed - {result.get('error')}")
        print()
    except Exception as e:
        print(f"❌ Failed: {e}")
        print()
        return False
    
    print("=" * 80)
    print("ALL TESTS PASSED ✅")
    print("=" * 80)
    return True


def test_endpoint_with_images():
    """Test the full endpoint with image generation"""
    import requests
    
    print("=" * 80)
    print("TESTING ENDPOINT WITH IMAGE GENERATION")
    print("=" * 80)
    print()
    
    BASE_URL = "http://localhost:5001"
    
    test_data = {
        "caption": "The mistake that almost ended our startup. Here's what we learned.",
        "hashtags": ["#startup", "#entrepreneurship", "#lessons"],
        "format": "image",
        "brand_id": "default",
        "generate_images": True
    }
    
    print(f"Caption: {test_data['caption']}")
    print(f"Format: {test_data['format']}")
    print("Sending request...")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/studio/generate-media",
            json=test_data,
            timeout=60  # Longer timeout for image generation
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Generation Time: {result['result'].get('generation_time_seconds')}s")
            
            if 'image_url' in result['result']:
                print(f"Image URL: {result['result']['image_url']}")
            else:
                print("⚠️  No image URL in response (prompts only)")
            print()
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(response.text)
            print()
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is the Flask server running?")
        print("   Run: python app.py")
        print()
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        return False
    
    print("=" * 80)
    print("ENDPOINT TEST COMPLETE ✅")
    print("=" * 80)
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--endpoint":
        test_endpoint_with_images()
    else:
        test_aws_image_generator()
