# AWS Amplify Deployment Guide

## 🚀 Quick Deployment to AWS Amplify

### Option 1: Environment Variables (Recommended - Secure)

AWS Amplify has built-in support for environment variables. Your secrets stay secure and never go into git.

#### Step 1: Deploy to Amplify
1. Go to: https://console.aws.amazon.com/amplify/
2. Click "New app" → "Host web app"
3. Connect your GitHub repository: `Sukheshkanna13/instamedia-v2`
4. Select branch: `main`

#### Step 2: Configure Build Settings
Amplify will auto-detect your app. Use this build configuration:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/dist
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
backend:
  phases:
    build:
      commands:
        - cd backend
        - pip install -r requirements.txt
```

#### Step 3: Add Environment Variables in Amplify Console
1. In Amplify Console, go to: **App settings** → **Environment variables**
2. Click **Manage variables**
3. Add these variables:

```
LLM_PROVIDER = gemini
GEMINI_API_KEY = AIzaSyDxtbnNkNmDuMPwNcstY1SAajYxjBC58Ek
GROQ_API_KEY = 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
SUPABASE_URL = https://rlirzjjecrbcfxzwdftp.supabase.co
SUPABASE_ANON_KEY = sb_publishable_O4fjB_bL9UNwIM5gZxFDew_Z2pAxaI-
FLASK_ENV = production
PORT = 5001
```

4. Click **Save**

#### Step 4: Deploy
Click **Save and deploy**

✅ Your secrets are now secure in AWS and never in git!

---

## Option 2: Commit .env for Prototype (Quick & Simple)

If you want the absolute simplest deployment for a prototype, you can commit the .env file.

⚠️ **WARNING**: Only do this for prototypes, never for production with real user data!

### Steps:

1. Remove .env from .gitignore
2. Commit and push .env file
3. Deploy to Amplify

I can help you do this if you want the quick prototype approach.

---

## Option 3: Use AWS Secrets Manager (Most Secure)

For production, use AWS Secrets Manager:

```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# In app.py
secrets = get_secret('instamedia-ai-secrets')
GEMINI_API_KEY = secrets['GEMINI_API_KEY']
```

---

## Recommended Approach for Your Prototype

**Use Option 1 (Amplify Environment Variables)**

Why?
- ✅ Simple to set up (5 minutes)
- ✅ Secrets stay secure
- ✅ Easy to update keys later
- ✅ No code changes needed
- ✅ Works immediately
- ✅ Free on AWS Amplify

**Time to deploy**: ~10 minutes total

---

## Alternative: Vercel/Netlify (Even Simpler)

If you want the absolute easiest deployment:

### Vercel (Frontend + Backend)
1. Go to: https://vercel.com
2. Import your GitHub repo
3. Add environment variables in Vercel dashboard
4. Deploy (automatic)

### Netlify (Frontend only)
1. Go to: https://netlify.com
2. Import your GitHub repo
3. Add environment variables
4. Deploy

Both have free tiers and are simpler than AWS Amplify.

---

## What Do You Want?

**Choose one**:

1. **AWS Amplify with Environment Variables** (Recommended - Secure)
   - I'll create the amplify.yml config file
   - You add env vars in AWS console
   - Deploy

2. **Commit .env to Git** (Quick prototype - Less secure)
   - I'll remove .env from .gitignore
   - Commit and push .env
   - Deploy anywhere

3. **Vercel/Netlify** (Easiest - Recommended for prototypes)
   - I'll create deployment configs
   - You connect GitHub
   - Deploy in 5 minutes

Let me know which approach you prefer!
