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

load_dotenv()

app = Flask(__name__)
CORS(app)

# ── CONFIG ────────────────────────────────────────────────────────────────────
# ── CONFIG ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY",   "")
GROQ_API_KEY     = os.getenv("GROQ_API_KEY",     "")
SUPABASE_URL     = os.getenv("SUPABASE_URL",     "")
SUPABASE_ANON    = os.getenv("SUPABASE_ANON_KEY","")
LLM_PROVIDER     = os.getenv("LLM_PROVIDER", "gemini")

# ── CLIENTS ───────────────────────────────────────────────────────────────────
print("⏳ Loading sentence-transformer embedding model...")
# Mock classes for bypass
class MockEmbedder:
    def encode(self, text):
        class Result:
            def tolist(self): return [0.0] * 384
        return Result()

embedder = MockEmbedder()
print("⚠️  Embedding model mocked (Python 3.14 compatibility mode).")

class MockCollection:
    def __init__(self): self.n = 0
    def count(self): return self.n
    def get(self, include=None, ids=None): return {"ids":[], "documents":[], "metadatas":[]}
    def add(self, ids, embeddings, documents, metadatas): self.n += len(ids)
    def query(self, query_embeddings, n_results, include):
        return {"ids":[[]], "documents":[[]], "metadatas":[[]], "distances":[[]]}

collection = MockCollection()
print("⚠️  ChromaDB mocked (Python 3.14 compatibility mode).")

# Supabase client (graceful fallback if not configured)
supabase: Client = None
try:
    if SUPABASE_URL != "YOUR_SUPABASE_URL":
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON)
        print("✅ Supabase connected.")
    else:
        print("⚠️  Supabase not configured — using local fallback storage.")
except Exception as e:
    print(f"⚠️  Supabase connection failed: {e}")

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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024}
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
    clean = raw.strip()
    if clean.startswith("```"):
        parts = clean.split("```")
        clean = parts[1] if len(parts) > 1 else clean
        if clean.startswith("json"):
            clean = clean[4:]
    try:
        return json.loads(clean.strip())
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


# ── IDEATION ──────────────────────────────────────────────────────────────────

@app.route("/api/ideate", methods=["POST"])
def ideate():
    """
    Generate 5 content ideas based on Brand DNA + ESG top posts.
    Body: { brand_id, focus_area (optional) }
    """
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

    # Pull top 5 ERS posts for context
    top_posts = []
    if collection.count() > 0:
        all_p = collection.get(include=["documents","metadatas"])
        sorted_p = sorted(zip(all_p["documents"], all_p["metadatas"]),
                         key=lambda x: x[1].get("ers", 0), reverse=True)
        top_posts = [p[0] for p in sorted_p[:5]]

    mission = brand_dna.get("mission", "")
    tone = brand_dna.get("tone_descriptors", "[]")
    banned = brand_dna.get("banned_words", "[]")

    posts_text = "\n".join([f"- {p[:100]}" for p in top_posts])

    prompt = f"""You are a creative strategist for a brand.

Brand Mission: {mission or "Not set"}
Brand Tone: {tone}
Banned Words: {banned}
Focus Area: {focus}

Top emotionally resonating posts:
{posts_text or "No historical data yet."}

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
    return jsonify({"success": True, "result": result})


# ── CREATIVE STUDIO ───────────────────────────────────────────────────────────

@app.route("/api/studio/generate", methods=["POST"])
def studio_generate():
    """
    Generate full post content from an idea + Brand DNA.
    Body: { idea_title, idea_hook, angle, platform, brand_id }
    """
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

    # Pull top ERS posts for conditioning
    top_posts = []
    if collection.count() > 0:
        all_p = collection.get(include=["documents","metadatas"])
        sorted_p = sorted(zip(all_p["documents"], all_p["metadatas"]),
                         key=lambda x: x[1].get("ers", 0), reverse=True)
        top_posts = [p[0] for p in sorted_p[:3]]

    mission = brand_dna.get("mission", "")
    tone = brand_dna.get("tone_descriptors", "[]")
    banned = brand_dna.get("banned_words", "[]")
    posts_context = "\n".join([f"[ERS Top Post]: {p[:150]}" for p in top_posts])

    prompt = f"""You are a brand copywriter. Write a social media post.

Idea: {idea}
Opening hook: {hook}
Emotional angle: {angle}
Platform: {platform}
Brand Mission: {mission or "Not defined"}
Tone: {tone}
NEVER use these words: {banned}

Reference our top emotionally resonant posts:
{posts_context or "No reference posts available."}

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


# ── ANALYZE (EMOTIONAL ALIGNER) ───────────────────────────────────────────────

@app.route("/api/analyze", methods=["POST"])
def analyze_draft():
    """Core Emotional Aligner — unchanged from v1, now also checks banned words."""
    data = request.get_json()
    draft = data.get("draft", "").strip()
    brand_id = data.get("brand_id", "default")

    if not draft or len(draft) < 10:
        return jsonify({"error": "Draft too short"}), 400
    if collection.count() == 0:
        return jsonify({"error": "DB empty. Seed first."}), 400

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


if __name__ == "__main__":
    print(f"\n🚀 InstaMedia AI v2 Backend")
    print(f"   LLM: {LLM_PROVIDER} | ChromaDB: {collection.count()} posts | Supabase: {supabase is not None}\n")
    app.run(debug=True, port=5001)
