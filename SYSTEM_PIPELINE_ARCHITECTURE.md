# InstaMedia AI v2 - System Pipeline Architecture

**Date**: March 2, 2026  
**Version**: 2.0  
**Purpose**: Complete system architecture and data flow documentation

---

## 🏗️ System Overview

InstaMedia AI v2 is an **Emotional Signal Engine** that helps brands create emotionally resonant social media content by analyzing engagement patterns and generating AI-powered content ideas.

### Core Components
1. **Frontend**: React + TypeScript + Vite
2. **Backend**: Flask + Python
3. **AI/ML**: Gemini/Groq LLM + Sentence Transformers
4. **Database**: ChromaDB (vector) + Supabase (relational)
5. **Web Scraping**: Apify (Instagram)
6. **Deployment**: AWS Amplify / Vercel

---

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (React Frontend - Vite)                      │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────────┐  │
│  │ Overview │ Brand DNA│ Ideation │  Studio  │   Calendar   │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────────┘  │
│  ┌──────────┬──────────┬──────────────────────────────────┐    │
│  │ Database │  Drift   │  Cold Start  │   Connections    │    │
│  └──────────┴──────────┴──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API LAYER                          │
│                     (Flask - Python)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Brand DNA  │  Ideation  │  Studio  │  Calendar  │ Stats │  │
│  │  Analyze    │  Scrape    │  Health  │  Seed      │       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                      AI/ML PROCESSING                           │
│  ┌──────────────────┬──────────────────┬──────────────────┐    │
│  │  Gemini/Groq LLM │ Sentence Trans.  │  Emotion Analysis│    │
│  │  (Content Gen)   │  (Embeddings)    │  (Classification)│    │
│  └──────────────────┴──────────────────┴──────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                      DATA STORAGE                               │
│  ┌──────────────────┬──────────────────┬──────────────────┐    │
│  │   ChromaDB       │    Supabase      │   Apify API      │    │
│  │ (Vector Store)   │  (Relational)    │ (Web Scraping)   │    │
│  └──────────────────┴──────────────────┴──────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Core Data Pipelines

### Pipeline 1: Content Ideation Flow

```
User Input (Focus Area, Context)
    ↓
Frontend: IdeationEnhanced.tsx
    ↓ POST /api/ideate
Backend: ideate() endpoint
    ↓
1. Fetch Brand DNA from Supabase/Local
2. Query ChromaDB for top 5 ERS posts
3. Build LLM prompt with context
    ↓
Gemini/Groq LLM
    ↓
Generate 5 content ideas with:
    - Title
    - Hook
    - Emotional Angle
    - Platform
    - Predicted ERS
    ↓
Return JSON to Frontend
    ↓
Display ideas with selection UI
    ↓
User selects idea → Navigate to Studio
```

### Pipeline 2: Creative Studio Flow

```
Selected Idea from Ideation
    ↓
Frontend: CreativeStudio.tsx
    ↓ POST /api/studio/generate
Backend: studio_generate() endpoint
    ↓
1. Fetch Brand DNA
2. Query top 3 ERS posts for conditioning
3. Build comprehensive prompt
    ↓
Gemini/Groq LLM
    ↓
Generate full post with:
    - Post text (platform-appropriate)
    - Hashtags
    - Image style prompt
    - Call-to-action
    - Word count
    ↓
Return to Frontend
    ↓
Display with editing options
    ↓
User approves → Schedule or Publish
```

### Pipeline 3: Emotional Analysis Flow

```
User Draft Text
    ↓
Frontend: CreativeStudio.tsx
    ↓ POST /api/analyze
Backend: analyze_draft() endpoint
    ↓
1. Check banned words from Brand DNA
2. Generate embedding for draft
    ↓
ChromaDB Vector Search
    ↓
Find top 20 similar posts
    ↓
Calculate combined score:
    - Semantic similarity (40%)
    - ERS score (60%)
    ↓
Select top 5 reference posts
    ↓
Build analysis prompt with references
    ↓
Gemini/Groq LLM
    ↓
Analyze and return:
    - Resonance score (0-100)
    - Verdict (STRONG_MATCH/GOOD_MATCH/WEAK_MATCH/MISMATCH)
    - Emotional archetype
    - What works
    - What's missing
    - Missing signals
    - Rewrite suggestion
    - Banned words found
    - Confidence level
    ↓
Return analysis to Frontend
    ↓
Display with visual feedback
```

### Pipeline 4: Database Expansion (Web Scraping)

```
User Input (Keywords, Platforms, Count)
    ↓
Frontend: DatabaseExpansion.tsx
    ↓ POST /api/database/scrape
Backend: scrape_posts() endpoint
    ↓
Check Apify API Key
    ↓
For each platform:
    ↓
    Instagram: scrape_platform()
        ↓
        Apify Instagram Hashtag Scraper
        ↓
        Extract: caption, likes, comments
        ↓
    LinkedIn: (Not available - skip)
    Twitter: (Not available - skip)
    ↓
For each scraped post:
    ↓
    1. Calculate ERS
    2. Analyze emotion with LLM
    ↓
Return scraped posts to Frontend
    ↓
Display with preview and selection UI
    ↓
User selects posts to add
    ↓ POST /api/database/add-posts
Backend: add_scraped_posts() endpoint
    ↓
For each selected post:
    ↓
    1. Generate embedding
    2. Store in ChromaDB with metadata
    ↓
Update database statistics
    ↓
Return success to Frontend
```

### Pipeline 5: Brand DNA Management

```
User Input (Brand Details)
    ↓
Frontend: BrandDNA.tsx
    ↓ POST /api/brand-dna
Backend: save_brand_dna() endpoint
    ↓
Build record with:
    - brand_id
    - brand_name
    - mission
    - tone_descriptors
    - hex_colors
    - banned_words
    - typography
    - logo_url
    - updated_at
    ↓
Check if exists in Supabase
    ↓
    If exists: UPDATE
    If not: INSERT
    ↓
Fallback to local storage if Supabase unavailable
    ↓
Return success to Frontend
```

---

## 🗄️ Data Models

### ChromaDB (Vector Database)

**Collection**: `posts`

**Document**: Post text content

**Metadata**:
```json
{
  "ers": 72.5,
  "likes": 1500,
  "comments": 120,
  "shares": 45,
  "platform": "instagram",
  "emotion": "Inspiring",
  "source": "scraped" | "seed"
}
```

**Embedding**: 384-dimensional vector (sentence-transformers)

### Supabase (Relational Database)

**Table**: `brand_dna`
```sql
{
  id: UUID,
  brand_id: STRING,
  brand_name: STRING,
  mission: TEXT,
  tone_descriptors: JSON,
  hex_colors: JSON,
  banned_words: JSON,
  typography: STRING,
  logo_url: STRING,
  updated_at: TIMESTAMP
}
```

**Table**: `scheduled_posts`
```sql
{
  id: UUID,
  content: TEXT,
  platform: STRING,
  scheduled_time: TIMESTAMP,
  brand_id: STRING,
  resonance_score: INTEGER,
  image_style: TEXT,
  hashtags: JSON,
  status: STRING,
  created_at: TIMESTAMP
}
```

---

## 🔌 API Endpoints

### Brand DNA
- `GET /api/brand-dna?brand_id=default` - Fetch brand DNA
- `POST /api/brand-dna` - Save/update brand DNA

### Content Generation
- `POST /api/ideate` - Generate 5 content ideas
- `POST /api/studio/generate` - Generate full post
- `POST /api/analyze` - Analyze draft for emotional resonance

### Database Management
- `POST /api/database/scrape` - Scrape posts from social media
- `POST /api/database/add-posts` - Add scraped posts to database
- `GET /api/database/stats` - Get database statistics

### Scheduling
- `POST /api/posts/schedule` - Schedule a post
- `GET /api/posts/calendar?brand_id=default` - Get calendar posts
- `GET /api/posts/recent?brand_id=default&limit=5` - Get recent posts
- `GET /api/posts/stats?brand_id=default` - Get post statistics

### System
- `GET /api/health` - Health check
- `POST /api/seed` - Seed database with sample posts
- `GET /api/stats` - Get ERS statistics
- `GET /api/posts` - Get all posts

---

## 🧠 AI/ML Components

### 1. Sentence Transformers (Embeddings)
**Model**: `all-MiniLM-L6-v2`
**Purpose**: Convert text to 384-dim vectors
**Usage**: Semantic similarity search in ChromaDB

### 2. Gemini LLM (Primary)
**Model**: `gemini-2.5-flash`
**API**: Google AI Studio
**Usage**:
- Content ideation
- Full post generation
- Emotional analysis
- Emotion classification

### 3. Groq LLM (Alternative)
**Model**: `llama-3.1-8b-instant`
**API**: Groq Cloud
**Usage**: Same as Gemini (fallback option)

### 4. ERS Calculation
**Formula**:
```python
raw = (likes * 0.2) + (comments * 0.5) + (shares * 0.8)
ers = min(round(log1p(raw) * 10, 2), 100.0)
```

**Weights**:
- Likes: 0.2 (passive engagement)
- Comments: 0.5 (active engagement)
- Shares: 0.8 (highest engagement)

---

## 🔐 Environment Configuration

### Required Variables
```env
# LLM Provider
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key
GROQ_API_KEY=your_key

# Web Scraping
APIFY_API_KEY=your_key

# Database (Optional)
SUPABASE_URL=your_url
SUPABASE_ANON_KEY=your_key

# Flask
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5001
```

---

## 📁 Directory Structure

```
instamedia-v2/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   ├── .env.example          # Template
│   └── venv/                 # Virtual environment
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── modules/      # Page components
│   │   │   │   ├── Overview.tsx
│   │   │   │   ├── BrandDNA.tsx
│   │   │   │   ├── IdeationEnhanced.tsx
│   │   │   │   ├── CreativeStudio.tsx
│   │   │   │   ├── Calendar.tsx
│   │   │   │   ├── Connections.tsx
│   │   │   │   ├── DatabaseExpansion.tsx
│   │   │   │   ├── BrandDrift.tsx
│   │   │   │   └── ColdStart.tsx
│   │   │   └── ui/           # UI components
│   │   │       ├── CSVUploader.tsx
│   │   │       ├── OAuthConnect.tsx
│   │   │       └── ScoreRing.tsx
│   │   ├── lib/
│   │   │   └── api.ts        # API client
│   │   ├── types/
│   │   │   └── index.ts      # TypeScript types
│   │   ├── App.tsx           # Main app component
│   │   ├── main.tsx          # Entry point
│   │   └── index.css         # Global styles
│   ├── package.json
│   └── vite.config.ts
│
├── data/
│   └── brand_posts.csv       # Sample data (51 posts)
│
└── .kiro/
    └── specs/
        └── insta-media-ai/   # Specifications
```

---

## 🔄 Request/Response Flow Examples

### Example 1: Generate Content Ideas

**Request**:
```http
POST /api/ideate
Content-Type: application/json

{
  "brand_id": "default",
  "focus_area": "Focus: Product launch\nTarget Audience: Millennials\nGoal: Drive engagement\nTone: Inspiring, Authentic\nPlatforms: Instagram, LinkedIn"
}
```

**Response**:
```json
{
  "success": true,
  "result": {
    "ideas": [
      {
        "id": "1",
        "title": "Behind the Innovation",
        "hook": "What if we told you this product took 3 years to perfect?",
        "angle": "Vulnerability",
        "platform": "Instagram",
        "predicted_ers": 78
      }
    ]
  }
}
```

### Example 2: Scrape Instagram Posts

**Request**:
```http
POST /api/database/scrape
Content-Type: application/json

{
  "keywords": "sustainability",
  "platforms": ["instagram"],
  "count": 10
}
```

**Response**:
```json
{
  "success": true,
  "mode": "live",
  "scraped_posts": [
    {
      "text": "Join us at Plastics Recycling Show...",
      "likes": 150,
      "comments": 12,
      "shares": 0,
      "platform": "instagram",
      "emotion": "Inspiring",
      "ers": 45.2
    }
  ],
  "message": "Found 5 real posts from Instagram."
}
```

---

## 🚀 Deployment Pipeline

### Development
```bash
# Backend
cd backend
source venv/bin/activate
python app.py
# → http://127.0.0.1:5001

# Frontend
cd frontend
npm run dev
# → http://localhost:5173
```

### Production (AWS Amplify)
```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm install
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/dist
    files:
      - '**/*'
backend:
  phases:
    build:
      commands:
        - cd backend
        - pip install -r requirements.txt
```

---

## 📊 Performance Metrics

### Response Times
- Health check: <50ms
- Ideation: 2-5 seconds (LLM)
- Studio generation: 3-7 seconds (LLM)
- Analysis: 2-4 seconds (LLM + vector search)
- Scraping: 10-30 seconds (Apify)
- Database query: <100ms

### Throughput
- API requests: ~100 req/min
- Vector search: ~1000 queries/sec
- LLM calls: Limited by API rate limits

---

## 🔒 Security Considerations

### API Keys
- Stored in `.env` (gitignored)
- Never exposed to frontend
- Validated on backend

### Data Privacy
- Brand DNA stored locally or Supabase
- No PII collected
- Posts anonymized

### Rate Limiting
- LLM: 15 req/min (Gemini free tier)
- Apify: Based on plan
- Backend: No limits (add if needed)

---

## 🎯 Key Features Summary

1. **Brand DNA Vault**: Store brand identity
2. **Content Ideation**: AI-generated ideas with context
3. **Creative Studio**: Full post generation
4. **Emotional Analysis**: Draft scoring
5. **Database Expansion**: Instagram scraping
6. **Calendar**: Schedule posts
7. **Brand Drift**: Monitor consistency
8. **Cold Start**: Bootstrap with archetypes

---

## 📈 Scalability Considerations

### Current Limitations
- ChromaDB: In-memory (lost on restart)
- Supabase: Optional (local fallback)
- Single server deployment

### Production Improvements
- Persistent ChromaDB (disk storage)
- Required Supabase connection
- Load balancer for multiple instances
- Redis caching layer
- CDN for frontend assets

---

This pipeline architecture provides a complete overview of the InstaMedia AI v2 system for context transfer to other LLMs or documentation purposes.
