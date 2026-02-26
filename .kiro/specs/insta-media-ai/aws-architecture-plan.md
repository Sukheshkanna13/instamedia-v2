# AWS Architecture Plan: InstaMedia AI — Emotional Signal Engine

## AWS AI for Bharat Hackathon 2025 | Serverless Production Architecture

## Executive Summary

This document outlines the AWS serverless architecture for InstaMedia AI's Emotional Signal Engine. The architecture transforms the prototype (Flask + ChromaDB + Supabase) into a production-ready, scalable system using AWS managed services while maintaining the core innovation: emotion-driven content intelligence through RAG (Retrieval-Augmented Generation).

## Architecture Philosophy

**Serverless-First**: Zero infrastructure management, pay-per-use pricing, automatic scaling
**Event-Driven**: Asynchronous workflows triggered by user actions and scheduled events
**AI-Native**: Amazon Bedrock for LLM reasoning, Amazon Comprehend for content safety
**Cost-Optimized**: Free tier for prototype, predictable scaling for production

## High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                            │
│  React + TypeScript (CloudFront + S3 Static Hosting)            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API Gateway (REST)                           │
│  Authentication: Cognito JWT | Rate Limiting | Request Routing  │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Lambda:      │  │ Lambda:      │  │ Lambda:      │
│ Brand DNA    │  │ ESG Engine   │  │ Creative     │
│ Manager      │  │ Orchestrator │  │ Studio       │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data & AI Layer                             │
│  DynamoDB | S3 | OpenSearch Serverless | Bedrock | Comprehend   │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Orchestration & Automation                      │
│  Step Functions | EventBridge Scheduler | SQS | SNS             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components Mapping

### Prototype → AWS Migration Path

| Prototype Component | AWS Service | Rationale |
|---------------------|-------------|-----------|
| Flask Backend | AWS Lambda + API Gateway | Serverless, auto-scaling, pay-per-request |
| ChromaDB (Vector DB) | Amazon OpenSearch Serverless (Vector Engine) | Managed vector search, k-NN, cosine similarity |
| Supabase PostgreSQL | Amazon DynamoDB | Serverless NoSQL, single-digit ms latency |
| Supabase Storage | Amazon S3 | Object storage for logos, CSVs, media assets |
| sentence-transformers | Amazon Bedrock Titan Embeddings | Managed embeddings API, no local compute |
| Gemini/Groq LLM | Amazon Bedrock (Claude 3 Haiku) | Enterprise LLM, content safety, low latency |
| Manual Scheduling | Amazon EventBridge Scheduler | Cron-based triggers for content publishing |
| Background Jobs | AWS Step Functions + SQS | Orchestrate multi-step workflows |

---

## Detailed Component Architecture

### 1. Frontend Layer

**Service**: Amazon CloudFront + S3 Static Website Hosting

**Architecture**:
```
User Browser → CloudFront (CDN) → S3 Bucket (React Build)
                    ↓
              WAF (Optional: DDoS protection)
```

**Implementation**:
- React + TypeScript + Vite build artifacts deployed to S3
- CloudFront distribution with custom domain (Route 53)
- HTTPS enforced via ACM (AWS Certificate Manager)
- Cache invalidation on deployment via CloudFront API

**Cost**: Free tier: 1TB data transfer out, 10M requests/month

---

### 2. API Gateway Layer

**Service**: Amazon API Gateway (REST API)

**Architecture**:
```
CloudFront → API Gateway → Lambda Authorizer (Cognito JWT)
                              ↓
                    Route to Lambda Functions
```

**Endpoints**:
- `POST /api/brand-dna` → Lambda: SaveBrandDNA
- `POST /api/esg/upload` → Lambda: IngestHistoricalPosts
- `POST /api/ideate` → Lambda: GenerateIdeas
- `POST /api/studio/generate` → Lambda: GenerateContent
- `POST /api/studio/score` → Lambda: EmotionalAligner
- `GET /api/calendar` → Lambda: GetScheduledPosts
- `POST /api/calendar/schedule` → Lambda: SchedulePost
- `GET /api/dashboard` → Lambda: GetDashboardMetrics

**Features**:
- Request validation (JSON schema)
- Rate limiting per API key (1000 req/hour for free tier)
- CORS configuration for frontend domain
- CloudWatch logging for all requests

**Cost**: Free tier: 1M API calls/month

---

### 3. Compute Layer: AWS Lambda Functions

**Runtime**: Python 3.11 (for ML libraries compatibility)

#### Lambda Function: SaveBrandDNA
**Trigger**: API Gateway POST /api/brand-dna
**Purpose**: Store brand identity (mission, tone, colors, banned words)
**Flow**:
1. Validate input schema
2. Store to DynamoDB table `BrandProfiles`
3. Upload logo to S3 bucket `instamedia-brand-assets`
4. Return brand_id

**Memory**: 512 MB | **Timeout**: 10s | **Concurrency**: 10

---

#### Lambda Function: IngestHistoricalPosts
**Trigger**: API Gateway POST /api/esg/upload
**Purpose**: Build Emotional Signal Graph from CSV upload
**Flow**:
1. Parse CSV from S3 (uploaded via pre-signed URL)
2. Calculate ERS for each post: `log1p((likes×0.2)+(comments×0.5)+(shares×0.8))×10`
3. Generate embeddings via Bedrock Titan Embeddings API
4. Store vectors in OpenSearch Serverless (k-NN index)
5. Store metadata in DynamoDB table `ESGPosts`
6. Calculate baseline EPM (centroid of top 20% posts)
7. Store EPM in DynamoDB table `BrandProfiles`

**Memory**: 1024 MB | **Timeout**: 300s | **Concurrency**: 5
**Async**: Use SQS queue for batch processing if CSV > 100 posts

---

#### Lambda Function: GenerateIdeas (Ideation Agent)
**Trigger**: API Gateway POST /api/ideate
**Purpose**: Generate content ideas conditioned on ESG + Brand DNA
**Flow**:
1. Retrieve Brand DNA from DynamoDB
2. Query OpenSearch for top 5 posts similar to focus area (k-NN search)
3. Construct prompt with Brand DNA + reference posts
4. Call Bedrock Claude 3 Haiku for idea generation
5. Parse response into structured JSON (5 ideas)
6. Return ideas with reference post citations

**Memory**: 512 MB | **Timeout**: 30s | **Concurrency**: 20

**Bedrock Prompt Template**:
```
You are a content strategist for {brand_name}.

Brand Mission: {mission}
Brand Tone: {tone_descriptors}
Focus Area: {focus_area}

Top-performing posts from this brand's history:
{reference_posts}

Generate 5 content ideas that match this brand's emotional signature.
For each idea, provide: title, hook, emotional_angle, platform, predicted_ERS.
```

---

#### Lambda Function: GenerateContent (Creative Studio)
**Trigger**: API Gateway POST /api/studio/generate
**Purpose**: Generate full post with hashtags, CTA, image brief
**Flow**:
1. Retrieve Brand DNA from DynamoDB
2. Construct prompt with Brand DNA + topic/idea
3. Call Bedrock Claude 3 Haiku for content generation
4. Pass generated text through Comprehend Toxicity Detection
5. If toxic content detected, regenerate with adjusted parameters
6. Check for banned words from Brand DNA
7. Return generated content

**Memory**: 512 MB | **Timeout**: 30s | **Concurrency**: 20

---

#### Lambda Function: EmotionalAligner (The Bouncer Agent)
**Trigger**: API Gateway POST /api/studio/score
**Purpose**: Score draft content against ESG for emotional resonance
**Flow**:
1. Generate embedding for draft post via Bedrock Titan Embeddings
2. Query OpenSearch for top 3 similar historical posts (k-NN)
3. Calculate combined score: `(semantic_sim × 0.4) + (ERS/100 × 0.6)`
4. Analyze emotional gaps using Bedrock Claude 3 Haiku
5. Generate verdict, what_works, what_is_missing, rewrite_suggestion
6. Return JSON response with score + explainability

**Memory**: 512 MB | **Timeout**: 10s | **Concurrency**: 50

**OpenSearch Query**:
```json
{
  "size": 3,
  "query": {
    "knn": {
      "embedding_vector": {
        "vector": [0.123, 0.456, ...],
        "k": 3
      }
    }
  }
}
```

---

#### Lambda Function: SchedulePost
**Trigger**: API Gateway POST /api/calendar/schedule
**Purpose**: Schedule post for future publishing
**Flow**:
1. Store post to DynamoDB table `ScheduledPosts`
2. Create EventBridge Scheduler rule for scheduled_time
3. Target: Lambda PublishPost with post_id as input
4. Return confirmation

**Memory**: 256 MB | **Timeout**: 5s | **Concurrency**: 10

---

#### Lambda Function: PublishPost
**Trigger**: EventBridge Scheduler (scheduled time)
**Purpose**: Publish approved content to social media platforms
**Flow**:
1. Retrieve post from DynamoDB `ScheduledPosts`
2. Authenticate with platform API (OAuth tokens from Secrets Manager)
3. Format content for target platform (Instagram/LinkedIn/Twitter)
4. Call platform API to publish
5. Update post status to "published" in DynamoDB
6. Send SNS notification to user (success/failure)

**Memory**: 512 MB | **Timeout**: 60s | **Concurrency**: 5

---

#### Lambda Function: UpdateESG
**Trigger**: API Gateway POST /api/esg/update (manual engagement data entry)
**Purpose**: Continuous learning from published post performance
**Flow**:
1. Calculate actual ERS from engagement data
2. Generate embedding via Bedrock Titan Embeddings
3. Store in OpenSearch Serverless
4. Update DynamoDB `ESGPosts` with actual_ERS
5. Recalculate rolling EPM (last 30 posts)
6. Check for brand drift (cosine distance > 0.15)
7. If drift detected, send SNS alert

**Memory**: 512 MB | **Timeout**: 30s | **Concurrency**: 10

---

#### Lambda Function: DetectBrandDrift
**Trigger**: EventBridge Scheduler (daily at 2 AM IST)
**Purpose**: Proactive brand drift monitoring
**Flow**:
1. Retrieve baseline EPM and rolling EPM from DynamoDB
2. Calculate cosine distance
3. If distance > 0.15, generate drift report
4. Store drift event in DynamoDB `DriftEvents`
5. Send SNS notification to user
6. Update dashboard alert flag

**Memory**: 256 MB | **Timeout**: 10s | **Concurrency**: 1

---

### 4. Data Layer

#### Amazon DynamoDB Tables

**Table: BrandProfiles**
```
Partition Key: brand_id (String)
Attributes:
  - brand_name (String)
  - mission (String)
  - tone_descriptors (List<String>)
  - colors (List<String>)
  - banned_words (List<String>)
  - logo_s3_url (String)
  - baseline_epm (List<Float>) // 384-dim vector
  - rolling_epm (List<Float>)
  - esg_post_count (Number)
  - created_at (String)
  - updated_at (String)

GSI: None
Capacity: On-Demand (pay per request)
```

**Table: ESGPosts**
```
Partition Key: brand_id (String)
Sort Key: post_id (String)
Attributes:
  - post_text (String)
  - platform (String)
  - post_date (String)
  - likes (Number)
  - comments (Number)
  - shares (Number)
  - ers (Number) // Emotional Resonance Score
  - predicted_ers (Number) // From Emotional Aligner
  - embedding_indexed (Boolean) // OpenSearch sync status
  - created_at (String)

GSI: brand_id-ers-index (for top-performing posts query)
Capacity: On-Demand
```

**Table: ScheduledPosts**
```
Partition Key: brand_id (String)
Sort Key: post_id (String)
Attributes:
  - content (String)
  - platform (String)
  - scheduled_time (String) // ISO 8601
  - status (String) // draft | scheduled | published | failed
  - resonance_score (Number)
  - image_s3_url (String)
  - eventbridge_rule_name (String)
  - created_at (String)
  - published_at (String)

GSI: brand_id-scheduled_time-index (for calendar queries)
Capacity: On-Demand
```

**Table: DriftEvents**
```
Partition Key: brand_id (String)
Sort Key: timestamp (String)
Attributes:
  - drift_magnitude (Number)
  - baseline_epm (List<Float>)
  - rolling_epm (List<Float>)
  - emotional_signals_changed (List<String>)
  - acknowledged (Boolean)
  - created_at (String)

Capacity: On-Demand
```

---

#### Amazon OpenSearch Serverless (Vector Engine)

**Collection**: instamedia-esg-vectors

**Index Mapping**:
```json
{
  "mappings": {
    "properties": {
      "brand_id": { "type": "keyword" },
      "post_id": { "type": "keyword" },
      "post_text": { "type": "text" },
      "embedding_vector": {
        "type": "knn_vector",
        "dimension": 1024,
        "method": {
          "name": "hnsw",
          "engine": "faiss",
          "parameters": {
            "ef_construction": 512,
            "m": 16
          }
        }
      },
      "ers": { "type": "float" },
      "platform": { "type": "keyword" },
      "post_date": { "type": "date" }
    }
  }
}
```

**Why OpenSearch over ChromaDB**:
- Managed service (no server maintenance)
- Native k-NN search with FAISS/NMSLIB
- Scales automatically with data volume
- Integrated with AWS IAM for security
- Sub-100ms query latency at scale

**Cost**: Free tier: 750 OCU-hours/month (sufficient for prototype)

---

#### Amazon S3 Buckets

**Bucket: instamedia-brand-assets**
- Purpose: Store brand logos, uploaded CSVs, generated images
- Structure:
  ```
  /{brand_id}/logo.png
  /{brand_id}/uploads/{timestamp}.csv
  /{brand_id}/generated/{post_id}.png
  ```
- Lifecycle Policy: Delete uploads/ after 30 days
- Encryption: SSE-S3 (AES-256)

**Bucket: instamedia-frontend**
- Purpose: Host React static website
- Public read access via CloudFront OAI
- Versioning enabled for rollback

**Cost**: Free tier: 5GB storage, 20k GET requests, 2k PUT requests/month

---

### 5. AI & ML Layer

#### Amazon Bedrock

**Model: Claude 3 Haiku**
- Use Case: Content generation, idea generation, emotional analysis
- Input: Text prompts with Brand DNA + ESG context
- Output: Structured JSON responses
- Latency: ~2-3 seconds for 500 tokens
- Cost: $0.25 per 1M input tokens, $1.25 per 1M output tokens

**Model: Amazon Titan Embeddings G1 - Text**
- Use Case: Generate 1024-dim embeddings for posts
- Input: Post text (max 8k tokens)
- Output: Float array [1024]
- Latency: ~200ms per request
- Cost: $0.0001 per 1k tokens

**Bedrock API Call Pattern**:
```python
import boto3

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

# Content Generation
response = bedrock.invoke_model(
    modelId='anthropic.claude-3-haiku-20240307-v1:0',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{
            "role": "user",
            "content": prompt
        }]
    })
)

# Embeddings
response = bedrock.invoke_model(
    modelId='amazon.titan-embed-text-v1',
    body=json.dumps({
        "inputText": post_text
    })
)
```

---

#### Amazon Comprehend

**Service**: Real-time Toxicity Detection

**API Call**:
```python
comprehend = boto3.client('comprehend', region_name='us-east-1')

response = comprehend.detect_toxic_content(
    TextSegments=[{'Text': generated_content}],
    LanguageCode='en'
)

# Response structure
{
    'ResultList': [{
        'Toxicity': 0.85,  # 0-1 score
        'Labels': [
            {'Name': 'PROFANITY', 'Score': 0.92},
            {'Name': 'HATE_SPEECH', 'Score': 0.15}
        ]
    }]
}
```

**Threshold**: Reject content if Toxicity > 0.7

**Cost**: $0.0001 per 100 characters (first 50k units free per month)

---

### 6. Orchestration & Automation Layer

#### AWS Step Functions

**State Machine: ESG Ingestion Workflow**

**Purpose**: Orchestrate batch processing of historical posts

**Flow**:
```json
{
  "Comment": "ESG Ingestion Pipeline",
  "StartAt": "ParseCSV",
  "States": {
    "ParseCSV": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT:function:ParseCSV",
      "Next": "MapPosts"
    },
    "MapPosts": {
      "Type": "Map",
      "ItemsPath": "$.posts",
      "MaxConcurrency": 10,
      "Iterator": {
        "StartAt": "CalculateERS",
        "States": {
          "CalculateERS": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:REGION:ACCOUNT:function:CalculateERS",
            "Next": "GenerateEmbedding"
          },
          "GenerateEmbedding": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:REGION:ACCOUNT:function:GenerateEmbedding",
            "Next": "StoreInOpenSearch"
          },
          "StoreInOpenSearch": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:REGION:ACCOUNT:function:StoreVector",
            "End": true
          }
        }
      },
      "Next": "CalculateEPM"
    },
    "CalculateEPM": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT:function:CalculateEPM",
      "End": true
    }
  }
}
```

**Trigger**: S3 event (CSV upload) → EventBridge → Step Functions

**Cost**: Free tier: 4,000 state transitions/month

---

#### Amazon EventBridge Scheduler

**Schedule: Daily Brand Drift Check**
```
Name: daily-drift-check
Schedule: cron(0 20 * * ? *)  # 2 AM IST daily
Target: Lambda DetectBrandDrift
Input: { "scan_all_brands": true }
```

**Schedule: Content Publishing (Dynamic)**
```
Name: publish-post-{post_id}
Schedule: at({scheduled_time})  # One-time schedule
Target: Lambda PublishPost
Input: { "post_id": "abc123", "brand_id": "xyz789" }
```

**Cost**: Free tier: 14M invocations/month

---

#### Amazon SQS (Simple Queue Service)

**Queue: esg-ingestion-queue**
- Purpose: Decouple CSV upload from processing
- Type: Standard queue
- Visibility Timeout: 300s
- Dead Letter Queue: esg-ingestion-dlq (for failed posts)

**Flow**:
```
S3 Upload → EventBridge → Lambda (ParseCSV) → SQS (batch messages)
                                                  ↓
                                    Lambda (ProcessPost) polls queue
```

**Cost**: Free tier: 1M requests/month

---

#### Amazon SNS (Simple Notification Service)

**Topic: brand-alerts**
- Purpose: Send notifications to users
- Subscriptions:
  - Email: user@example.com
  - SMS: +91-XXXXXXXXXX (optional)
  - Lambda: SendInAppNotification

**Message Types**:
- Brand drift detected
- Content published successfully
- Content publishing failed
- ESG ingestion complete

**Cost**: Free tier: 1,000 email notifications/month

---

### 7. Security & Identity Layer

#### Amazon Cognito

**User Pool**: instamedia-users

**Features**:
- Email/password authentication
- JWT token generation (access + refresh)
- MFA optional (SMS/TOTP)
- Custom attributes: brand_id, subscription_tier

**User Flow**:
```
1. User signs up → Cognito creates user
2. Email verification → Cognito confirms user
3. User logs in → Cognito returns JWT tokens
4. Frontend stores tokens in localStorage
5. API Gateway validates JWT on each request
```

**Cost**: Free tier: 50,000 MAUs (Monthly Active Users)

---

#### AWS Secrets Manager

**Secrets Stored**:
- Social media OAuth tokens (Instagram, LinkedIn, Twitter)
- API keys for external services
- Database credentials (if using RDS in future)

**Rotation**: Automatic rotation every 90 days for OAuth tokens

**Cost**: $0.40 per secret per month

---

#### IAM Roles & Policies

**Role: LambdaExecutionRole**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/BrandProfiles"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::instamedia-brand-assets/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "comprehend:DetectToxicContent"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "es:ESHttpPost",
        "es:ESHttpGet"
      ],
      "Resource": "arn:aws:es:*:*:domain/instamedia-esg-vectors/*"
    }
  ]
}
```

---

### 8. Monitoring & Observability

#### Amazon CloudWatch

**Metrics to Track**:
- Lambda invocation count, duration, errors
- API Gateway 4xx/5xx errors, latency
- DynamoDB read/write capacity units
- OpenSearch query latency
- Bedrock API call count, token usage

**Alarms**:
- Lambda error rate > 5% → SNS alert
- API Gateway latency > 3s → SNS alert
- DynamoDB throttling events → SNS alert

**Logs**:
- All Lambda functions log to CloudWatch Logs
- Retention: 7 days (prototype), 30 days (production)

**Cost**: Free tier: 5GB ingestion, 5GB storage

---

#### AWS X-Ray

**Purpose**: Distributed tracing for debugging

**Integration**:
- Enable X-Ray on all Lambda functions
- Trace API Gateway → Lambda → DynamoDB/OpenSearch/Bedrock

**Use Case**: Identify bottlenecks in ESG query pipeline

**Cost**: Free tier: 100k traces/month

---

## End-to-End Workflow Examples

### Workflow 1: Brand Onboarding + ESG Construction

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: User Creates Brand Profile                              │
└─────────────────────────────────────────────────────────────────┘
User → CloudFront → API Gateway → Lambda: SaveBrandDNA
                                      ↓
                            DynamoDB: BrandProfiles (insert)
                                      ↓
                            S3: Upload logo
                                      ↓
                            Return: brand_id

┌─────────────────────────────────────────────────────────────────┐
│ Step 2: User Uploads Historical Posts CSV                       │
└─────────────────────────────────────────────────────────────────┘
User → CloudFront → API Gateway → Lambda: GeneratePresignedURL
                                      ↓
                            S3: Upload CSV to /uploads/
                                      ↓
                            EventBridge: S3 ObjectCreated event
                                      ↓
                            Step Functions: ESG Ingestion Workflow
                                      ↓
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
          Lambda: ParseCSV                    Lambda: CalculateERS
                    ↓                                   ↓
          SQS: Post messages              Bedrock: Generate embeddings
                    ↓                                   ↓
          Lambda: ProcessPost             OpenSearch: Store vectors
                    ↓                                   ↓
          DynamoDB: ESGPosts              DynamoDB: Update metadata
                                                        ↓
                                          Lambda: CalculateEPM
                                                        ↓
                                          DynamoDB: Store baseline EPM
                                                        ↓
                                          SNS: Notify user "ESG Ready"
```

---

### Workflow 2: Content Ideation → Generation → Scoring → Scheduling

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Generate Content Ideas                                  │
└─────────────────────────────────────────────────────────────────┘
User → API Gateway → Lambda: GenerateIdeas
                          ↓
                DynamoDB: Get Brand DNA
                          ↓
                OpenSearch: k-NN query (top 5 posts)
                          ↓
                Bedrock Claude 3 Haiku: Generate 5 ideas
                          ↓
                Return: Ideas with reference posts

┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Generate Full Post                                      │
└─────────────────────────────────────────────────────────────────┘
User selects idea → API Gateway → Lambda: GenerateContent
                                      ↓
                            DynamoDB: Get Brand DNA
                                      ↓
                            Bedrock Claude 3 Haiku: Generate post
                                      ↓
                            Comprehend: Toxicity check
                                      ↓
                            Check banned words
                                      ↓
                            Return: Generated content

┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Score Content (Emotional Aligner)                       │
└─────────────────────────────────────────────────────────────────┘
User edits draft → API Gateway → Lambda: EmotionalAligner
                                      ↓
                            Bedrock Titan: Generate embedding
                                      ↓
                            OpenSearch: k-NN query (top 3 posts)
                                      ↓
                            Calculate combined score
                                      ↓
                            Bedrock Claude 3 Haiku: Analyze gaps
                                      ↓
                            Return: Score + feedback + references

┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Schedule Post                                           │
└─────────────────────────────────────────────────────────────────┘
User clicks "Schedule" → API Gateway → Lambda: SchedulePost
                                          ↓
                                DynamoDB: ScheduledPosts (insert)
                                          ↓
                                EventBridge Scheduler: Create rule
                                          ↓
                                Return: Confirmation

┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Publish Post (Scheduled Time)                           │
└─────────────────────────────────────────────────────────────────┘
EventBridge Scheduler → Lambda: PublishPost
                            ↓
                  DynamoDB: Get post details
                            ↓
                  Secrets Manager: Get OAuth token
                            ↓
                  Platform API: Publish post
                            ↓
                  DynamoDB: Update status to "published"
                            ↓
                  SNS: Notify user
```

---

### Workflow 3: Post-Publish Learning & Brand Drift Detection

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: User Enters Engagement Data                             │
└─────────────────────────────────────────────────────────────────┘
User → API Gateway → Lambda: UpdateESG
                          ↓
                DynamoDB: Get post details
                          ↓
                Calculate actual ERS
                          ↓
                Bedrock Titan: Generate embedding
                          ↓
                OpenSearch: Store vector with actual ERS
                          ↓
                DynamoDB: Update ESGPosts with actual_ERS
                          ↓
                Calculate prediction error
                          ↓
                DynamoDB: Log prediction accuracy
                          ↓
                Recalculate rolling EPM (last 30 posts)
                          ↓
                Calculate drift (cosine distance)
                          ↓
                IF drift > 0.15:
                    DynamoDB: Store DriftEvent
                    SNS: Alert user
                          ↓
                Return: Confirmation

┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Daily Automated Drift Check                             │
└─────────────────────────────────────────────────────────────────┘
EventBridge Scheduler (2 AM IST) → Lambda: DetectBrandDrift
                                        ↓
                              DynamoDB: Get all brands
                                        ↓
                              For each brand:
                                  Get baseline EPM
                                  Get rolling EPM
                                  Calculate cosine distance
                                        ↓
                              IF drift > 0.15:
                                  DynamoDB: Store DriftEvent
                                  SNS: Alert user
                                  Dashboard: Set alert flag
```

---

## Cost Estimation

### Prototype Phase (First 3 Months)

**Assumptions**:
- 10 brands
- 100 posts per brand in ESG
- 50 content generations per brand per month
- 200 API calls per brand per month

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 20,000 invocations, 512MB avg | Free tier |
| API Gateway | 20,000 requests | Free tier |
| DynamoDB | 10k reads, 5k writes | Free tier |
| OpenSearch Serverless | 750 OCU-hours | Free tier |
| S3 | 5GB storage, 10k requests | Free tier |
| Bedrock Claude 3 Haiku | 5M input tokens, 2M output tokens | $1.25 + $2.50 = $3.75 |
| Bedrock Titan Embeddings | 10M tokens | $1.00 |
| Comprehend | 50k units | Free tier |
| CloudFront | 1TB transfer | Free tier |
| Cognito | 50 MAUs | Free tier |
| EventBridge | 10k invocations | Free tier |
| SNS | 1k emails | Free tier |

**Total Monthly Cost**: ~$5/month (Bedrock only)

---

### Production Phase (After Launch)

**Assumptions**:
- 1,000 brands
- 500 posts per brand in ESG
- 200 content generations per brand per month
- 2,000 API calls per brand per month

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Lambda | 2M invocations, 512MB avg | $8.00 |
| API Gateway | 2M requests | $3.50 |
| DynamoDB | 1M reads, 500k writes | $12.50 |
| OpenSearch Serverless | 2,000 OCU-hours | $480.00 |
| S3 | 500GB storage, 1M requests | $15.00 |
| Bedrock Claude 3 Haiku | 500M input, 200M output | $375.00 |
| Bedrock Titan Embeddings | 1B tokens | $100.00 |
| Comprehend | 5M units | $50.00 |
| CloudFront | 10TB transfer | $85.00 |
| Cognito | 5,000 MAUs | $27.50 |
| EventBridge | 1M invocations | $1.00 |
| SNS | 100k emails | $2.00 |

**Total Monthly Cost**: ~$1,159/month for 1,000 brands
**Cost per Brand**: ~$1.16/month

---

## Deployment Strategy

### Phase 1: Prototype (Weeks 1-2)

**Goal**: Validate core ESG + Emotional Aligner functionality

**Services to Deploy**:
1. Lambda functions: SaveBrandDNA, IngestHistoricalPosts, GenerateIdeas, GenerateContent, EmotionalAligner
2. DynamoDB tables: BrandProfiles, ESGPosts
3. OpenSearch Serverless collection
4. API Gateway with Cognito authorizer
5. S3 buckets for assets
6. CloudFront + S3 for frontend

**Deployment Tool**: AWS SAM (Serverless Application Model)

**Infrastructure as Code**:
```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  SaveBrandDNAFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: handlers/brand_dna.save
      Runtime: python3.11
      MemorySize: 512
      Timeout: 10
      Environment:
        Variables:
          BRAND_TABLE: !Ref BrandProfilesTable
      Events:
        Api:
          Type: Api
          Properties:
            Path: /api/brand-dna
            Method: POST
            Auth:
              Authorizer: CognitoAuthorizer

  BrandProfilesTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: BrandProfiles
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: brand_id
          AttributeType: S
      KeySchema:
        - AttributeName: brand_id
          KeyType: HASH
```

**Deployment Commands**:
```bash
sam build
sam deploy --guided --region us-east-1
```

---

### Phase 2: Full Feature Set (Weeks 3-4)

**Additional Services**:
1. Step Functions for ESG ingestion
2. EventBridge Scheduler for publishing
3. Lambda: SchedulePost, PublishPost, UpdateESG, DetectBrandDrift
4. SQS queues for async processing
5. SNS topics for notifications
6. Secrets Manager for OAuth tokens

---

### Phase 3: Production Hardening (Weeks 5-6)

**Enhancements**:
1. WAF rules on CloudFront (DDoS protection)
2. CloudWatch alarms and dashboards
3. X-Ray tracing enabled
4. Backup policies for DynamoDB
5. Multi-region failover (optional)
6. CI/CD pipeline (GitHub Actions → SAM deploy)

---

## Migration Path: Prototype → AWS

### Current Prototype Stack
- Flask backend (local)
- ChromaDB (local)
- Supabase PostgreSQL
- sentence-transformers (local)
- Gemini/Groq LLM

### Migration Steps

#### Step 1: Data Migration
```python
# Export ChromaDB to OpenSearch
import chromadb
from opensearchpy import OpenSearch

chroma_client = chromadb.Client()
collection = chroma_client.get_collection("esg_posts")

opensearch_client = OpenSearch(
    hosts=[{'host': 'your-opensearch-endpoint', 'port': 443}],
    http_auth=('username', 'password'),
    use_ssl=True
)

# Migrate vectors
results = collection.get(include=['embeddings', 'metadatas', 'documents'])
for i, embedding in enumerate(results['embeddings']):
    doc = {
        'brand_id': results['metadatas'][i]['brand_id'],
        'post_id': results['ids'][i],
        'post_text': results['documents'][i],
        'embedding_vector': embedding,
        'ers': results['metadatas'][i]['ers']
    }
    opensearch_client.index(index='esg-posts', body=doc)
```

#### Step 2: Replace Embeddings Model
```python
# Before (local sentence-transformers)
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode(text)

# After (Bedrock Titan)
import boto3
bedrock = boto3.client('bedrock-runtime')
response = bedrock.invoke_model(
    modelId='amazon.titan-embed-text-v1',
    body=json.dumps({'inputText': text})
)
embedding = json.loads(response['body'].read())['embedding']
```

#### Step 3: Replace LLM Calls
```python
# Before (Gemini)
import google.generativeai as genai
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(prompt)

# After (Bedrock Claude)
import boto3
bedrock = boto3.client('bedrock-runtime')
response = bedrock.invoke_model(
    modelId='anthropic.claude-3-haiku-20240307-v1:0',
    body=json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': 1024,
        'messages': [{'role': 'user', 'content': prompt}]
    })
)
```

#### Step 4: Refactor Flask Routes to Lambda Handlers
```python
# Before (Flask)
@app.route('/api/brand-dna', methods=['POST'])
def save_brand_dna():
    data = request.json
    # Save to Supabase
    return jsonify({'brand_id': brand_id})

# After (Lambda)
def lambda_handler(event, context):
    data = json.loads(event['body'])
    # Save to DynamoDB
    return {
        'statusCode': 200,
        'body': json.dumps({'brand_id': brand_id})
    }
```

---

## Performance Optimization Strategies

### 1. Lambda Cold Start Mitigation
- Use Provisioned Concurrency for critical functions (EmotionalAligner)
- Keep deployment packages < 50MB (use Lambda Layers for dependencies)
- Use Python 3.11 for faster startup

### 2. OpenSearch Query Optimization
- Use approximate k-NN (HNSW) instead of exact search
- Set `ef_search` parameter based on accuracy/speed tradeoff
- Cache frequent queries in ElastiCache (optional)

### 3. DynamoDB Access Patterns
- Use GSI for calendar queries (brand_id + scheduled_time)
- Batch writes for ESG ingestion (BatchWriteItem)
- Use DynamoDB Streams for real-time updates

### 4. Bedrock API Optimization
- Batch embedding requests (up to 25 texts per call)
- Use streaming for long-form content generation
- Implement exponential backoff for rate limits

### 5. Frontend Performance
- Enable CloudFront compression (gzip/brotli)
- Use React.lazy() for code splitting
- Implement optimistic UI updates

---

## Security Best Practices

### 1. API Security
- Enable AWS WAF on API Gateway
- Implement request throttling (1000 req/hour per user)
- Validate all inputs with JSON schema
- Use API keys for additional layer

### 2. Data Encryption
- Enable encryption at rest for all services
- Use TLS 1.3 for data in transit
- Rotate Secrets Manager secrets every 90 days

### 3. IAM Least Privilege
- Each Lambda function has minimal permissions
- Use resource-based policies for cross-service access
- Enable CloudTrail for audit logging

### 4. Content Safety
- Always run Comprehend toxicity check
- Implement custom banned words filter
- Log all flagged content for review

---

## Disaster Recovery & Business Continuity

### Backup Strategy

**DynamoDB**:
- Enable Point-in-Time Recovery (PITR)
- Daily backups to S3 via AWS Backup
- Cross-region replication for critical tables

**OpenSearch**:
- Automated snapshots every 24 hours
- Retention: 14 days
- Manual snapshots before major changes

**S3**:
- Versioning enabled on all buckets
- Lifecycle policy: Move to Glacier after 90 days
- Cross-region replication for brand assets

### Recovery Time Objective (RTO)
- Target: < 4 hours for full system recovery
- Critical path: Restore DynamoDB → Deploy Lambda → Restore OpenSearch

### Recovery Point Objective (RPO)
- Target: < 1 hour of data loss
- Achieved via: PITR on DynamoDB, continuous S3 replication

---

## Monitoring Dashboard

### CloudWatch Dashboard: InstaMedia AI Overview

**Widgets**:
1. API Gateway Request Count (last 24h)
2. Lambda Error Rate (all functions)
3. DynamoDB Throttled Requests
4. OpenSearch Query Latency (p50, p99)
5. Bedrock API Call Count
6. Comprehend Toxicity Detection Rate
7. SNS Notification Delivery Success Rate

**Alarms**:
- Lambda error rate > 5% → PagerDuty alert
- API Gateway 5xx > 10 requests/min → Email alert
- OpenSearch query latency > 1s → Slack alert
- DynamoDB throttling events → Auto-scale capacity

---

## Future Enhancements (V2 Roadmap)

### 1. Multi-Language Support
- Use Amazon Translate for content localization
- Fine-tune Bedrock models on Indian language corpus
- Separate ESG collections per language

### 2. Visual ESG (Image Analysis)
- Use Amazon Rekognition for image content analysis
- Build visual embedding space alongside text embeddings
- Score image-text alignment

### 3. Advanced Analytics
- Use Amazon QuickSight for brand performance dashboards
- Implement cohort analysis (brand archetypes)
- A/B testing framework for content variations

### 4. Real-Time Engagement Tracking
- Integrate with social media webhooks
- Use Amazon Kinesis for streaming analytics
- Auto-update ESG within 1 hour of post publish

### 5. Multi-Tenant Architecture
- Implement tenant isolation via Cognito groups
- Separate DynamoDB tables per tenant tier
- Usage-based billing via AWS Marketplace

---

## AWS Well-Architected Framework Alignment

### Operational Excellence
✅ Infrastructure as Code (AWS SAM)
✅ Automated deployments (CI/CD)
✅ CloudWatch monitoring and alarms
✅ X-Ray distributed tracing

### Security
✅ Encryption at rest and in transit
✅ IAM least privilege policies
✅ Secrets Manager for credentials
✅ Cognito for authentication
✅ WAF for DDoS protection

### Reliability
✅ Multi-AZ deployments (DynamoDB, OpenSearch)
✅ Automated backups and PITR
✅ Dead letter queues for failed tasks
✅ Circuit breaker patterns in Step Functions

### Performance Efficiency
✅ Serverless auto-scaling
✅ OpenSearch k-NN optimization
✅ CloudFront CDN for frontend
✅ Lambda Provisioned Concurrency for critical paths

### Cost Optimization
✅ Pay-per-use pricing (Lambda, DynamoDB)
✅ Free tier utilization for prototype
✅ S3 lifecycle policies
✅ Right-sized Lambda memory allocation

### Sustainability
✅ Serverless reduces idle compute
✅ Efficient vector search algorithms
✅ CloudFront reduces data transfer

---

## Hackathon Demo Architecture

### Simplified Demo Stack (2-Week Build)

**Core Services Only**:
1. Lambda: 5 functions (BrandDNA, ESG, Ideation, Studio, Aligner)
2. DynamoDB: 2 tables (BrandProfiles, ESGPosts)
3. OpenSearch Serverless: 1 collection
4. API Gateway: 1 REST API
5. S3: 1 bucket for assets
6. Bedrock: Claude 3 Haiku + Titan Embeddings
7. Cognito: 1 user pool

**Excluded for Demo**:
- EventBridge Scheduler (manual publishing)
- Step Functions (synchronous ESG ingestion)
- SNS notifications (in-app only)
- Multi-region setup

**Demo Flow**:
1. Create brand profile
2. Upload 50 sample posts
3. Generate 3 content ideas
4. Generate full post
5. Score with Emotional Aligner
6. Show reference posts (explainability)

**Total Demo Cost**: < $10 for 2 weeks

---

## Technical Challenges & Solutions

### Challenge 1: Vector Dimensionality Mismatch
**Problem**: sentence-transformers (384-dim) vs Titan Embeddings (1024-dim)
**Solution**: 
- Retrain ESG with Titan embeddings during migration
- Use dimensionality reduction (PCA) if needed
- Accept slight accuracy drop for managed service benefits

### Challenge 2: Cold Start Latency
**Problem**: Lambda cold starts add 2-3s to first request
**Solution**:
- Use Provisioned Concurrency for EmotionalAligner (most latency-sensitive)
- Implement client-side loading states
- Pre-warm functions via EventBridge (every 5 minutes)

### Challenge 3: OpenSearch Cost at Scale
**Problem**: OpenSearch Serverless can be expensive (>$400/month)
**Solution**:
- Use OpenSearch provisioned clusters for production (cheaper at scale)
- Implement tiered storage (hot/warm/cold)
- Archive old ESG data to S3 + Athena for analytics

### Challenge 4: Bedrock Rate Limits
**Problem**: Free tier has strict rate limits (15 req/min for Gemini equivalent)
**Solution**:
- Implement request queuing with SQS
- Use exponential backoff with jitter
- Upgrade to paid tier for production ($0.25/1M tokens is affordable)

### Challenge 5: Real-Time ESG Updates
**Problem**: Updating OpenSearch after every post is slow
**Solution**:
- Batch updates every 1 hour via EventBridge
- Use DynamoDB Streams → Lambda → OpenSearch pipeline
- Implement eventual consistency model

---

## Code Structure

### Lambda Function Organization

```
lambda/
├── handlers/
│   ├── brand_dna.py          # SaveBrandDNA
│   ├── esg_ingestion.py      # IngestHistoricalPosts
│   ├── ideation.py           # GenerateIdeas
│   ├── creative_studio.py    # GenerateContent
│   ├── emotional_aligner.py  # EmotionalAligner
│   ├── calendar.py           # SchedulePost, GetScheduledPosts
│   ├── publisher.py          # PublishPost
│   └── drift_detector.py     # DetectBrandDrift
├── lib/
│   ├── bedrock_client.py     # Bedrock API wrapper
│   ├── opensearch_client.py  # OpenSearch operations
│   ├── dynamodb_client.py    # DynamoDB operations
│   ├── comprehend_client.py  # Toxicity detection
│   └── utils.py              # ERS calculation, etc.
├── requirements.txt
└── template.yaml             # SAM template
```

### Sample Lambda Handler

```python
# handlers/emotional_aligner.py
import json
import boto3
from lib.bedrock_client import generate_embedding, analyze_content
from lib.opensearch_client import search_similar_posts
from lib.dynamodb_client import get_brand_dna

def lambda_handler(event, context):
    body = json.loads(event['body'])
    brand_id = body['brand_id']
    draft_text = body['draft_text']
    
    # Get Brand DNA
    brand_dna = get_brand_dna(brand_id)
    
    # Generate embedding
    embedding = generate_embedding(draft_text)
    
    # Search ESG
    similar_posts = search_similar_posts(brand_id, embedding, k=3)
    
    # Calculate score
    scores = []
    for post in similar_posts:
        semantic_sim = post['_score']
        ers = post['_source']['ers']
        combined = (semantic_sim * 0.4) + (ers / 100 * 0.6)
        scores.append(combined)
    
    resonance_score = int(sum(scores) / len(scores) * 100)
    
    # Analyze with Bedrock
    analysis = analyze_content(draft_text, similar_posts, brand_dna)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'resonance_score': resonance_score,
            'verdict': 'Approved' if resonance_score > 70 else 'Needs Work',
            'reference_posts': similar_posts,
            'analysis': analysis
        })
    }
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_emotional_aligner.py
import pytest
from handlers.emotional_aligner import lambda_handler

def test_emotional_aligner_high_score():
    event = {
        'body': json.dumps({
            'brand_id': 'test-brand',
            'draft_text': 'Amazing product launch! 🚀'
        })
    }
    response = lambda_handler(event, None)
    body = json.loads(response['body'])
    assert body['resonance_score'] > 50
    assert 'reference_posts' in body
```

### Integration Tests
- Test API Gateway → Lambda → DynamoDB flow
- Test ESG ingestion pipeline end-to-end
- Test Bedrock API error handling

### Load Tests
- Use Artillery or Locust
- Simulate 100 concurrent users
- Target: < 3s response time for 95th percentile

---

## Deployment Checklist

### Pre-Deployment
- [ ] Set up AWS account and IAM users
- [ ] Request Bedrock model access (Claude 3 Haiku, Titan Embeddings)
- [ ] Create S3 buckets with proper policies
- [ ] Set up Cognito user pool
- [ ] Configure Secrets Manager for OAuth tokens

### Deployment
- [ ] Deploy SAM template: `sam deploy --guided`
- [ ] Create OpenSearch Serverless collection
- [ ] Upload frontend to S3 and configure CloudFront
- [ ] Test all API endpoints with Postman
- [ ] Load sample data for demo

### Post-Deployment
- [ ] Set up CloudWatch alarms
- [ ] Configure SNS topics for alerts
- [ ] Enable X-Ray tracing
- [ ] Document API endpoints
- [ ] Create user onboarding guide

---

## Conclusion

This AWS architecture transforms InstaMedia AI from a local prototype into a production-ready, scalable platform while maintaining the core innovation: **emotion-driven content intelligence through RAG**.

**Key Benefits**:
1. **Zero Infrastructure Management**: Fully serverless
2. **Cost-Effective**: < $10/month for prototype, ~$1/brand/month at scale
3. **Scalable**: Auto-scales from 10 to 10,000 brands
4. **Secure**: Enterprise-grade security with Cognito, IAM, encryption
5. **Observable**: Full visibility via CloudWatch, X-Ray
6. **AWS-Native**: Leverages Bedrock, Comprehend, OpenSearch for AI capabilities

**Next Steps**:
1. Review and approve this architecture plan
2. Set up AWS account and request Bedrock access
3. Begin Phase 1 deployment (Lambda + DynamoDB + OpenSearch)
4. Migrate prototype data to AWS
5. Build demo for hackathon presentation

---

## Appendix: AWS Service Comparison

### Why OpenSearch Serverless over Alternatives?

| Service | Pros | Cons | Verdict |
|---------|------|------|---------|
| OpenSearch Serverless | Managed, k-NN built-in, auto-scaling | Expensive at scale | ✅ Best for prototype |
| OpenSearch Provisioned | Cheaper at scale, full control | Requires capacity planning | ✅ Best for production |
| DynamoDB + Lambda | Cheapest, simple | No native vector search | ❌ Not suitable |
| Aurora PostgreSQL + pgvector | SQL interface, familiar | Not serverless, complex setup | ❌ Overkill |
| Pinecone (external) | Purpose-built for vectors | Not AWS-native, vendor lock-in | ❌ Against hackathon rules |

### Why Bedrock over Alternatives?

| Service | Pros | Cons | Verdict |
|---------|------|------|---------|
| Amazon Bedrock | AWS-native, multiple models, managed | Slightly more expensive | ✅ Best choice |
| SageMaker Endpoints | Full control, custom models | Complex setup, expensive | ❌ Overkill |
| External APIs (OpenAI) | Easy to use | Not AWS-native, data privacy concerns | ❌ Against hackathon theme |
| Self-hosted LLMs | Full control, no API costs | Requires GPU instances, complex | ❌ Not serverless |

---

**Document Version**: 1.0  
**Last Updated**: 2025-02-26  
**Author**: InstaMedia AI Team  
**AWS AI for Bharat Hackathon 2025**
