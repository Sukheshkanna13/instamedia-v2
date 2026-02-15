# InstaMedia AI v2 — Emotional Signal Engine
### TypeScript + Supabase + 4-Module Architecture

Insta Media AI is built on an Orchestrator-Worker Multi-Agent Architecture that coordinates specialized AI agents to deliver autonomous marketing operations. The system leverages AWS serverless infrastructure for scalability and cost-efficiency, with Amazon Bedrock providing the foundation for AI-powered content generation and decision-making.

The architecture follows event-driven patterns where the Orchestrator acts as the central coordinator, delegating tasks to specialized agents (Intelligence Gatherer, Creative Suite, Distribution Engine, and Analyst Agent) that operate independently but maintain state coherence through DynamoDB. This design enables parallel processing, fault isolation, and independent scaling of each agent based on workload.
```
Frontend: React + TypeScript + Vite (no external UI library)
Backend:  Python Flask + ChromaDB + sentence-transformers
Database: Supabase PostgreSQL (free tier) + local fallback
AI:       Gemini 1.5 Flash (free) or Groq Llama 3 (free)
Cost:     $0
```

---

## 4 Modules Built

| Module | What It Does |
|--------|-------------|
| **Brand DNA Vault** | Store tone, colors, banned words, logo. AI reads this before generating. |
| **Ideation** | 5 content ideas conditioned on Brand DNA + ESG emotional memory |
| **Creative Studio** | Split screen: generate post left, emotional score right |
| **Content Calendar** | Visual calendar of scheduled posts + upcoming queue |

---

## Project Structure

```
instamedia-v2/
├── backend/
│   ├── app.py                    ← Flask API (all routes, Supabase integrated)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx               ← Sidebar layout + tab routing
│   │   ├── index.css             ← Full design system (Playfair + IBM Plex Mono)
│   │   ├── main.tsx
│   │   ├── types/index.ts        ← All TypeScript interfaces
│   │   ├── lib/api.ts            ← Typed API client
│   │   └── components/
│   │       ├── ui/
│   │       │   └── ScoreRing.tsx
│   │       └── modules/
│   │           ├── Overview.tsx       ← Dashboard with stats + activity feed
│   │           ├── BrandDNA.tsx       ← Brand DNA Vault form
│   │           ├── Ideation.tsx       ← AI idea generation
│   │           ├── CreativeStudio.tsx ← Generate + Analyze split screen
│   │           └── Calendar.tsx       ← Content calendar + scheduler
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── index.html
├── supabase_schema.sql           ← Run once in Supabase SQL Editor
└── data/brand_posts.csv          ← (copy from v1)
```

---

## DEVELOPER 1 — Backend Setup (30 min)

```bash
cd backend

# Virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
# venv\Scripts\activate       # Windows

# Install (includes supabase client now)
pip install -r requirements.txt

# Configure keys
cp .env.example .env
# Edit .env: add GEMINI_API_KEY at minimum

# Start
python app.py
```

**Verify:** `curl http://localhost:5000/api/health`

**Seed posts:** `curl -X POST http://localhost:5000/api/seed`

---

## DEVELOPER 2 — Frontend Setup (10 min)

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

**TypeScript check:** `npm run typecheck`

---

## Supabase Setup (Optional — 15 min)

> Without Supabase, the app still works using in-memory Python dicts.
> Brand DNA and scheduled posts reset on server restart.
> **For the demo, local mode is fine.**

### If you want persistence:

1. Go to https://supabase.com → New project (free)
2. Dashboard → SQL Editor → paste `supabase_schema.sql` → Run
3. Dashboard → Project Settings → API → copy URL and anon key
4. Add to `backend/.env`:
   ```
   SUPABASE_URL=https://xxxx.supabase.co
   SUPABASE_ANON_KEY=eyJhbGc...
   ```
5. Restart Flask

---

## All API Endpoints (v2)

| Method | Endpoint | Module |
|--------|----------|--------|
| GET  | `/api/health`          | All |
| POST | `/api/seed`            | Setup |
| GET  | `/api/brand-dna`       | Brand DNA |
| POST | `/api/brand-dna`       | Brand DNA |
| POST | `/api/ideate`          | Ideation |
| POST | `/api/studio/generate` | Creative Studio |
| POST | `/api/analyze`         | Creative Studio |
| POST | `/api/posts/schedule`  | Calendar |
| GET  | `/api/posts/calendar`  | Calendar |
| GET  | `/api/posts/recent`    | Overview |
| GET  | `/api/posts/stats`     | Overview |
| GET  | `/api/stats`           | ESG |
| GET  | `/api/posts`           | Library |
| POST | `/api/generate`        | Generator |

---

## Developer Split — 24-Hour Plan

### Dev 1 (Backend / AI)
**Hours 1–4:** Setup Flask v2 + seed ChromaDB + test `/api/analyze`
**Hours 5–8:** Wire up Supabase OR confirm local fallback works
**Hours 9–12:** Test `/api/ideate` and `/api/studio/generate` end-to-end
**Hours 12–16:** Test all scheduling endpoints + final integration

### Dev 2 (Frontend / TypeScript)
**Hours 1–4:** `npm install` + verify App loads + nav works
**Hours 5–8:** Brand DNA form: save/load with real API
**Hours 9–12:** Ideation → Studio flow working (idea → generates post → scores)
**Hours 12–16:** Calendar shows scheduled posts + polish

---

## Demo Script (5 minutes)

1. **Overview** → Show stats cards (hardcoded = fine) + "AI Engine Online"
2. **Brand DNA** → Fill in brand name, mission, 3 tone words, 2 banned words → Save
3. **Ideation** → Click "Generate 5 Ideas" → Show AI ideas with predicted ERS
4. **Studio** → Select idea → Generate post → Score it → Show the analysis split screen
5. **Calendar** → Schedule the post → Show it appearing on the calendar

**The pitch:** "Every other tool just generates content. We score it for emotional resonance against what has actually worked for this brand — before it goes live."

---

## Design System

Font pairing: `Playfair Display` (display/editorial) + `IBM Plex Mono` (labels/data) + `Figtree` (body)

Color system:
- `--teal`    `#00D4B8` — primary actions, scores, online status
- `--coral`   `#FF5757` — errors, banned words, mismatch
- `--violet`  `#A78BFA` — tone/creative elements
- `--amber`   `#F5A623` — warnings, weak scores
- `--emerald` `#34D399` — success, strong match
