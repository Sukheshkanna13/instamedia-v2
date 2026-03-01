# API Keys Setup Guide

This guide will help you get all the necessary API keys to run InstaMedia AI with full functionality.

## 🚀 Quick Start (Minimum Required)

To get the app running with AI features, you only need **ONE** API key:

### Option 1: Gemini (Recommended for Development)
1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key
5. Open `backend/.env` and replace:
   ```env
   GEMINI_API_KEY=your_gemini_key_here
   ```
   with your actual key:
   ```env
   GEMINI_API_KEY=AIzaSyD...your_actual_key
   ```

**Free Tier**: 15 requests/min, 1M tokens/day (plenty for development)

### Option 2: Groq (Alternative - Fast Inference)
1. Go to: https://console.groq.com
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Open `backend/.env` and:
   - Change `LLM_PROVIDER=gemini` to `LLM_PROVIDER=groq`
   - Replace `GROQ_API_KEY=your_groq_key_here` with your actual key

**Free Tier**: Fast inference with Llama models

---

## 📦 Optional: Supabase (Production Persistence)

For development, the app uses in-memory storage. For production, add Supabase:

1. Go to: https://supabase.com
2. Create a free account
3. Create a new project
4. Go to: Project Settings → API
5. Copy:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **Anon/Public Key** (starts with `eyJ...`)
6. Open `backend/.env` and replace:
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

**Free Tier**: 500MB database, 50k rows, 2GB bandwidth/month

---

## 🔗 Optional: OAuth (Social Media Connections)

To enable Instagram, LinkedIn, and Twitter connections:

### Instagram OAuth
1. Go to: https://developers.facebook.com/apps/
2. Create a new app (select "Business" type)
3. Add Instagram Basic Display product
4. Configure OAuth redirect URI: `http://localhost:3000/auth/callback/instagram`
5. Copy Client ID and Client Secret
6. Add to `backend/.env`:
   ```env
   INSTAGRAM_CLIENT_ID=your_instagram_client_id
   INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
   INSTAGRAM_REDIRECT_URI=http://localhost:3000/auth/callback/instagram
   ```

### LinkedIn OAuth
1. Go to: https://www.linkedin.com/developers/apps
2. Create a new app
3. Add "Sign In with LinkedIn" product
4. Configure OAuth redirect URI: `http://localhost:3000/auth/callback/linkedin`
5. Copy Client ID and Client Secret
6. Add to `backend/.env`:
   ```env
   LINKEDIN_CLIENT_ID=your_linkedin_client_id
   LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
   LINKEDIN_REDIRECT_URI=http://localhost:3000/auth/callback/linkedin
   ```

### Twitter OAuth
1. Go to: https://developer.twitter.com/en/portal/dashboard
2. Create a new project and app
3. Enable OAuth 2.0
4. Configure callback URI: `http://localhost:3000/auth/callback/twitter`
5. Copy Client ID and Client Secret
6. Add to `backend/.env`:
   ```env
   TWITTER_CLIENT_ID=your_twitter_client_id
   TWITTER_CLIENT_SECRET=your_twitter_client_secret
   TWITTER_REDIRECT_URI=http://localhost:3000/auth/callback/twitter
   ```

---

## ☁️ Optional: AWS (Production Deployment)

Only needed when deploying to AWS Lambda/API Gateway:

1. Go to: https://console.aws.amazon.com/iam/
2. Create a new IAM user with programmatic access
3. Attach policies:
   - `AmazonS3FullAccess`
   - `AmazonDynamoDBFullAccess`
   - `AmazonBedrockFullAccess`
   - `AWSLambdaFullAccess`
   - `AmazonAPIGatewayAdministrator`
4. Copy Access Key ID and Secret Access Key
5. Add to `backend/.env`:
   ```env
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   AWS_REGION=us-east-1
   ```

---

## 🔐 Security Best Practices

### For Development
- ✅ Keep `.env` file in `backend/` directory
- ✅ Never commit `.env` to git (already in `.gitignore`)
- ✅ Use free tier API keys for testing

### For Production
1. **Generate a secure SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Add to `.env`:
   ```env
   SECRET_KEY=your_generated_secret_key
   ```

2. **Use AWS Secrets Manager** for sensitive keys:
   - Store OAuth secrets in AWS Secrets Manager
   - Reference them in Lambda environment variables
   - Never hardcode secrets in code

3. **Rotate keys regularly**:
   - Rotate API keys every 90 days
   - Monitor usage in provider dashboards
   - Set up billing alerts

---

## ✅ Verification Steps

After adding your API keys:

### 1. Check .env file
```bash
cd backend
cat .env | grep -v "your_.*_here"
```
You should see your actual keys (not placeholder text).

### 2. Restart backend
```bash
# Stop current backend (Ctrl+C)
cd backend
source venv/bin/activate
python app.py
```

### 3. Test API connection
Open browser to: http://127.0.0.1:5001/api/health

You should see:
```json
{
  "status": "healthy",
  "llm_provider": "gemini",  // or "groq"
  "posts_in_chromadb": 0,
  "supabase_connected": false  // true if Supabase configured
}
```

### 4. Test AI features
1. Go to: http://localhost:3000
2. Navigate to "Content Ideation"
3. Click "Generate Ideas"
4. If you see AI-generated content ideas → ✅ Success!

---

## 🐛 Troubleshooting

### "No LLM API Key found"
**Cause**: API key not set or invalid format  
**Fix**: 
- Check `.env` file has actual key (not placeholder)
- Ensure no extra spaces around the key
- Verify key is valid in provider dashboard

### "API key invalid" or "401 Unauthorized"
**Cause**: Wrong API key or expired key  
**Fix**:
- Regenerate key in provider dashboard
- Copy new key to `.env`
- Restart backend

### "Rate limit exceeded"
**Cause**: Too many requests to free tier API  
**Fix**:
- Wait a few minutes
- Upgrade to paid tier
- Switch to alternative provider (Gemini ↔ Groq)

### Backend still shows "mocked mode"
**Cause**: `.env` file not loaded  
**Fix**:
- Ensure `.env` is in `backend/` directory (not root)
- Restart backend with virtual environment activated
- Check file permissions: `chmod 600 backend/.env`

---

## 📊 Cost Estimation

### Development (Free Tier)
- **Gemini**: Free (15 req/min, 1M tokens/day)
- **Groq**: Free (fast inference)
- **Supabase**: Free (500MB, 50k rows)
- **Total**: $0/month

### Production (AWS Serverless)
Based on 1 brand, 100 posts/month:
- **Lambda**: ~$0.20/month
- **API Gateway**: ~$0.35/month
- **DynamoDB**: ~$0.25/month (on-demand)
- **OpenSearch Serverless**: ~$0.24/month (750 OCU-hours free tier)
- **S3**: ~$0.02/month
- **Bedrock (Claude 3 Haiku)**: ~$0.10/month
- **Total**: ~$1.16/month per brand

See `aws-architecture-plan.md` for detailed cost breakdown.

---

## 🎯 What You Need Right Now

**Minimum to get started**:
1. ✅ One LLM API key (Gemini or Groq) - **5 minutes**
2. ✅ Restart backend - **30 seconds**
3. ✅ Test in browser - **1 minute**

**Total time**: ~7 minutes to full AI functionality!

**Optional for later**:
- Supabase (when you need persistence)
- OAuth (when you want social media posting)
- AWS (when you deploy to production)

---

## 📞 Support

- **Gemini Issues**: https://ai.google.dev/gemini-api/docs
- **Groq Issues**: https://console.groq.com/docs
- **Supabase Issues**: https://supabase.com/docs
- **AWS Issues**: https://docs.aws.amazon.com/

---

**Ready to go?** Just add your Gemini or Groq API key to `backend/.env` and restart the backend! 🚀
