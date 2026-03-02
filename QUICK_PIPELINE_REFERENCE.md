# InstaMedia AI v2 - Quick Pipeline Reference

**For LLM Context Transfer**

---

## System Stack

```
Frontend: React + TypeScript + Vite
Backend: Flask + Python
AI: Gemini/Groq LLM
Vector DB: ChromaDB
Relational DB: Supabase (optional)
Scraping: Apify (Instagram only)
```

---

## Core Pipelines

### 1. Content Ideation
```
User Input → Frontend (IdeationEnhanced.tsx) 
→ POST /api/ideate 
→ Fetch Brand DNA + Top 5 ERS posts 
→ LLM prompt 
→ Generate 5 ideas 
→ Return JSON
```

### 2. Creative Studio
```
Selected Idea → Frontend (CreativeStudio.tsx) 
→ POST /api/studio/generate 
→ Fetch Brand DNA + Top 3 posts 
→ LLM prompt 
→ Generate full post 
→ Return with hashtags/CTA
```

### 3. Emotional Analysis
```
Draft Text → Frontend 
→ POST /api/analyze 
→ Generate embedding 
→ ChromaDB vector search (top 20) 
→ Calculate similarity + ERS scores 
→ LLM analysis 
→ Return resonance score + suggestions
```

### 4. Database Expansion
```
Keywords + Platform → Frontend (DatabaseExpansion.tsx) 
→ POST /api/database/scrape 
→ Apify Instagram scraper 
→ Extract posts 
→ Calculate ERS + Analyze emotion 
→ Return for review 
→ User selects 
→ POST /api/database/add-posts 
→ Store in ChromaDB
```

---

## Key Endpoints

```
POST /api/ideate              - Generate ideas
POST /api/studio/generate     - Generate full post
POST /api/analyze             - Analyze draft
POST /api/database/scrape     - Scrape Instagram
POST /api/database/add-posts  - Add to database
GET  /api/database/stats      - Database stats
POST /api/brand-dna           - Save brand DNA
GET  /api/brand-dna           - Fetch brand DNA
```

---

## Data Flow

```
User → React Frontend → Flask API → LLM/ChromaDB → Response → UI Update
```

---

## ERS Formula

```python
raw = (likes * 0.2) + (comments * 0.5) + (shares * 0.8)
ers = min(round(log1p(raw) * 10, 2), 100.0)
```

---

## Environment Variables

```env
GEMINI_API_KEY=your_key
APIFY_API_KEY=your_key
SUPABASE_URL=your_url (optional)
SUPABASE_ANON_KEY=your_key (optional)
```

---

## Current Status

✅ Instagram scraping working
⚠️ LinkedIn/Twitter require paid plan
✅ All 3 enhancement phases complete
✅ Production ready

---

## File Structure

```
backend/app.py          - Main Flask app (900 lines)
frontend/src/App.tsx    - Main React app
frontend/src/lib/api.ts - API client
frontend/src/components/modules/ - 9 page components
data/brand_posts.csv    - 51 sample posts
```

---

## Key Features

1. Brand DNA Vault
2. Multi-step Ideation (16 focus options)
3. Creative Studio (full post generation)
4. Emotional Analysis (vector similarity)
5. Database Expansion (Instagram scraping)
6. Calendar & Scheduling
7. Brand Drift Detection
8. Cold Start Bootstrap

---

This is the complete working system ready for deployment.
