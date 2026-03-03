"""
Test script for Media Generator Service (Phase 6, Days 10-11)
Tests prompt translation for all three formats: image, carousel, video
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

# Mock LLM caller for testing
def mock_llm_caller(prompt: str) -> str:
    """Mock LLM that returns valid JSON responses"""
    if "single image" in prompt.lower() or '"format": "image"' in prompt:
        return json.dumps({
            "format": "image",
            "image_prompt": "A modern, minimalist workspace with a laptop showing code, warm lighting, professional atmosphere, shallow depth of field",
            "style": "modern minimalist photography",
            "mood": "focused and professional"
        })
    elif "carousel" in prompt.lower():
        return json.dumps({
            "format": "carousel",
            "slide_count": 4,
            "slides": [
                {
                    "slide_number": 1,
                    "title": "The Problem",
                    "content": "Every founder faces this challenge at some point in their journey.",
                    "image_prompt": "Frustrated entrepreneur at desk, dramatic lighting, relatable moment"
                },
                {
                    "slide_number": 2,
                    "title": "The Turning Point",
                    "content": "Here's what changed everything for us.",
                    "image_prompt": "Light bulb moment, bright and inspiring, breakthrough visualization"
                },
                {
                    "slide_number": 3,
                    "title": "The Solution",
                    "content": "We implemented this simple framework that transformed our approach.",
                    "image_prompt": "Clean diagram or framework visualization, professional and clear"
                },
                {
                    "slide_number": 4,
                    "title": "Your Next Step",
                    "content": "Start applying this today and see the difference.",
                    "image_prompt": "Confident entrepreneur taking action, motivational and empowering"
                }
            ]
        })
    elif "video" in prompt.lower() or "storyboard" in prompt.lower():
        return json.dumps({
            "format": "video",
            "scene_count": 6,
            "total_duration": "25s",
            "storyboard": [
                {
                    "scene_number": 1,
                    "description": "Hook: Close-up of founder's face, looking directly at camera with intensity",
                    "duration": "3s",
                    "keyframe_prompt": "Close-up portrait, direct eye contact, dramatic lighting, intense expression"
                },
                {
                    "scene_number": 2,
                    "description": "Problem setup: Quick cuts of common startup struggles",
                    "duration": "4s",
                    "keyframe_prompt": "Montage of startup challenges, fast-paced, relatable moments"
                },
                {
                    "scene_number": 3,
                    "description": "The mistake: Reveal the critical error most founders make",
                    "duration": "5s",
                    "keyframe_prompt": "Dramatic reveal moment, realization, impactful visual"
                },
                {
                    "scene_number": 4,
                    "description": "The solution: Show the better approach with examples",
                    "duration": "5s",
                    "keyframe_prompt": "Solution visualization, clear and actionable, positive transformation"
                },
                {
                    "scene_number": 5,
                    "description": "Results: Quick showcase of positive outcomes",
                    "duration": "4s",
                    "keyframe_prompt": "Success indicators, growth metrics, celebration moment"
                },
                {
                    "scene_number": 6,
                    "description": "CTA: Direct call-to-action with founder speaking",
                    "duration": "4s",
                    "keyframe_prompt": "Founder speaking to camera, confident and inviting, clear CTA"
                }
            ]
        })
    else:
        return '{"error": "Unknown format"}'


def test_media_generator():
    """Test the MediaGeneratorService with all three formats"""
    from services.media_generator import create_media_generator
    
    print("=" * 80)
    print("MEDIA GENERATOR SERVICE TEST")
    print("=" * 80)
    print()
    
    # Create service with mock LLM
    media_gen = create_media_generator(mock_llm_caller)
    
    # Test data
    caption = "The mistake that almost ended our startup. Here's what we learned."
    hashtags = ["#startup", "#entrepreneurship", "#lessons", "#founder"]
    
    print(f"📝 Test Caption: {caption}")
    print(f"🏷️  Hashtags: {', '.join(hashtags)}")
    print()
    
    # Test 1: Single Image
    print("─" * 80)
    print("TEST 1: SINGLE IMAGE GENERATION")
    print("─" * 80)
    try:
        result = media_gen.generate_image_prompt(caption, hashtags)
        print("✅ Success!")
        print(f"Format: {result.get('format')}")
        print(f"Style: {result.get('style')}")
        print(f"Mood: {result.get('mood')}")
        print(f"Prompt: {result.get('image_prompt')}")
        print()
    except Exception as e:
        print(f"❌ Failed: {e}")
        print()
    
    # Test 2: Carousel
    print("─" * 80)
    print("TEST 2: CAROUSEL GENERATION (3-5 slides)")
    print("─" * 80)
    try:
        result = media_gen.generate_carousel_slides(caption, hashtags)
        print("✅ Success!")
        print(f"Format: {result.get('format')}")
        print(f"Slide Count: {result.get('slide_count')}")
        print()
        for slide in result.get('slides', []):
            print(f"  Slide {slide['slide_number']}: {slide['title']}")
            print(f"    Content: {slide['content']}")
            print(f"    Image: {slide['image_prompt'][:60]}...")
            print()
    except Exception as e:
        print(f"❌ Failed: {e}")
        print()
    
    # Test 3: Video Storyboard
    print("─" * 80)
    print("TEST 3: VIDEO STORYBOARD GENERATION (5-8 scenes)")
    print("─" * 80)
    try:
        result = media_gen.generate_video_storyboard(caption, hashtags)
        print("✅ Success!")
        print(f"Format: {result.get('format')}")
        print(f"Scene Count: {result.get('scene_count')}")
        print(f"Total Duration: {result.get('total_duration')}")
        print()
        for scene in result.get('storyboard', []):
            print(f"  Scene {scene['scene_number']} ({scene['duration']})")
            print(f"    {scene['description']}")
            print(f"    Keyframe: {scene['keyframe_prompt'][:60]}...")
            print()
    except Exception as e:
        print(f"❌ Failed: {e}")
        print()
    
    # Test 4: Main entry point
    print("─" * 80)
    print("TEST 4: MAIN ENTRY POINT (translate_to_creative_prompt)")
    print("─" * 80)
    for format_type in ["image", "carousel", "video"]:
        try:
            result = media_gen.translate_to_creative_prompt(
                caption=caption,
                hashtags=hashtags,
                format_type=format_type
            )
            print(f"✅ {format_type.upper()}: Success!")
            print(f"   Format: {result.get('format')}")
            if format_type == "image":
                print(f"   Prompt: {result.get('image_prompt', '')[:60]}...")
            elif format_type == "carousel":
                print(f"   Slides: {result.get('slide_count')}")
            elif format_type == "video":
                print(f"   Scenes: {result.get('scene_count')}, Duration: {result.get('total_duration')}")
            print()
        except Exception as e:
            print(f"❌ {format_type.upper()}: Failed - {e}")
            print()
    
    print("=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)


def test_with_real_llm():
    """Test with real LLM (Gemini or Groq)"""
    import requests
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
    
    if not GEMINI_API_KEY and not GROQ_API_KEY:
        print("⚠️  No LLM API key found. Using mock mode.")
        return test_media_generator()
    
    def call_gemini(prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192}
        }
        try:
            res = requests.post(url, json=payload, timeout=30)
            res.raise_for_status()
            return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"[Gemini Error: {e}]"
    
    def call_groq(prompt: str) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Groq Error: {e}]"
    
    llm_caller = call_groq if LLM_PROVIDER == "groq" else call_gemini
    
    print("=" * 80)
    print(f"TESTING WITH REAL LLM: {LLM_PROVIDER.upper()}")
    print("=" * 80)
    print()
    
    from services.media_generator import create_media_generator
    
    media_gen = create_media_generator(llm_caller)
    
    caption = "The mistake that almost ended our startup. Here's what we learned."
    hashtags = ["#startup", "#entrepreneurship", "#lessons"]
    
    print(f"📝 Caption: {caption}")
    print(f"🏷️  Hashtags: {', '.join(hashtags)}")
    print()
    
    # Test image generation
    print("─" * 80)
    print("TESTING: IMAGE PROMPT GENERATION")
    print("─" * 80)
    try:
        result = media_gen.generate_image_prompt(caption, hashtags)
        print("✅ Success!")
        print(json.dumps(result, indent=2))
        print()
    except Exception as e:
        print(f"❌ Failed: {e}")
        print()
    
    print("=" * 80)
    print("REAL LLM TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--real":
        test_with_real_llm()
    else:
        test_media_generator()
