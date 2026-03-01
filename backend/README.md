# InstaMedia AI - Backend Setup

Flask backend for the InstaMedia AI Emotional Signal Engine.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

**Option A - Interactive Setup (Recommended)**:
```bash
python setup_keys.py
```

**Option B - Manual Setup**:
1. Open `backend/.env` in your editor
2. Add your Gemini or Groq API key (see `API_KEYS_SETUP.md` for details)
3. Save the file

### 3. Verify Configuration
```bash
python verify_setup.py
```

### 4. Start Backend
```bash
python app.py
```

Backend will run on: http://127.0.0.1:5001

## 📁 Files Overview

### Core Files
- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (API keys, secrets)
- `.env.example` - Template for environment variables

### Setup Scripts
- `setup_keys.py` - Interactive API key configuration
- `verify_setup.py` - Verify configuration is correct
- `API_KEYS_SETUP.md` - Detailed setup guide

### Debug Scripts
- `debug_ideate.py` - Test content ideation endpoint
- `debug_studio.py` - Test creative studio endpoint
- `debug_supabase.py` - Test Supabase connection
- `verify_gemini_key.py` - Test Gemini API key

## 🔑 Required API Keys

### Minimum (Choose One)
- **Gemini API Key** (Recommended)
  - Get: https://aistudio.google.com/app/apikey
  - Free: 15 req/min, 1M tokens/day
  
- **Groq API Key** (Alternative)
  - Get: https://console.groq.com
  - Free: Fast inference

### Optional
- **Supabase** (for production persistence)
  - Get: https://supabase.com
  - Free: 500MB, 50k rows

- **OAuth Credentials** (for social media posting)
  - Instagram: https://developers.facebook.com/apps/
  - LinkedIn: https://www.linkedin.com/developers/apps
  - Twitter: https://developer.twitter.com/en/portal/dashboard

See `API_KEYS_SETUP.md` for detailed instructions.

## 🧪 Testing

### Health Check
```bash
curl http://127.0.0.1:5001/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "llm_provider": "gemini",
  "posts_in_chromadb": 0,
  "supabase_connected": false
}
```

### Test Endpoints
```bash
# Test content ideation
python debug_ideate.py

# Test creative studio
python debug_studio.py

# Test Supabase connection
python debug_supabase.py
```

## 📋 API Endpoints

### Core Endpoints
- `GET /api/health` - Health check
- `POST /api/seed` - Seed database with sample posts

### Brand DNA
- `GET /api/brand-dna?brand_id={id}` - Get brand DNA
- `POST /api/brand-dna` - Save brand DNA

### ESG (Emotional Signal Generation)
- `POST /api/analyze` - Analyze draft content
- `GET /api/esg/presigned-url` - Get S3 pre-signed URL
- `POST /api/esg/upload` - Trigger ESG ingestion

### Content Generation
- `POST /api/ideate` - Generate content ideas
- `POST /api/studio/generate` - Generate full post
- `POST /api/generate` - Simple content generation

### OAuth
- `GET /api/auth/{platform}` - Initiate OAuth flow
- `GET /api/auth/callback` - OAuth callback handler

### Calendar & Posts
- `POST /api/posts/schedule` - Schedule a post
- `GET /api/posts/calendar` - Get calendar posts
- `GET /api/posts/recent` - Get recent posts
- `GET /api/posts/stats` - Get post statistics

### Stats
- `GET /api/stats` - Get ERS statistics
- `GET /api/posts` - Get all posts

## 🔧 Configuration

### Environment Variables

```env
# LLM Provider (required)
LLM_PROVIDER=gemini  # or "groq"
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here

# Supabase (optional)
SUPABASE_URL=your_url
SUPABASE_ANON_KEY=your_key

# OAuth (optional)
INSTAGRAM_CLIENT_ID=your_id
INSTAGRAM_CLIENT_SECRET=your_secret
LINKEDIN_CLIENT_ID=your_id
LINKEDIN_CLIENT_SECRET=your_secret
TWITTER_CLIENT_ID=your_id
TWITTER_CLIENT_SECRET=your_secret

# Flask
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5001
```

## 🐛 Troubleshooting

### "No LLM API Key found"
- Check `.env` file exists in `backend/` directory
- Verify API key is not placeholder text
- Run `python verify_setup.py` to check configuration

### "Module not found" errors
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### "Port 5001 already in use"
- Stop other Flask processes
- Or change port in `.env`: `PORT=5002`

### Backend shows "mocked mode"
- This is normal for development without Supabase
- Add Supabase credentials to enable persistence

## 📚 Documentation

- `API_KEYS_SETUP.md` - Detailed API key setup guide
- `../STATUS.md` - Overall project status
- `../.kiro/specs/insta-media-ai/` - Architecture and requirements

## 🚀 Production Deployment

For AWS Lambda deployment, see:
- `../.kiro/specs/insta-media-ai/aws-architecture-plan.md`

Key steps:
1. Set up AWS services (Lambda, API Gateway, DynamoDB, OpenSearch)
2. Configure AWS credentials in `.env`
3. Deploy Lambda functions
4. Update frontend API base URL

## 💡 Tips

- Use `python verify_setup.py` to check configuration
- Check `app.py` logs for detailed error messages
- Test individual endpoints with debug scripts
- Monitor API usage in provider dashboards
- Set up billing alerts for AWS services

## 📞 Support

- **Gemini**: https://ai.google.dev/gemini-api/docs
- **Groq**: https://console.groq.com/docs
- **Supabase**: https://supabase.com/docs
- **Flask**: https://flask.palletsprojects.com/

---

**Ready to start?** Run `python setup_keys.py` to configure your API keys! 🚀
