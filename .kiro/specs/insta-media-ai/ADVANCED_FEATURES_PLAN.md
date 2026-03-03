# InstaMedia AI v2 - Advanced Features Development Plan

**Date**: March 2, 2026  
**Version**: 3.0 (Advanced Features)  
**Status**: Planning Phase

---

## 🎯 Overview

This document outlines the phased implementation plan for 5 major advanced features:

1. **Brand DNA Enhancement** - Logo upload + RAG-based company intelligence
2. **ERS Logic Optimization** - Dynamic real-time scoring with Apify
3. **Multi-Modal Creative Studio** - Image/Video/Carousel generation
4. **Automated Cold Start** - Competitor seeding
5. **Dynamic Brand Drift Monitor** - Real-time alignment tracking

---

## 📋 Feature Summary

### Feature 1: Brand DNA Enhancement with RAG
**Priority**: High  
**Complexity**: Medium  
**Timeline**: 2-3 days

**Components**:
- Supabase S3 logo upload
- Web scraping company website
- RAG-based company knowledge extraction
- Custom-tuned LLM responses

### Feature 2: ERS Logic Optimization
**Priority**: Critical  
**Complexity**: High  
**Timeline**: 3-4 days

**Components**:
- Real-time Apify integration
- Dynamic ERS calculation
- Top 20% filtering ("Winner" filter)
- ChromaDB optimization
- Enhanced RAG generation

### Feature 3: Multi-Modal Creative Studio
**Priority**: High  
**Complexity**: Very High  
**Timeline**: 5-7 days

**Components**:
- Multi-step media selection UI
- LLM prompt translation layer
- AWS Bedrock integration (Titan Image Generator)
- Image/Video/Carousel generation
- S3 storage for generated media

### Feature 4: Automated Cold Start
**Priority**: Medium  
**Complexity**: Medium  
**Timeline**: 2-3 days

**Components**:
- Competitor handle input UI
- Concurrent Apify scraping
- ERS-based filtering
- Automatic database seeding
- Onboarding flow

### Feature 5: Dynamic Brand Drift Monitor
**Priority**: Medium  
**Complexity**: High  
**Timeline**: 3-4 days

**Components**:
- Vector centroid calculation
- Cosine distance measurement
- AWS Lambda + EventBridge scheduling
- Alert system (SNS)
- Dashboard widget

---

## 🗓️ Phased Implementation Plan

### Phase 4: Brand DNA Enhancement (Days 1-3)
### Phase 5: ERS Logic Optimization (Days 4-7)
### Phase 6: Multi-Modal Creative Studio (Days 8-14)
### Phase 7: Cold Start + Brand Drift (Days 15-20)

---

## 📊 Detailed Feature Breakdown



## Phase 4: Brand DNA Enhancement with RAG

### Objectives
1. Enable logo upload to Supabase S3
2. Scrape company website for brand intelligence
3. Build RAG knowledge base from scraped data
4. Enhance LLM responses with company context

### Technical Requirements

#### 4.1 Logo Upload to Supabase S3
**Backend** (`backend/app.py`):
```python
# New endpoint
@app.route("/api/brand-dna/upload-logo", methods=["POST"])
def upload_logo():
    # 1. Receive file from frontend
    # 2. Validate file type (jpg, png, svg)
    # 3. Upload to Supabase Storage
    # 4. Return public URL
    # 5. Update brand_dna table with logo_url
```

**Frontend** (`BrandDNA.tsx`):
```typescript
// Add file upload component
// Preview uploaded logo
// Store logo URL in brand DNA
```

**Supabase Storage Setup**:
- Bucket: `brand-logos`
- Public access: Yes
- Max file size: 5MB
- Allowed types: image/jpeg, image/png, image/svg+xml

#### 4.2 Website Scraping & RAG Knowledge Base
**Backend** (`backend/services/brand_intelligence.py`):
```python
def scrape_company_website(website_url, brand_id):
    # 1. Use Apify Web Scraper or BeautifulSoup
    # 2. Extract: About, Mission, Values, Products
    # 3. Clean and chunk text (500 chars per chunk)
    # 4. Generate embeddings for each chunk
    # 5. Store in ChromaDB with metadata
    # 6. Return summary statistics
```

**ChromaDB Collection**: `brand_knowledge`
```python
{
    "document": "chunk_text",
    "metadata": {
        "brand_id": "default",
        "source": "website",
        "url": "https://...",
        "section": "about" | "mission" | "products",
        "scraped_at": "timestamp"
    }
}
```

#### 4.3 RAG-Enhanced LLM Responses
**Update existing endpoints**:
```python
def get_brand_context(brand_id, query):
    # 1. Query brand_knowledge collection
    # 2. Retrieve top 5 relevant chunks
    # 3. Concatenate into context string
    # 4. Inject into LLM prompt
    
# Update ideate() endpoint
# Update studio_generate() endpoint
# Update analyze_draft() endpoint
```

### Implementation Steps

**Day 1: Logo Upload**
- [ ] Create Supabase storage bucket
- [ ] Implement upload endpoint
- [ ] Add file upload UI to BrandDNA.tsx
- [ ] Test upload and retrieval

**Day 2: Website Scraping**
- [ ] Create brand_intelligence.py service
- [ ] Implement web scraping function
- [ ] Create brand_knowledge ChromaDB collection
- [ ] Test scraping and storage

**Day 3: RAG Integration**
- [ ] Implement get_brand_context() helper
- [ ] Update ideate() with brand context
- [ ] Update studio_generate() with brand context
- [ ] Test enhanced responses

### Success Criteria
- ✅ Logo uploads successfully to Supabase
- ✅ Website scraping extracts relevant content
- ✅ Brand knowledge stored in ChromaDB
- ✅ LLM responses include company-specific context
- ✅ Generated content aligns with brand values

---

## Phase 5: ERS Logic Optimization

### Objectives
1. Implement real-time Apify scraping
2. Calculate ERS dynamically for all posts
3. Filter top 20% performers ("Winner" filter)
4. Optimize ChromaDB for RAG generation
5. Enhance content quality with high-ERS references

### Technical Requirements

#### 5.1 Enhanced Apify Integration
**Backend** (`backend/services/apify_ingestion.py`):
```python
def scrape_and_score(target, platform, count=50):
    # 1. Trigger Apify actor
    # 2. Parse response (text, likes, comments, shares)
    # 3. Calculate ERS for each post
    # 4. Sort by ERS descending
    # 5. Return all posts with scores
    
def calculate_ers(likes, comments, shares):
    # Current formula
    raw = (likes * 0.2) + (comments * 0.5) + (shares * 0.8)
    ers = min(round(math.log1p(raw) * 10, 2), 100.0)
    return ers
```

#### 5.2 Winner Filter Implementation
```python
def filter_top_performers(posts, percentile=0.2):
    # 1. Sort posts by ERS
    # 2. Calculate cutoff index (top 20%)
    # 3. Return only high-performers
    # 4. Log statistics (avg ERS, count)
    
    sorted_posts = sorted(posts, key=lambda x: x['ers'], reverse=True)
    cutoff = int(len(sorted_posts) * percentile)
    winners = sorted_posts[:cutoff]
    return winners
```

#### 5.3 ChromaDB Optimization
**Enhanced Metadata**:
```python
{
    "ers": 87.5,
    "likes": 5000,
    "comments": 450,
    "shares": 120,
    "platform": "instagram",
    "emotion": "Inspiring",
    "source": "apify",
    "scraped_at": "2026-03-02T10:00:00Z",
    "is_winner": True,  # Top 20%
    "percentile": 95    # ERS percentile
}
```

#### 5.4 RAG Enhancement for Content Generation
**Update LLM Prompts**:
```python
prompt = f"""You are a creative strategist.

HIGH-PERFORMING REFERENCE POSTS (ERS > 85):
{top_posts_context}

These posts achieved exceptional emotional resonance. Analyze:
- Vocabulary patterns
- Hook structures
- Emotional triggers
- Storytelling techniques

Generate content that adopts these proven patterns while maintaining our Brand DNA.

Brand Mission: {mission}
Focus: {focus_area}
"""
```

### Implementation Steps

**Day 4: Apify Service Enhancement**
- [ ] Create apify_ingestion.py service
- [ ] Implement scrape_and_score()
- [ ] Test with Instagram scraper
- [ ] Add error handling and rate limiting

**Day 5: Winner Filter**
- [ ] Implement filter_top_performers()
- [ ] Update scraping endpoint to use filter
- [ ] Add ERS statistics to response
- [ ] Test filtering logic

**Day 6: ChromaDB Optimization**
- [ ] Update metadata schema
- [ ] Add is_winner and percentile fields
- [ ] Migrate existing data
- [ ] Optimize query performance

**Day 7: RAG Enhancement**
- [ ] Update LLM prompts with high-ERS context
- [ ] Test content quality improvements
- [ ] A/B test old vs new prompts
- [ ] Document improvements

### New API Endpoint

```python
@app.route("/api/esg/scrape", methods=["POST"])
def esg_scrape():
    """
    Real-time scraping with ERS filtering
    
    Body: {
        "target": "hashtag or handle",
        "platform": "instagram",
        "brand_id": "default"
    }
    
    Returns: {
        "success": true,
        "total_scraped": 50,
        "winners_added": 10,
        "avg_ers": 78.5,
        "min_ers": 65.0,
        "max_ers": 92.3
    }
    """
```

### Success Criteria
- ✅ Real-time scraping with ERS calculation
- ✅ Top 20% filtering working correctly
- ✅ ChromaDB optimized with enhanced metadata
- ✅ Content quality improved with high-ERS references
- ✅ API response time < 30 seconds

---

## Phase 6: Multi-Modal Creative Studio

### Objectives
1. Add media format selection (Image/Video/Carousel)
2. Implement LLM prompt translation layer
3. Integrate AWS Bedrock Titan Image Generator
4. Generate images, carousels, and video storyboards
5. Store generated media in S3

### Technical Requirements

#### 6.1 Frontend Multi-Step UI
**Update** (`CreativeStudio.tsx`):
```typescript
// Step 1: Generate caption + hashtags (existing)
// Step 2: Select media format
type MediaFormat = 'image' | 'video' | 'carousel';

// Step 3: Generate media
// Step 4: Display results
```

#### 6.2 LLM Prompt Translation Layer
**Backend** (`backend/services/media_generator.py`):
```python
def translate_to_creative_prompt(caption, hashtags, format):
    """
    Use Claude 3 Haiku to convert caption into specialized prompt
    """
    if format == "image":
        # Generate detailed image prompt
        # Focus: lighting, subject, style, camera angles
        
    elif format == "carousel":
        # Divide into 3-5 slides
        # Return JSON: [{text, image_prompt}]
        
    elif format == "video":
        # Generate video storyboard
        # Return JSON: [{scene, voiceover, visual_action}]
```

#### 6.3 AWS Bedrock Integration
**Setup**:
```python
import boto3

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def generate_image_titan(prompt):
    # Call Titan Image Generator G1
    # Return S3 URL or base64
    
def generate_carousel_images(slides):
    # Concurrent calls for each slide
    # Return array of image URLs
```

#### 6.4 Media Storage
**Supabase S3**:
- Bucket: `generated-media`
- Structure: `{brand_id}/{media_type}/{timestamp}/`
- Public access: Yes

### Implementation Steps

**Days 8-9: Frontend UI**
- [ ] Add media format selection UI
- [ ] Implement multi-step flow
- [ ] Add loading states
- [ ] Create media display components

**Days 10-11: Translation Layer**
- [ ] Create media_generator.py service
- [ ] Implement translate_to_creative_prompt()
- [ ] Test with Claude 3 Haiku
- [ ] Validate JSON outputs

**Days 12-13: AWS Bedrock Integration**
- [ ] Set up AWS credentials
- [ ] Implement Titan Image Generator calls
- [ ] Test image generation
- [ ] Implement carousel generation

**Day 14: Integration & Testing**
- [ ] Connect frontend to backend
- [ ] Test end-to-end flow
- [ ] Optimize performance
- [ ] Handle errors gracefully

### New API Endpoints

```python
@app.route("/api/studio/generate-media", methods=["POST"])
def generate_media():
    """
    Body: {
        "caption": "...",
        "hashtags": [...],
        "format": "image" | "video" | "carousel",
        "brand_id": "default"
    }
    
    Returns: {
        "success": true,
        "format": "image",
        "media_url": "https://...",
        "creative_prompt": "..."
    }
    """
```

### Success Criteria
- ✅ Multi-step UI working smoothly
- ✅ LLM translation generates valid prompts
- ✅ Images generated successfully
- ✅ Carousels with 3-5 slides
- ✅ Video storyboards structured correctly
- ✅ Media stored in S3

---

## Phase 7: Cold Start & Brand Drift

### Part A: Automated Cold Start (Days 15-17)

#### Objectives
1. Competitor handle input during onboarding
2. Concurrent scraping of competitor posts
3. ERS-based filtering and seeding
4. Automatic database population

#### Technical Requirements

**Frontend** (`ColdStart.tsx`):
```typescript
// Onboarding flow
// Input: 3 competitor handles
// Display: Scraping progress
// Result: Database seeded confirmation
```

**Backend** (`backend/services/cold_start.py`):
```python
async def seed_from_competitors(competitor_handles, brand_id):
    # 1. Concurrent Apify scraping (3 handles)
    # 2. Scrape 50 posts per competitor
    # 3. Calculate ERS for all posts
    # 4. Filter top 20% across all competitors
    # 5. Embed and store in ChromaDB
    # 6. Tag as "competitor_seed"
    # 7. Return statistics
```

#### Implementation Steps

**Day 15: Frontend**
- [ ] Update ColdStart.tsx with input form
- [ ] Add progress indicators
- [ ] Display seeding results

**Day 16: Backend Service**
- [ ] Create cold_start.py
- [ ] Implement concurrent scraping
- [ ] Add ERS filtering
- [ ] Test with real competitors

**Day 17: Integration**
- [ ] Connect frontend to backend
- [ ] Test onboarding flow
- [ ] Handle timeouts gracefully
- [ ] Add async processing if needed

### Part B: Dynamic Brand Drift Monitor (Days 18-20)

#### Objectives
1. Calculate brand alignment score
2. Detect emotional drift
3. Automated monitoring with EventBridge
4. Alert system for drift detection

#### Technical Requirements

**Backend** (`backend/services/brand_drift.py`):
```python
def calculate_brand_drift(brand_id):
    # 1. Fetch baseline EPM (centroid of top 20% all-time)
    # 2. Fetch rolling EPM (centroid of last 15 posts)
    # 3. Calculate cosine distance
    # 4. Return drift score (0-1)
    
def get_baseline_epm(brand_id):
    # Query ChromaDB for top 20% posts
    # Calculate centroid vector
    
def get_rolling_epm(brand_id):
    # Query last 15 published posts
    # Calculate centroid vector
    
def calculate_cosine_distance(vec1, vec2):
    # Use numpy or ChromaDB distance
    # Return distance (0 = identical, 1 = opposite)
```

**AWS Lambda** (`lambda/brand_drift_monitor.py`):
```python
def lambda_handler(event, context):
    # 1. Get all active brand_ids
    # 2. Calculate drift for each
    # 3. If drift > 0.15, send SNS alert
    # 4. Log to DynamoDB
```

**EventBridge Schedule**:
- Frequency: Weekly (every Monday 9am)
- Target: Lambda function

#### Implementation Steps

**Day 18: Drift Calculation**
- [ ] Create brand_drift.py
- [ ] Implement vector centroid calculation
- [ ] Implement cosine distance
- [ ] Test with sample data

**Day 19: AWS Integration**
- [ ] Create Lambda function
- [ ] Set up EventBridge schedule
- [ ] Configure SNS for alerts
- [ ] Test automated monitoring

**Day 20: Dashboard Widget**
- [ ] Update BrandDrift.tsx
- [ ] Display drift score
- [ ] Show health indicator
- [ ] Add historical trend chart

### New API Endpoints

```python
@app.route("/api/drift/calculate", methods=["POST"])
def calculate_drift():
    """Calculate current brand drift score"""
    
@app.route("/api/drift/history", methods=["GET"])
def get_drift_history():
    """Get historical drift scores"""
```

### Success Criteria
- ✅ Cold start seeds database with competitor data
- ✅ Drift calculation accurate
- ✅ Automated monitoring working
- ✅ Alerts sent when drift detected
- ✅ Dashboard displays health metrics

---

## 🔧 Technical Stack Updates

### New Dependencies

**Backend** (`requirements.txt`):
```
boto3==1.34.0              # AWS SDK
apify-client==1.7.1        # Already added
beautifulsoup4==4.12.0     # Web scraping
numpy==1.26.0              # Vector math
asyncio                    # Concurrent operations
```

**Frontend** (`package.json`):
```json
{
  "react-dropzone": "^14.2.3",
  "recharts": "^2.10.0"
}
```

### AWS Services Required
- Amazon Bedrock (Claude 3 Haiku, Titan Image Generator)
- S3 (media storage)
- Lambda (drift monitoring)
- EventBridge (scheduling)
- SNS (alerts)
- DynamoDB (drift history)

### Environment Variables

```env
# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1

# Supabase Storage
SUPABASE_STORAGE_URL=https://...
```

---

## 📊 Implementation Timeline

```
Week 1 (Days 1-7):
├── Days 1-3: Phase 4 - Brand DNA Enhancement
└── Days 4-7: Phase 5 - ERS Logic Optimization

Week 2 (Days 8-14):
└── Days 8-14: Phase 6 - Multi-Modal Creative Studio

Week 3 (Days 15-20):
├── Days 15-17: Phase 7A - Automated Cold Start
└── Days 18-20: Phase 7B - Brand Drift Monitor

Total: 20 days (4 weeks)
```

---

## 🎯 Success Metrics

### Phase 4: Brand DNA Enhancement
- Logo upload success rate: >95%
- Website scraping accuracy: >80%
- RAG context relevance: >85%

### Phase 5: ERS Optimization
- Scraping speed: <30 seconds
- Winner filter accuracy: 100%
- Content quality improvement: +20%

### Phase 6: Multi-Modal Studio
- Image generation success: >90%
- Carousel generation: 3-5 slides
- User satisfaction: >85%

### Phase 7: Cold Start & Drift
- Cold start time: <2 minutes
- Drift detection accuracy: >90%
- Alert false positive rate: <10%

---

## 🚀 Next Steps

1. Review and approve this plan
2. Set up AWS account and services
3. Begin Phase 4 implementation
4. Weekly progress reviews
5. Iterative testing and refinement

---

This comprehensive plan provides a clear roadmap for implementing all advanced features in a phased, manageable approach.
