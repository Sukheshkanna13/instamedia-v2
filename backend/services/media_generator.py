"""
Media Generator Service - Phase 6, Days 10-11
Translates text captions into creative prompts for multi-modal content generation.

Supports three formats:
1. Single Image - One high-quality image prompt
2. Carousel - 3-5 slides with individual prompts
3. Video Storyboard - 5-8 scenes with keyframe descriptions
"""

import json
import re
from typing import Dict, List, Any, Literal

MediaFormat = Literal["image", "carousel", "video"]


class MediaGeneratorService:
    """Service for translating captions to creative prompts for image generation"""
    
    def __init__(self, llm_caller):
        """
        Initialize with LLM caller function
        
        Args:
            llm_caller: Function that takes a prompt string and returns LLM response
        """
        self.call_llm = llm_caller
    
    def translate_to_creative_prompt(
        self, 
        caption: str, 
        hashtags: List[str], 
        format_type: MediaFormat,
        brand_context: str = ""
    ) -> Dict[str, Any]:
        """
        Main entry point: Translate caption to creative prompt based on format
        
        Args:
            caption: The post caption/text
            hashtags: List of hashtags (with or without #)
            format_type: "image", "carousel", or "video"
            brand_context: Optional brand DNA context
            
        Returns:
            Dict with format-specific structure
        """
        if format_type == "image":
            return self.generate_image_prompt(caption, hashtags, brand_context)
        elif format_type == "carousel":
            return self.generate_carousel_slides(caption, hashtags, brand_context)
        elif format_type == "video":
            return self.generate_video_storyboard(caption, hashtags, brand_context)
        else:
            raise ValueError(f"Unknown format: {format_type}")
    
    def generate_image_prompt(
        self, 
        caption: str, 
        hashtags: List[str],
        brand_context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate a single image prompt from caption
        
        Returns:
            {
                "format": "image",
                "image_prompt": str,
                "style": str,
                "mood": str
            }
        """
        # Clean hashtags
        clean_tags = [h.replace("#", "").strip() for h in hashtags if h.strip()]
        hashtag_str = ", ".join(clean_tags[:5]) if clean_tags else "professional, modern"
        
        prompt = f"""You are a creative director translating social media captions into visual image prompts for AI image generation.

CAPTION:
"{caption}"

HASHTAGS: {hashtag_str}

{f"BRAND CONTEXT: {brand_context}" if brand_context else ""}

Create a detailed image prompt that captures the essence of this caption. The prompt should be:
- Visually descriptive (colors, composition, lighting, mood)
- Professional and engaging
- Suitable for social media (Instagram/LinkedIn)
- 1-2 sentences maximum
- CRITICAL: The prompt MUST explicitly ask for "negative space" or "clean areas" (especially near the bottom-right or edges) specifically intended for text overlays and brand logo placement.
- CRITICAL: Strongly enforce and mention the specific brand hex colors and visual guidelines provided in the BRAND CONTEXT.

Return ONLY a JSON object with this structure:
{{
    "format": "image",
    "image_prompt": "detailed visual description here, including instructions for negative space and brand colors",
    "style": "photography style (e.g., 'modern minimalist', 'vibrant editorial', 'cinematic')",
    "mood": "emotional tone (e.g., 'inspiring', 'professional', 'energetic')"
}}

JSON:"""

        response = self.call_llm(prompt)
        return self._parse_json_response(response, {
            "format": "image",
            "image_prompt": "A professional, modern image representing the content",
            "style": "modern minimalist",
            "mood": "professional"
        })
    
    def generate_carousel_slides(
        self, 
        caption: str, 
        hashtags: List[str],
        brand_context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate 3-5 carousel slides from caption
        
        Returns:
            {
                "format": "carousel",
                "slide_count": int,
                "slides": [
                    {
                        "slide_number": 1,
                        "title": str,
                        "content": str,
                        "image_prompt": str
                    },
                    ...
                ]
            }
        """
        clean_tags = [h.replace("#", "").strip() for h in hashtags if h.strip()]
        hashtag_str = ", ".join(clean_tags[:5]) if clean_tags else "professional, modern"
        
        prompt = f"""You are a creative director creating a carousel post (3-5 slides) for social media.

CAPTION:
"{caption}"

HASHTAGS: {hashtag_str}

{f"BRAND CONTEXT: {brand_context}" if brand_context else ""}

Break this caption into 3-5 engaging carousel slides. Each slide should:
- Have a clear title (3-5 words)
- Have concise content (1-2 sentences)
- Have a visual prompt for image generation

Return ONLY a JSON object with this structure:
{{
    "format": "carousel",
    "slide_count": 3,
    "slides": [
        {{
            "slide_number": 1,
            "title": "Hook Title",
            "content": "Brief engaging content for this slide",
            "image_prompt": "Visual description for this slide's image"
        }},
        {{
            "slide_number": 2,
            "title": "Next Point",
            "content": "Content for slide 2",
            "image_prompt": "Visual description for slide 2"
        }},
        {{
            "slide_number": 3,
            "title": "Final Takeaway",
            "content": "Closing content",
            "image_prompt": "Visual description for final slide"
        }}
    ]
}}

Create 3-5 slides (choose the right number based on content depth).

JSON:"""

        response = self.call_llm(prompt)
        default = {
            "format": "carousel",
            "slide_count": 3,
            "slides": [
                {
                    "slide_number": 1,
                    "title": "Introduction",
                    "content": "Opening slide content",
                    "image_prompt": "Professional opening image"
                },
                {
                    "slide_number": 2,
                    "title": "Main Point",
                    "content": "Key message content",
                    "image_prompt": "Engaging visual for main point"
                },
                {
                    "slide_number": 3,
                    "title": "Conclusion",
                    "content": "Closing message",
                    "image_prompt": "Strong closing visual"
                }
            ]
        }
        return self._parse_json_response(response, default)
    
    def generate_video_storyboard(
        self, 
        caption: str, 
        hashtags: List[str],
        brand_context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate 5-8 video storyboard scenes from caption
        
        Returns:
            {
                "format": "video",
                "scene_count": int,
                "total_duration": str,
                "storyboard": [
                    {
                        "scene_number": 1,
                        "description": str,
                        "duration": str,
                        "keyframe_prompt": str
                    },
                    ...
                ]
            }
        """
        clean_tags = [h.replace("#", "").strip() for h in hashtags if h.strip()]
        hashtag_str = ", ".join(clean_tags[:5]) if clean_tags else "professional, modern"
        
        prompt = f"""You are a video director creating a storyboard for a short-form video (Instagram Reel, TikTok, YouTube Short).

CAPTION:
"{caption}"

HASHTAGS: {hashtag_str}

{f"BRAND CONTEXT: {brand_context}" if brand_context else ""}

Create a 5-8 scene storyboard for a 15-30 second video. Each scene should:
- Have a clear description of what happens
- Have a duration (2-5 seconds)
- Have a keyframe image prompt (the key visual moment)

Return ONLY a JSON object with this structure:
{{
    "format": "video",
    "scene_count": 5,
    "total_duration": "20s",
    "storyboard": [
        {{
            "scene_number": 1,
            "description": "Opening hook - what grabs attention",
            "duration": "3s",
            "keyframe_prompt": "Visual description of key moment in this scene"
        }},
        {{
            "scene_number": 2,
            "description": "Scene 2 action",
            "duration": "4s",
            "keyframe_prompt": "Key visual for scene 2"
        }},
        {{
            "scene_number": 3,
            "description": "Scene 3 action",
            "duration": "4s",
            "keyframe_prompt": "Key visual for scene 3"
        }},
        {{
            "scene_number": 4,
            "description": "Scene 4 action",
            "duration": "4s",
            "keyframe_prompt": "Key visual for scene 4"
        }},
        {{
            "scene_number": 5,
            "description": "Closing with CTA",
            "duration": "5s",
            "keyframe_prompt": "Strong closing visual"
        }}
    ]
}}

Create 5-8 scenes (choose based on content complexity). Total duration should be 15-30 seconds.

JSON:"""

        response = self.call_llm(prompt)
        default = {
            "format": "video",
            "scene_count": 5,
            "total_duration": "20s",
            "storyboard": [
                {
                    "scene_number": 1,
                    "description": "Opening hook",
                    "duration": "3s",
                    "keyframe_prompt": "Attention-grabbing opening visual"
                },
                {
                    "scene_number": 2,
                    "description": "Main content introduction",
                    "duration": "4s",
                    "keyframe_prompt": "Key message visual"
                },
                {
                    "scene_number": 3,
                    "description": "Supporting point",
                    "duration": "4s",
                    "keyframe_prompt": "Supporting visual"
                },
                {
                    "scene_number": 4,
                    "description": "Climax or key insight",
                    "duration": "4s",
                    "keyframe_prompt": "Impactful moment visual"
                },
                {
                    "scene_number": 5,
                    "description": "Closing with call-to-action",
                    "duration": "5s",
                    "keyframe_prompt": "Strong closing visual with CTA"
                }
            ]
        }
        return self._parse_json_response(response, default)
    
    def _parse_json_response(self, response: str, default: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse JSON from LLM response, handling markdown fences and errors
        
        Args:
            response: Raw LLM response
            default: Default structure to return on parse failure
            
        Returns:
            Parsed JSON dict or default
        """
        try:
            # Remove markdown code fences
            cleaned = re.sub(r'```json\s*|\s*```', '', response.strip())
            cleaned = cleaned.strip()
            
            # Remove any leading/trailing text before/after JSON
            # Try to find JSON object
            if '{' in cleaned:
                start = cleaned.index('{')
                # Find matching closing brace
                brace_count = 0
                end = start
                for i in range(start, len(cleaned)):
                    if cleaned[i] == '{':
                        brace_count += 1
                    elif cleaned[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
                
                json_str = cleaned[start:end]
                parsed = json.loads(json_str)
                
                # Validate structure
                if isinstance(parsed, dict):
                    return parsed
            
            # If no JSON found, log the response for debugging
            print(f"⚠️  Could not find valid JSON in LLM response")
            print(f"Response preview: {response[:200]}...")
            return default
            
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON decode error: {e}")
            print(f"Attempted to parse: {json_str[:200] if 'json_str' in locals() else 'N/A'}...")
            return default
        except Exception as e:
            print(f"⚠️  Unexpected parse error: {e}")
            return default


# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────

def create_media_generator(llm_caller) -> MediaGeneratorService:
    """Factory function to create MediaGeneratorService instance"""
    return MediaGeneratorService(llm_caller)
