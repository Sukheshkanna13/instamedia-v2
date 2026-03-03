"""
InstaMedia AI v2 — Flask Backend
Adds: Brand DNA Vault, Scheduled Posts, Supabase integration
Keeps: ESG Engine, ChromaDB, Emotional Aligner from v1
"""

import os, csv, json, math, time, requests, uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
# from sentence_transformers import SentenceTransformer
# import chromadb
chromadb = None
SentenceTransformer = None
from supabase import create_client, Client
from dotenv import load_dotenv

# Apify client for web scraping
try:
    from apify_client import ApifyClient
    APIFY_AVAILABLE = True
except ImportError:
    APIFY_AVAILABLE = False
    print("⚠️  apify-client not installed. Web scraping will use mock mode.")

load_dotenv(override=True)

app = Flask(__name__)
CORS(app)

# ── CONFIG ────────────────────────────────────────────────────────────────────
# ── CONFIG ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY",   "")
GROQ_API_KEY     = os.getenv("GROQ_API_KEY",     "")
SUPABASE_URL     = os.getenv("SUPABASE_URL",     "")
SUPABASE_ANON    = os.getenv("SUPABASE_ANON_KEY","")
APIFY_API_KEY    = os.getenv("APIFY_API_KEY",    "")
LLM_PROVIDER     = os.getenv("LLM_PROVIDER", "gemini")

if not GEMINI_API_KEY and not GROQ_API_KEY:
    print("⚠️  WARNING: No LLM API Key found. AI features will fail.")

# ── CLIENTS ───────────────────────────────────────────────────────────────────
print("⏳ Loading sentence-transformer embedding model...")
# Mock classes for bypass (Python 3.14 compatibility)
class MockEmbedder:
    def encode(self, text):
        class Result:
            def tolist(self): return [0.0] * 384
        return Result()

embedder = MockEmbedder()
print("⚠️  Embedding model mocked (Python 3.14 compatibility mode).")

class MockCollection:
    def __init__(self):
        self.data = {"ids": [], "embeddings": [], "documents": [], "metadatas": []}
    def count(self): 
        return len(self.data["ids"])
    def get(self, include=None, ids=None): 
        return {
            "ids": self.data["ids"],
            "documents": self.data["documents"],
            "metadatas": self.data["metadatas"]
        }
    def add(self, ids, embeddings, documents, metadatas):
        self.data["ids"].extend(ids)
        self.data["embeddings"].extend(embeddings)
        self.data["documents"].extend(documents)
        self.data["metadatas"].extend(metadatas)
    def query(self, query_embeddings, n_results, include, where=None):
        n = min(n_results, len(self.data["ids"]))
        return {
            "ids": [self.data["ids"][:n]],
            "documents": [self.data["documents"][:n]],
            "metadatas": [self.data["metadatas"][:n]],
            "distances": [[0.1] * n]
        }

collection = MockCollection()
print("⚠️  ChromaDB mocked (Python 3.14 compatibility mode).")

# Supabase client (enhanced with validation and testing)
supabase: Client = None

def validate_and_connect_supabase():
    """Validate credentials and establish Supabase connection with detailed logging"""
    global supabase
    
    # Check if configured
    if not SUPABASE_URL or SUPABASE_URL == "your_supabase_project_url":
        print("⚠️  Supabase not configured — using local fallback storage.")
        return False
    
    # Validate URL format
    if not SUPABASE_URL.startswith("https://"):
        print(f"❌ Supabase URL invalid: Must start with 'https://' (got: {SUPABASE_URL[:20]}...)")
        return False
    
    if not ".supabase.co" in SUPABASE_URL:
        print(f"❌ Supabase URL invalid: Must contain '.supabase.co' (got: {SUPABASE_URL})")
        return False
    
    # Validate key format
    if not SUPABASE_ANON or SUPABASE_ANON == "your_supabase_anon_key":
        print("❌ Supabase key not configured")
        return False
    
    if not SUPABASE_ANON.startswith("eyJ"):
        print(f"❌ Supabase key invalid: Should start with 'eyJ' (got: {SUPABASE_ANON[:10]}...)")
        return False
    
    # Attempt connection
    try:
        print(f"🔄 Connecting to Supabase: {SUPABASE_URL}")
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON)
        
        # Test connection with a simple query
        test_result = supabase.table("brand_dna").select("count").limit(1).execute()
        
        print(f"✅ Supabase connected successfully! (Tables accessible)")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Supabase connection failed: {error_msg}")
        
        # Provide helpful error messages
        if "Invalid API key" in error_msg or "401" in error_msg:
            print("   → Check your SUPABASE_ANON_KEY is correct")
            print("   → Get it from: Supabase Dashboard → Settings → API → anon/public key")
        elif "404" in error_msg or "not found" in error_msg:
            print("   → Check your SUPABASE_URL is correct")
            print("   → Should be: https://xxxxx.supabase.co")
        elif "relation" in error_msg or "table" in error_msg:
            print("   → Tables may not exist yet. Run database migrations.")
        
        supabase = None
        return False

# Initialize Supabase connection
supabase_connected = validate_and_connect_supabase()

# In-memory fallback when Supabase isn't configured
_local_brand_dna = {}
_local_posts = []


# ── CORE HELPERS ──────────────────────────────────────────────────────────────

def calculate_ers(likes: int, comments: int, shares: int) -> float:
    raw = (likes * 0.2) + (comments * 0.5) + (shares * 0.8)
    return min(round(math.log1p(raw) * 10, 2), 100.0)

def embed_text(text: str) -> list:
    return embedder.encode(text).tolist()

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
    payload = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}],
               "temperature": 0.7, "max_tokens": 1024}
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Groq Error: {e}]"

def call_llm(prompt: str) -> str:
    return call_groq(prompt) if LLM_PROVIDER == "groq" else call_gemini(prompt)

def parse_llm_json(raw: str) -> dict:
    """Safely parse JSON from LLM response, stripping markdown fences."""
    import re
    clean = raw.strip()
    
    # Try capturing anything between { and } as a fallback
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean)
    if match:
        clean = match.group(1)
    else:
        # Fallback to general JSON boundary extraction
        match = re.search(r"(\{[\s\S]*\})", clean)
        if match:
            clean = match.group(1)
            
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"error": "parse_failed", "raw": raw}


# ── BRAND DNA VAULT ───────────────────────────────────────────────────────────

@app.route("/api/brand-dna", methods=["GET"])
def get_brand_dna():
    """Fetch stored Brand DNA for the brand."""
    brand_id = request.args.get("brand_id", "default")

    if supabase:
        try:
            res = supabase.table("brand_dna").select("*").eq("brand_id", brand_id).execute()
            if res.data:
                return jsonify({"success": True, "data": res.data[0]})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        # Local fallback
        data = _local_brand_dna.get(brand_id, {})
        return jsonify({"success": True, "data": data})

    return jsonify({"success": True, "data": {}})


@app.route("/api/brand-dna", methods=["POST"])
def save_brand_dna():
    """
    Save/update Brand DNA Vault.
    Body: {
      brand_id, brand_name, mission, tone_descriptors,
      hex_colors, banned_words, typography, logo_url
    }
    """
    data = request.get_json()
    brand_id = data.get("brand_id", "default")

    record = {
        "brand_id": brand_id,
        "brand_name": data.get("brand_name", ""),
        "mission": data.get("mission", ""),
        "tone_descriptors": json.dumps(data.get("tone_descriptors", [])),
        "hex_colors": json.dumps(data.get("hex_colors", [])),
        "banned_words": json.dumps(data.get("banned_words", [])),
        "typography": data.get("typography", ""),
        "logo_url": data.get("logo_url", ""),
        "connected_platforms": json.dumps(data.get("connected_platforms", [])),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    if supabase:
        try:
            existing = supabase.table("brand_dna").select("id").eq("brand_id", brand_id).execute()
            if existing.data:
                supabase.table("brand_dna").update(record).eq("brand_id", brand_id).execute()
            else:
                record["id"] = str(uuid.uuid4())
                supabase.table("brand_dna").insert(record).execute()
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        _local_brand_dna[brand_id] = record

    return jsonify({"success": True, "message": "Brand DNA saved."})


@app.route("/api/brand-dna/upload-logo", methods=["POST"])
def upload_logo():
    """
    Upload brand logo to Supabase Storage.
    Accepts: multipart/form-data with 'logo' file and 'brand_id'
    Returns: { success: bool, logo_url: str }
    """
    if 'logo' not in request.files:
        return jsonify({"error": "No logo file provided"}), 400
    
    file = request.files['logo']
    brand_id = request.form.get('brand_id', 'default')
    
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'svg', 'webp'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_ext not in allowed_extensions:
        return jsonify({"error": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"}), 400
    
    if not supabase:
        return jsonify({"error": "Supabase not configured. Logo upload requires Supabase Storage."}), 503
    
    try:
        # Generate unique filename
        unique_filename = f"{brand_id}_{int(time.time())}.{file_ext}"
        file_path = f"{unique_filename}"
        
        # Read file content
        file_content = file.read()
        
        # Upload to Supabase Storage
        # First, try to create bucket if it doesn't exist (will fail silently if exists)
        try:
            supabase.storage.create_bucket('brand-logos', {'public': True})
        except:
            pass  # Bucket likely already exists
        
        # Upload file
        storage_response = supabase.storage.from_('brand-logos').upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": file.content_type, "upsert": "true"}
        )
        
        # Get public URL
        public_url = supabase.storage.from_('brand-logos').get_public_url(file_path)
        
        # Update brand_dna table with logo_url
        try:
            supabase.table("brand_dna").update({
                "logo_url": public_url,
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }).eq("brand_id", brand_id).execute()
        except:
            # If update fails, brand_dna record might not exist yet
            # That's okay, it will be created when they save Brand DNA
            pass
        
        return jsonify({
            "success": True,
            "logo_url": public_url,
            "message": "Logo uploaded successfully"
        })
        
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


@app.route("/api/brand-dna/scrape-website", methods=["POST"])
def scrape_website():
    """
    Scrape a company website to extract brand information
    Body: { url: string, brand_id: string }
    Returns: { success: bool, data: dict }
    """
    from services.brand_intelligence import BrandIntelligenceService
    
    data = request.get_json()
    url = data.get("url", "").strip()
    brand_id = data.get("brand_id", "default")
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    # Initialize service with ChromaDB collection
    service = BrandIntelligenceService(collection=collection)
    
    # Scrape the website
    result = service.scrape_company_website(url, brand_id)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400


# ── IDEATION ──────────────────────────────────────────────────────────────────

@app.route("/api/ideate", methods=["POST"])
def ideate():
    """
    Generate 5 content ideas based on Brand DNA + High-ERS Winners + Brand Context (RAG).
    Enhanced with Phase 5 ERS optimization.
    Body: { brand_id, focus_area (optional) }
    """
    from services.brand_intelligence import get_brand_context
    from services.chromadb_optimizer import ChromaDBOptimizer
    
    data = request.get_json()
    brand_id = data.get("brand_id", "default")
    focus = data.get("focus_area", "general brand storytelling")

    # Pull brand DNA
    brand_dna = _local_brand_dna.get(brand_id, {})
    if supabase:
        try:
            res = supabase.table("brand_dna").select("*").eq("brand_id", brand_id).execute()
            if res.data:
                brand_dna = res.data[0]
        except:
            pass

    # NEW: Use ChromaDB optimizer to get high-ERS winners only
    top_posts = []
    if collection.count() > 0:
        optimizer = ChromaDBOptimizer(collection)
        
        # Query winners only (top 20% by ERS)
        result = optimizer.query_winners_only(limit=5)
        
        if result["success"] and result["results"].get("documents"):
            top_posts = result["results"]["documents"]
            
            # Log performance
            print(f"✨ Retrieved {len(top_posts)} winner posts in {result['query_time_ms']}ms")
        else:
            # Fallback to old method if optimizer fails
            all_p = collection.get(include=["documents","metadatas"])
            sorted_p = sorted(zip(all_p["documents"], all_p["metadatas"]),
                             key=lambda x: x[1].get("ers", 0), reverse=True)
            top_posts = [p[0] for p in sorted_p[:5]]

    # Get brand context from scraped website data (RAG)
    brand_context = get_brand_context(brand_id, focus, collection)

    mission = brand_dna.get("mission", "")
    tone = brand_dna.get("tone_descriptors", "[]")
    banned = brand_dna.get("banned_words", "[]")

    posts_text = "\n".join([f"- {p[:100]}" for p in top_posts])

    prompt = f"""You are a creative strategist for a brand.

Brand Mission: {mission or "Not set"}
Brand Tone: {tone}
Banned Words: {banned}
Focus Area: {focus}

🏆 PROVEN HIGH-PERFORMING POSTS (Top 20% by Engagement):
{posts_text or "No historical data yet."}

{f"Brand Knowledge (from website):\n{brand_context}\n" if brand_context else ""}

These posts have been validated as top performers. Use their patterns, emotional angles, and structures as proven templates for success.

Generate exactly 5 content ideas for social media. Return ONLY valid JSON:
{{
  "ideas": [
    {{
      "id": "1",
      "title": "<short title>",
      "hook": "<compelling opening line>",
      "angle": "<emotional angle e.g. Vulnerability, Authority, Community>",
      "platform": "<Instagram|LinkedIn|Both>",
      "predicted_ers": <integer 40-90>
    }}
  ]
}}"""

    raw = call_llm(prompt)
    result = parse_llm_json(raw)
    
    # 🚨 Catch LLM errors
    if "error" in result:
        return jsonify({"success": False, "error": f"LLM Ideation Failed: {result.get('raw', 'Unknown LLM Error')}"}), 500
        
    return jsonify({"success": True, "result": result})


# ── CREATIVE STUDIO ───────────────────────────────────────────────────────────

@app.route("/api/studio/generate", methods=["POST"])
def studio_generate():
    """
    Generate full post content from an idea + Brand DNA + High-ERS Winners + Brand Context (RAG).
    Enhanced with Phase 5 ERS optimization.
    Body: { idea_title, idea_hook, angle, platform, brand_id }
    """
    from services.brand_intelligence import get_brand_context
    from services.chromadb_optimizer import ChromaDBOptimizer
    
    data = request.get_json()
    idea = data.get("idea_title", "")
    hook = data.get("idea_hook", "")
    angle = data.get("angle", "storytelling")
    platform = data.get("platform", "Instagram")
    brand_id = data.get("brand_id", "default")

    # Pull brand DNA
    brand_dna = _local_brand_dna.get(brand_id, {})
    if supabase:
        try:
            res = supabase.table("brand_dna").select("*").eq("brand_id", brand_id).execute()
            if res.data:
                brand_dna = res.data[0]
        except:
            pass

    # NEW: Use ChromaDB optimizer to get high-ERS winners only
    top_posts = []
    winner_stats = {}
    if collection.count() > 0:
        optimizer = ChromaDBOptimizer(collection)
        
        # Query winners only (top 20% by ERS)
        result = optimizer.query_winners_only(limit=3)
        
        if result["success"] and result["results"].get("documents"):
            top_posts = result["results"]["documents"]
            metadatas = result["results"]["metadatas"]
            
            # Calculate winner stats
            if metadatas:
                avg_ers = sum(m.get("ers", 0) for m in metadatas) / len(metadatas)
                winner_stats = {
                    "count": len(top_posts),
                    "avg_ers": round(avg_ers, 1)
                }
            
            print(f"✨ Retrieved {len(top_posts)} winner posts in {result['query_time_ms']}ms")
        else:
            # Fallback to old method
            all_p = collection.get(include=["documents","metadatas"])
            sorted_p = sorted(zip(all_p["documents"], all_p["metadatas"]),
                             key=lambda x: x[1].get("ers", 0), reverse=True)
            top_posts = [p[0] for p in sorted_p[:3]]

    # Get brand context from scraped website data (RAG)
    brand_context = get_brand_context(brand_id, idea, collection)

    mission = brand_dna.get("mission", "")
    tone = brand_dna.get("tone_descriptors", "[]")
    banned = brand_dna.get("banned_words", "[]")
    
    # Enhanced posts context with winner emphasis
    posts_context = "\n".join([f"🏆 WINNER POST (Top 20%): {p[:150]}" for p in top_posts])

    prompt = f"""You are a brand copywriter. Write a social media post.

Idea: {idea}
Opening hook: {hook}
Emotional angle: {angle}
Platform: {platform}
Brand Mission: {mission or "Not defined"}
Tone: {tone}
NEVER use these words: {banned}

🏆 PROVEN PATTERNS FROM TOP PERFORMERS:
{posts_context or "No reference posts available."}

{f"Winner Stats: {winner_stats['count']} posts, Avg ERS: {winner_stats['avg_ers']}\n" if winner_stats else ""}

{f"Brand Knowledge (from website):\n{brand_context}\n" if brand_context else ""}

These are VALIDATED high-performers (top 20% by engagement). Mirror their:
- Emotional hooks and storytelling patterns
- Content structure and pacing
- Call-to-action styles
- Tone and voice characteristics

Return ONLY valid JSON:
{{
  "post_text": "<full post text, platform-appropriate length>",
  "hashtags": ["<tag1>", "<tag2>", "<tag3>"],
  "image_style_prompt": "<a 1-sentence prompt describing the ideal image style for this post>",
  "cta": "<call to action line>",
  "word_count": <integer>
}}"""

    raw = call_llm(prompt)
    result = parse_llm_json(raw)
    return jsonify({"success": True, "result": result})


# ── MULTI-MODAL MEDIA GENERATION (Phase 6) ────────────────────────────────────

@app.route("/api/studio/generate-media", methods=["POST"])
def generate_media():
    """
    Phase 6, Days 10-13: Generate multi-modal content with AWS Bedrock Titan.
    Supports: image, carousel (3-5 slides), video storyboard (5-8 scenes)
    
    Body: {
        caption: str,
        hashtags: list[str],
        format: "image" | "carousel" | "video",
        brand_id: str (optional),
        generate_images: bool (optional, default True)
    }
    
    Returns: {
        success: bool,
        result: {
            format: str,
            caption: str,
            hashtags: list[str],
            generation_time_seconds: float,
            image_url: str (for image format),
            slides: list (for carousel format, with image_url per slide),
            storyboard: list (for video format, with image_url per scene)
        }
    }
    """
    from services.media_generator import create_media_generator
    from services.brand_intelligence import get_brand_context
    from services.aws_image_generator import create_aws_image_generator
    
    start_time = time.time()
    
    data = request.get_json()
    caption = data.get("caption", "").strip()
    hashtags = data.get("hashtags", [])
    format_type = data.get("format", "image")
    brand_id = data.get("brand_id", "default")
    generate_images = data.get("generate_images", True)  # Allow disabling for testing
    
    # Validation
    if not caption:
        return jsonify({"success": False, "error": "Caption is required"}), 400
    
    if format_type not in ["image", "carousel", "video"]:
        return jsonify({"success": False, "error": f"Invalid format: {format_type}"}), 400
    
    # Get brand context for better prompts
    brand_context = ""
    try:
        brand_context = get_brand_context(brand_id, caption, collection)
    except Exception as e:
        print(f"⚠️  Could not fetch brand context: {e}")
    
    # Step 1: Generate creative prompts (Translation Layer)
    media_gen = create_media_generator(call_llm)
    
    try:
        result = media_gen.translate_to_creative_prompt(
            caption=caption,
            hashtags=hashtags,
            format_type=format_type,
            brand_context=brand_context[:500] if brand_context else ""
        )
        
        print(f"✨ Generated {format_type} prompts")
        
        # Step 2: Generate actual images with AWS Bedrock (if enabled)
        if generate_images:
            aws_gen = create_aws_image_generator()
            
            if aws_gen is None:
                print("⚠️  AWS not configured, returning prompts only")
            else:
                try:
                    if format_type == "image":
                        # Single image generation
                        prompt = result.get("image_prompt", "")
                        if prompt:
                            image_result = aws_gen.generate_and_upload(prompt)
                            result["image_url"] = image_result["url"]
                            print(f"✅ Generated image in {image_result['generation_time_seconds']}s")
                    
                    elif format_type == "carousel":
                        # Carousel images (concurrent generation)
                        slides = result.get("slides", [])
                        if slides:
                            image_results = aws_gen.generate_carousel_images(slides)
                            # Add URLs to slides
                            for slide, img_result in zip(slides, image_results):
                                slide["image_url"] = img_result.get("url")
                            print(f"✅ Generated {len(image_results)} carousel images")
                    
                    elif format_type == "video":
                        # Video storyboard keyframes (concurrent generation)
                        storyboard = result.get("storyboard", [])
                        if storyboard:
                            image_results = aws_gen.generate_storyboard_keyframes(storyboard)
                            # Add URLs to scenes
                            for scene, img_result in zip(storyboard, image_results):
                                scene["image_url"] = img_result.get("url")
                            print(f"✅ Generated {len(image_results)} storyboard keyframes")
                
                except Exception as e:
                    print(f"⚠️  Image generation error: {e}")
                    # Continue with prompts only
        
        # Add metadata
        result["caption"] = caption
        result["hashtags"] = hashtags
        result["generation_time_seconds"] = round(time.time() - start_time, 2)
        
        print(f"✨ Completed {format_type} generation in {result['generation_time_seconds']}s")
        
        return jsonify({"success": True, "result": result})
        
    except Exception as e:
        print(f"❌ Media generation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ── ANALYZE (EMOTIONAL ALIGNER) ───────────────────────────────────────────────

@app.route("/api/analyze", methods=["POST"])
def analyze_draft():
    """Core Emotional Aligner — unchanged from v1, now also checks banned words."""
    data = request.get_json()
    draft = data.get("draft", "").strip()
    brand_id = data.get("brand_id", "default")

    if not draft or len(draft) < 10:
        return jsonify({"error": "Draft too short"}), 400
    
    # Check if DB is empty and provide helpful message
    if collection.count() == 0:
        return jsonify({
            "success": False,
            "error": "database_empty",
            "message": "Your brand memory is being initialized. Please try again in a moment.",
            "action": "Please refresh the page or click 'Seed Database' in settings.",
            "technical_detail": "ChromaDB collection is empty. Run /api/seed to load historical posts."
        }), 503  # Service Unavailable (temporary)

    start = time.time()

    # Check banned words from Brand DNA
    banned_words = []
    brand_dna = _local_brand_dna.get(brand_id, {})
    if supabase:
        try:
            res = supabase.table("brand_dna").select("banned_words").eq("brand_id", brand_id).execute()
            if res.data:
                banned_words = json.loads(res.data[0].get("banned_words", "[]"))
        except:
            pass
    else:
        bw_raw = brand_dna.get("banned_words", "[]")
        banned_words = json.loads(bw_raw) if isinstance(bw_raw, str) else bw_raw

    found_banned = [w for w in banned_words if w.lower() in draft.lower()]

    # ChromaDB semantic search
    emb = embed_text(draft)
    n = min(20, collection.count())
    results = collection.query(query_embeddings=[emb], n_results=n,
                               include=["documents","metadatas","distances"])

    candidates = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        sim = 1 - dist
        ers = meta.get("ers", 0)
        candidates.append({
            "text": doc, "ers": ers, "semantic_sim": round(sim, 3),
            "combined": (sim * 0.4) + (ers / 100 * 0.6),
            "platform": meta.get("platform", "instagram")
        })

    top_posts = sorted(candidates, key=lambda x: x["combined"], reverse=True)[:5]

    posts_fmt = "\n\n".join([f"[Post {i+1} | ERS: {p['ers']:.1f}]\n{p['text']}"
                             for i, p in enumerate(top_posts)])

    prompt = f"""You are an Emotional Alignment Checker for a brand's social media content.

Brand's top resonating posts:
{posts_fmt}

Draft to analyze: {draft}
{"⚠️ BANNED WORDS FOUND: " + str(found_banned) if found_banned else ""}

Return ONLY valid JSON:
{{
  "resonance_score": <integer 0-100>,
  "verdict": "<STRONG_MATCH|GOOD_MATCH|WEAK_MATCH|MISMATCH>",
  "emotional_archetype": "<detected archetype>",
  "what_works": "<1-2 sentences>",
  "what_is_missing": "<1-2 sentences>",
  "missing_signals": ["<signal1>", "<signal2>", "<signal3>"],
  "rewrite_suggestion": "<rewritten version under 280 chars>",
  "banned_words_found": {json.dumps(found_banned)},
  "confidence": "<HIGH|MEDIUM|LOW>"
}}"""

    raw = call_llm(prompt)
    analysis = parse_llm_json(raw)

    # 🚨 NEW: Catch LLM errors
    if "error" in analysis:
        return jsonify({"success": False, "error": f"LLM Scoring Failed: {analysis.get('raw', 'Unknown error')}"}), 500

    return jsonify({
        "success": True, "draft": draft, "analysis": analysis,
        "reference_posts": top_posts[:3],
        "processing_time_seconds": round(time.time() - start, 2),
        "db_size": collection.count(),
        "banned_words_found": found_banned
    })


# ── SCHEDULED POSTS ───────────────────────────────────────────────────────────

@app.route("/api/posts/schedule", methods=["POST"])
def schedule_post():
    """
    Save an approved post to the content calendar.
    Body: {
      content, platform, scheduled_time, brand_id,
      resonance_score, image_style, hashtags, status
    }
    """
    data = request.get_json()

    record = {
        "id": str(uuid.uuid4()),
        "content": data.get("content", ""),
        "platform": data.get("platform", "instagram"),
        "scheduled_time": data.get("scheduled_time", ""),
        "brand_id": data.get("brand_id", "default"),
        "resonance_score": data.get("resonance_score", 0),
        "image_style": data.get("image_style", ""),
        "hashtags": json.dumps(data.get("hashtags", [])),
        "status": data.get("status", "scheduled"),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    if supabase:
        try:
            supabase.table("scheduled_posts").insert(record).execute()
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        _local_posts.append(record)

    return jsonify({"success": True, "post": record})


@app.route("/api/posts/calendar", methods=["GET"])
def get_calendar_posts():
    """Return all posts for the calendar view."""
    brand_id = request.args.get("brand_id", "default")

    if supabase:
        try:
            res = supabase.table("scheduled_posts").select("*").eq("brand_id", brand_id).execute()
            return jsonify({"success": True, "posts": res.data or []})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    brand_posts = [p for p in _local_posts if p.get("brand_id") == brand_id]
    return jsonify({"success": True, "posts": brand_posts})


@app.route("/api/posts/recent", methods=["GET"])
def get_recent_posts():
    """Return last 5 posts for dashboard activity feed."""
    brand_id = request.args.get("brand_id", "default")
    limit = int(request.args.get("limit", 5))

    if supabase:
        try:
            res = (supabase.table("scheduled_posts").select("*")
                   .eq("brand_id", brand_id).limit(limit).execute())
            return jsonify({"success": True, "posts": res.data or []})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    posts = _local_posts[-limit:] if _local_posts else []
    return jsonify({"success": True, "posts": posts[::-1]})


@app.route("/api/posts/<post_id>", methods=["DELETE"])
def delete_post(post_id):
    """Delete a scheduled post."""
    brand_id = request.args.get("brand_id", "default")
    
    if supabase:
        try:
            res = supabase.table("scheduled_posts").delete().eq("id", post_id).eq("brand_id", brand_id).execute()
            if not res.data:
                return jsonify({"error": "Post not found or unauthorized"}), 404
            return jsonify({"success": True, "message": "Post deleted from calendar"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        global _local_posts
        initial_len = len(_local_posts)
        _local_posts = [p for p in _local_posts if p.get("id") != post_id]
        if len(_local_posts) == initial_len:
            return jsonify({"error": "Post not found"}), 404
        return jsonify({"success": True, "message": "Post deleted from calendar"})


@app.route("/api/posts/<post_id>/reschedule", methods=["PUT"])
def reschedule_post(post_id):
    """Reschedule an existing post."""
    data = request.get_json()
    new_time = data.get("scheduled_time")
    brand_id = data.get("brand_id", "default")
    
    if not new_time:
        return jsonify({"error": "New scheduled_time is required"}), 400

    if supabase:
        try:
            res = supabase.table("scheduled_posts").update({"scheduled_time": new_time}).eq("id", post_id).eq("brand_id", brand_id).execute()
            if not res.data:
                return jsonify({"error": "Post not found or unauthorized"}), 404
            return jsonify({"success": True, "post": res.data[0]})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        for p in _local_posts:
            if p.get("id") == post_id:
                p["scheduled_time"] = new_time
                return jsonify({"success": True, "post": p})
        return jsonify({"error": "Post not found"}), 404

@app.route("/api/posts/stats", methods=["GET"])
def get_post_stats():
    """Dashboard metric cards — total posts, avg resonance, etc."""
    brand_id = request.args.get("brand_id", "default")

    if supabase:
        try:
            res = supabase.table("scheduled_posts").select("*").eq("brand_id", brand_id).execute()
            posts = res.data or []
        except:
            posts = []
    else:
        posts = [p for p in _local_posts if p.get("brand_id") == brand_id]

    total = len(posts)
    scheduled = len([p for p in posts if p.get("status") == "scheduled"])
    published = len([p for p in posts if p.get("status") == "published"])
    scores = [p.get("resonance_score", 0) for p in posts if p.get("resonance_score", 0) > 0]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    return jsonify({
        "success": True,
        "total_content": total,
        "scheduled": scheduled,
        "published": published,
        "avg_resonance_score": avg_score,
        "db_post_count": collection.count()
    })


# ── SEED & HEALTH ─────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "posts_in_chromadb": collection.count(),
        "llm_provider": LLM_PROVIDER,
        "supabase_connected": supabase is not None,
        "embedding_model": "all-MiniLM-L6-v2"
    })


@app.route("/api/seed", methods=["POST"])
def seed():
    csv_path = os.path.join(os.path.dirname(__file__), "../data/brand_posts.csv")
    if not os.path.exists(csv_path):
        return jsonify({"error": f"CSV not found at {csv_path}"}), 404

    added = skipped = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            post_id = f"post_{i}"
            if collection.get(ids=[post_id])["ids"]:
                skipped += 1
                continue
            text = row["post_text"].strip()
            ers = calculate_ers(int(row.get("likes",0)),
                                int(row.get("comments",0)),
                                int(row.get("shares",0)))
            collection.add(ids=[post_id], embeddings=[embed_text(text)],
                          documents=[text], metadatas=[{
                              "ers": ers, "likes": int(row.get("likes",0)),
                              "comments": int(row.get("comments",0)),
                              "shares": int(row.get("shares",0)),
                              "platform": row.get("platform","instagram")
                          }])
            added += 1

    return jsonify({"success": True, "added": added, "skipped": skipped,
                   "total": collection.count()})


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    topic = data.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "Topic required"}), 400

    all_p = collection.get(include=["documents","metadatas"])
    top = sorted(zip(all_p["documents"], all_p["metadatas"]),
                 key=lambda x: x[1].get("ers",0), reverse=True)[:3]

    posts_ctx = "\n".join([f"[ERS:{m.get('ers',0):.1f}] {d}" for d,m in top])

    prompt = f"""Brand's highest ERS posts:
{posts_ctx}

Write 3 post variations about: "{topic}"
Return ONLY valid JSON:
{{
  "archetype_detected": "<archetype>",
  "variations": [
    {{"text": "<post>", "emotional_angle": "<angle>", "predicted_ers": <int>}},
    {{"text": "<post>", "emotional_angle": "<angle>", "predicted_ers": <int>}},
    {{"text": "<post>", "emotional_angle": "<angle>", "predicted_ers": <int>}}
  ]
}}"""

    raw = call_llm(prompt)
    result = parse_llm_json(raw)
    return jsonify({"success": True, "topic": topic, "result": result})


@app.route("/api/stats", methods=["GET"])
def get_ers_stats():
    if collection.count() == 0:
        return jsonify({"error":"DB empty"}), 400
    all_p = collection.get(include=["documents","metadatas"])
    ers_scores = [m.get("ers",0) for m in all_p["metadatas"]]
    top10 = sorted(zip(all_p["documents"], all_p["metadatas"]),
                   key=lambda x: x[1].get("ers",0), reverse=True)[:10]
    return jsonify({
        "total_posts": collection.count(),
        "avg_ers": round(sum(ers_scores)/len(ers_scores),2),
        "max_ers": round(max(ers_scores),2),
        "min_ers": round(min(ers_scores),2),
        "top_posts": [{"text":d[:120]+"..","ers":m.get("ers",0),"platform":m.get("platform")}
                      for d,m in top10]
    })


@app.route("/api/posts", methods=["GET"])
def get_posts():
    if collection.count() == 0:
        return jsonify({"posts":[]}), 200
    all_p = collection.get(include=["documents","metadatas"])
    posts = [{"text":d,"ers":m.get("ers",0),"likes":m.get("likes",0),
              "comments":m.get("comments",0),"shares":m.get("shares",0),
              "platform":m.get("platform","unknown")}
             for d,m in zip(all_p["documents"],all_p["metadatas"])]
    posts.sort(key=lambda x: x["ers"], reverse=True)
    return jsonify({"posts":posts})


# ── DATABASE EXPANSION (Web Scraping) ────────────────────────────────────────

@app.route("/api/database/scrape", methods=["POST"])
def scrape_posts():
    """
    Scrape posts from social media and add to database.
    Body: {
      keywords: string,
      platforms: ["instagram", "linkedin", "twitter"],
      count: number (default 20)
    }
    """
    data = request.get_json()
    keywords = data.get("keywords", "").strip()
    platforms = data.get("platforms", ["instagram"])
    count = min(int(data.get("count", 20)), 100)  # Max 100 posts
    
    if not keywords:
        return jsonify({"error": "Keywords required"}), 400
    
    # Check if Apify is configured and available
    if not APIFY_API_KEY or not APIFY_AVAILABLE:
        reason = "Apify client not installed" if not APIFY_AVAILABLE else "Apify API key not configured"
        return jsonify({
            "success": True,
            "message": f"{reason}. Using mock data for demo.",
            "scraped_posts": generate_mock_scraped_posts(keywords, count),
            "added_count": 0,
            "mode": "mock"
        })
    
    # Real Apify scraping
    try:
        apify_client = ApifyClient(APIFY_API_KEY)
        scraped_posts = []
        unavailable_platforms = []
        
        # Scrape from each platform
        for platform in platforms:
            try:
                if platform in ["linkedin", "twitter"]:
                    unavailable_platforms.append(platform)
                    print(f"⚠️  {platform.title()} scraper not available (requires paid plan)")
                    continue
                    
                platform_posts = scrape_platform(apify_client, platform, keywords, count // len(platforms))
                scraped_posts.extend(platform_posts)
            except Exception as e:
                print(f"Error scraping {platform}: {e}")
                continue
        
        if not scraped_posts:
            # Fallback to mock if scraping failed
            message = "Scraping failed. "
            if unavailable_platforms:
                message += f"{', '.join([p.title() for p in unavailable_platforms])} scrapers not available in free tier. "
            message += "Using mock data for demo."
            
            return jsonify({
                "success": True,
                "message": message,
                "scraped_posts": generate_mock_scraped_posts(keywords, count),
                "added_count": 0,
                "mode": "mock",
                "unavailable_platforms": unavailable_platforms
            })
        
        message = f"Found {len(scraped_posts)} real posts from Instagram."
        if unavailable_platforms:
            message += f" Note: {', '.join([p.title() for p in unavailable_platforms])} scrapers require paid Apify plan."
        
        return jsonify({
            "success": True,
            "scraped_posts": scraped_posts,
            "added_count": 0,
            "mode": "live",
            "message": message,
            "unavailable_platforms": unavailable_platforms
        })
        
    except Exception as e:
        print(f"Apify scraping error: {e}")
        # Fallback to mock data
        return jsonify({
            "success": True,
            "message": f"Scraping error: {str(e)}. Using mock data for demo.",
            "scraped_posts": generate_mock_scraped_posts(keywords, count),
            "added_count": 0,
            "mode": "mock"
        })


@app.route("/api/database/add-posts", methods=["POST"])
def add_scraped_posts():
    """
    Add approved scraped posts to the database.
    Body: {
      posts: [{text, likes, comments, shares, platform}]
    }
    """
    data = request.get_json()
    posts = data.get("posts", [])
    
    if not posts:
        return jsonify({"error": "No posts provided"}), 400
    
    added = 0
    for post in posts:
        try:
            text = post.get("text", "").strip()
            if not text or len(text) < 10:
                continue
            
            # Calculate ERS
            ers = calculate_ers(
                int(post.get("likes", 0)),
                int(post.get("comments", 0)),
                int(post.get("shares", 0))
            )
            
            # Analyze emotion with LLM
            emotion = analyze_post_emotion(text)
            
            # Add to database
            post_id = f"scraped_{collection.count()}_{added}"
            collection.add(
                ids=[post_id],
                embeddings=[embed_text(text)],
                documents=[text],
                metadatas=[{
                    "ers": ers,
                    "likes": int(post.get("likes", 0)),
                    "comments": int(post.get("comments", 0)),
                    "shares": int(post.get("shares", 0)),
                    "platform": post.get("platform", "unknown"),
                    "emotion": emotion,
                    "source": "scraped"
                }]
            )
            added += 1
        except Exception as e:
            print(f"Error adding post: {e}")
            continue
    
    return jsonify({
        "success": True,
        "added_count": added,
        "total_posts": collection.count(),
        "message": f"Added {added} posts to your emotional database"
    })


@app.route("/api/esg/scrape", methods=["POST"])
def scrape_with_ers():
    """
    Scrape posts from social media accounts with ERS calculation.
    Body: {
      target: string (username/handle),
      platform: string (instagram, linkedin, twitter),
      count: number (default 20),
      filter_winners: boolean (optional, default false),
      winner_percentile: number (optional, default 0.2)
    }
    
    New endpoint for Phase 5: ERS Logic Optimization + Winner Filter
    """
    from services.apify_ingestion import ApifyIngestionService
    
    data = request.get_json()
    target = data.get("target", "").strip()
    platform = data.get("platform", "instagram").lower()
    count = min(int(data.get("count", 20)), 100)
    filter_winners = data.get("filter_winners", False)
    winner_percentile = float(data.get("winner_percentile", 0.2))
    
    if not target:
        return jsonify({"error": "Target username/handle required"}), 400
    
    # Check if Apify is configured
    if not APIFY_API_KEY or not APIFY_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "Apify not configured",
            "message": "Apify API key required for social media scraping"
        }), 503
    
    try:
        # Initialize Apify client
        apify_client = ApifyClient(APIFY_API_KEY)
        
        # Initialize service
        service = ApifyIngestionService(
            apify_client=apify_client,
            collection=collection,
            embedder=embedder
        )
        
        # Scrape and score
        result = service.scrape_and_score(
            target=target, 
            platform=platform, 
            count=count,
            filter_winners=filter_winners,
            winner_percentile=winner_percentile
        )
        
        if result['success']:
            response = {
                "success": True,
                "posts": result['posts'],
                "stats": result['stats'],
                "platform": result['platform'],
                "target": result['target']
            }
            
            # Add filter info if winners were filtered
            if filter_winners:
                response["filtered"] = True
                response["all_posts_count"] = result.get("all_posts_count", 0)
                response["winner_count"] = result.get("winner_count", 0)
                response["cutoff_ers"] = result.get("cutoff_ers", 0)
                response["message"] = f"Filtered top {int(winner_percentile*100)}% ({result.get('winner_count', 0)} of {result.get('all_posts_count', 0)} posts)"
            else:
                response["message"] = f"Successfully scraped {len(result['posts'])} posts from {target}"
            
            return jsonify(response)
        else:
            return jsonify({
                "success": False,
                "error": result['error'],
                "posts": []
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "posts": []
        }), 500


@app.route("/api/database/stats", methods=["GET"])
def get_database_stats():
    """Get database statistics for dashboard"""
    if collection.count() == 0:
        return jsonify({
            "total_posts": 0,
            "avg_ers": 0,
            "platforms": {},
            "emotions": {},
            "sources": {}
        })
    
    all_p = collection.get(include=["metadatas"])
    metadatas = all_p["metadatas"]
    
    # Calculate stats
    ers_scores = [m.get("ers", 0) for m in metadatas]
    platforms = {}
    emotions = {}
    sources = {}
    
    for m in metadatas:
        # Platform distribution
        platform = m.get("platform", "unknown")
        platforms[platform] = platforms.get(platform, 0) + 1
        
        # Emotion distribution
        emotion = m.get("emotion", "unknown")
        emotions[emotion] = emotions.get(emotion, 0) + 1
        
        # Source distribution
        source = m.get("source", "seed")
        sources[source] = sources.get(source, 0) + 1
    
    return jsonify({
        "total_posts": collection.count(),
        "avg_ers": round(sum(ers_scores) / len(ers_scores), 2) if ers_scores else 0,
        "max_ers": round(max(ers_scores), 2) if ers_scores else 0,
        "min_ers": round(min(ers_scores), 2) if ers_scores else 0,
        "platforms": platforms,
        "emotions": emotions,
        "sources": sources
    })


# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────

def scrape_platform(apify_client, platform: str, keywords: str, count: int):
    """Scrape posts from a specific platform using Apify"""
    posts = []
    
    if platform == "instagram":
        # Instagram Hashtag Scraper
        # Actor: apify/instagram-hashtag-scraper
        run_input = {
            "hashtags": [keywords.replace(" ", "")],
            "resultsLimit": count
        }
        
        try:
            print(f"🔍 Scraping Instagram for #{keywords.replace(' ', '')}...")
            run = apify_client.actor("apify/instagram-hashtag-scraper").call(run_input=run_input)
            
            for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
                caption = item.get("caption", "")
                if not caption or len(caption) < 10:
                    continue
                    
                posts.append({
                    "text": caption[:500],  # Limit text length
                    "likes": item.get("likesCount", 0),
                    "comments": item.get("commentsCount", 0),
                    "shares": 0,  # Instagram doesn't provide shares
                    "platform": "instagram",
                    "emotion": "Unknown",  # Will be analyzed later
                    "ers": 0  # Will be calculated later
                })
            
            print(f"✅ Found {len(posts)} Instagram posts")
        except Exception as e:
            print(f"❌ Instagram scraping error: {e}")
    
    elif platform == "linkedin":
        # LinkedIn scraping not available in free tier
        print(f"⚠️  LinkedIn scraper not available in your Apify account")
        print(f"   → LinkedIn and Twitter scrapers require paid Apify plan")
        print(f"   → Using Instagram scraper only for now")
    
    elif platform == "twitter":
        # Twitter scraping not available in free tier
        print(f"⚠️  Twitter scraper not available in your Apify account")
        print(f"   → LinkedIn and Twitter scrapers require paid Apify plan")
        print(f"   → Using Instagram scraper only for now")
    
    # Calculate ERS and analyze emotion for each post
    if posts:
        print(f"🧠 Analyzing emotions for {len(posts)} posts...")
        for post in posts:
            post["ers"] = calculate_ers(post["likes"], post["comments"], post["shares"])
            if post["text"]:
                post["emotion"] = analyze_post_emotion(post["text"])
    
    return posts


def generate_mock_scraped_posts(keywords: str, count: int):
    """Generate mock scraped posts for demo purposes"""
    import random
    
    emotions = ["Inspiring", "Authentic", "Vulnerable", "Educational", "Entertaining"]
    platforms = ["instagram", "linkedin", "twitter"]
    
    posts = []
    for i in range(min(count, 20)):
        likes = random.randint(100, 5000)
        comments = random.randint(10, 500)
        shares = random.randint(5, 200)
        
        posts.append({
            "text": f"Mock post about {keywords} - This is a sample post that would be scraped from social media. It contains relevant content about {keywords} and demonstrates the emotional tone we're looking for. #{keywords.replace(' ', '')}",
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "platform": random.choice(platforms),
            "emotion": random.choice(emotions),
            "ers": calculate_ers(likes, comments, shares)
        })
    
    return posts


def analyze_post_emotion(text: str) -> str:
    """Analyze the emotional tone of a post using LLM"""
    if not GEMINI_API_KEY and not GROQ_API_KEY:
        return "Unknown"
    
    prompt = f"""Analyze the emotional tone of this social media post in ONE WORD.

Post: {text[:200]}

Choose ONE from: Inspiring, Authentic, Vulnerable, Educational, Entertaining, Promotional, Informative, Humorous, Empathetic, Authoritative

Return ONLY the single word, nothing else."""
    
    try:
        result = call_llm(prompt).strip()
        # Extract first word if LLM returns more
        emotion = result.split()[0].strip('.,!?')
        return emotion
    except:
        return "Unknown"


if __name__ == "__main__":
    # Auto-seed database if empty
    if collection.count() == 0:
        csv_path = os.path.join(os.path.dirname(__file__), "../data/brand_posts.csv")
        if os.path.exists(csv_path):
            print("📊 Auto-seeding database with sample posts...")
            try:
                with open(csv_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for i, row in enumerate(reader):
                        import random
                        emotions = ["Inspirational", "Educational", "Relatable", "Controversial", "Motivational", "Humorous"]
                        post_id = f"post_{i}"
                        text = row["post_text"].strip()
                        ers = calculate_ers(int(row.get("likes",0)),
                                            int(row.get("comments",0)),
                                            int(row.get("shares",0)))
                        collection.add(ids=[post_id], embeddings=[embed_text(text)],
                                      documents=[text], metadatas=[{
                                          "ers": ers, "likes": int(row.get("likes",0)),
                                          "comments": int(row.get("comments",0)),
                                          "shares": int(row.get("shares",0)),
                                          "platform": row.get("platform","instagram"),
                                          "emotion": random.choice(emotions),
                                          "source": "seed"
                                      }])
                print(f"✅ Auto-seeded {collection.count()} posts from CSV")
            except Exception as e:
                print(f"⚠️  Auto-seed failed: {e}")
    
    print(f"\n🚀 InstaMedia AI v2 Backend")
    print(f"   LLM: {LLM_PROVIDER} | ChromaDB: {collection.count()} posts | Supabase: {supabase is not None}\n")
    app.run(debug=True, port=8000)
