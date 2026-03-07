import json
from services.media_generator import create_media_generator

# 1. Create a "Mock" LLM Caller for testing
def mock_llm_caller(prompt: str) -> str:
    print(f"\n[MOCK LLM] Received prompt of length: {len(prompt)}")
    
    # Return a fake JSON response based on the format requested
    if "carousel" in prompt.lower():
        return """
        ```json
        {
            "format": "carousel",
            "slide_count": 3,
            "slides": [
                {
                    "slide_number": 1,
                    "title": "Stop Wasting Time",
                    "content": "Are you spending hours on manual AWS deployments?",
                    "image_prompt": "A frustrated developer looking at a complex server rack, dramatic blue lighting, cinematic."
                }
            ]
        }
        ```
        """
    return """{"format": "image", "image_prompt": "A sleek modern laptop on a wooden desk, high quality.", "style": "minimalist", "mood": "professional"}"""

# 2. Initialize Service
generator = create_media_generator(mock_llm_caller)

# 3. Test the Translation
print("--- Testing Carousel Generation ---")
result = generator.translate_to_creative_prompt(
    caption="Stop wasting time on manual deployments. Automate your pipeline today! #DevOps #AWS",
    hashtags=["#DevOps", "#AWS", "#Tech"],
    format_type="carousel",
    brand_context="Colors: Neon Blue and Dark Grey. Vibe: Futuristic and Tech-forward."
)

print("\n--- Final Parsed Output ---")
print(json.dumps(result, indent=2))
