# InstaMedia AI v3.0 - Implementation Task Breakdown

**Quick Reference for Development**

---

## Phase 4: Brand DNA Enhancement (3 days)

### Day 1: Logo Upload
- [ ] Create Supabase storage bucket `brand-logos`
- [ ] Backend: `POST /api/brand-dna/upload-logo` endpoint
- [ ] Frontend: File upload component in BrandDNA.tsx
- [ ] Test: Upload JPG, PNG, SVG
- [ ] Update brand_dna table with logo_url

### Day 2: Website Scraping
- [ ] Create `backend/services/brand_intelligence.py`
- [ ] Function: `scrape_company_website(url, brand_id)`
- [ ] Extract: About, Mission, Values, Products
- [ ] Create ChromaDB collection: `brand_knowledge`
- [ ] Test: Scrape sample website

### Day 3: RAG Integration
- [ ] Function: `get_brand_context(brand_id, query)`
- [ ] Update `ideate()` with brand context
- [ ] Update `studio_generate()` with brand context
- [ ] Test: Verify enhanced responses
- [ ] Document: Context injection examples

---

## Phase 5: ERS Logic Optimization (4 days)

### Day 4: Apify Service
- [ ] Create `backend/services/apify_ingestion.py`
- [ ] Function: `scrape_and_score(target, platform, count)`
- [ ] Function: `calculate_ers(likes, comments, shares)`
- [ ] Test: Instagram scraping with ERS
- [ ] Add rate limiting and error handling

### Day 5: Winner Filter
- [ ] Function: `filter_top_performers(posts, percentile=0.2)`
- [ ] Sort posts by ERS descending
- [ ] Calculate top 20% cutoff
- [ ] Add statistics logging
- [ ] Test: Verify filtering accuracy

### Day 6: ChromaDB Optimization
- [ ] Update metadata schema (add is_winner, percentile)
- [ ] Migration script for existing data
- [ ] Optimize query performance
- [ ] Add ERS-based retrieval
- [ ] Test: Query performance benchmarks

### Day 7: RAG Enhancement
- [ ] Update LLM prompts with high-ERS context
- [ ] Add "proven patterns" section to prompts
- [ ] A/B test old vs new prompts
- [ ] Measure content quality improvement
- [ ] Document: Prompt templates

**New Endpoint**: `POST /api/esg/scrape`

---

## Phase 6: Multi-Modal Creative Studio (7 days)

### Days 8-9: Frontend UI
- [ ] Add media format selection (Image/Video/Carousel)
- [ ] Multi-step flow component
- [ ] Loading states for each format
- [ ] Image display component
- [ ] Carousel display component
- [ ] Video storyboard display
- [ ] Update `frontend/src/types/index.ts`

### Days 10-11: Translation Layer
- [ ] Create `backend/services/media_generator.py`
- [ ] Function: `translate_to_creative_prompt(caption, hashtags, format)`
- [ ] Image prompt generation (Claude 3 Haiku)
- [ ] Carousel slide generation (3-5 slides)
- [ ] Video storyboard generation
- [ ] Validate JSON outputs
- [ ] Test: All three formats

### Days 12-13: AWS Bedrock
- [ ] Set up AWS credentials
- [ ] Function: `generate_image_titan(prompt)`
- [ ] Function: `generate_carousel_images(slides)`
- [ ] Concurrent image generation
- [ ] S3 upload for generated media
- [ ] Test: Image quality and speed
- [ ] Handle errors and retries

### Day 14: Integration
- [ ] Connect frontend to backend
- [ ] End-to-end testing (all formats)
- [ ] Performance optimization
- [ ] Error handling UI
- [ ] User feedback collection

**New Endpoint**: `POST /api/studio/generate-media`

---

## Phase 7A: Automated Cold Start (3 days)

### Day 15: Frontend
- [ ] Update `ColdStart.tsx` with competitor input
- [ ] Input: 3 competitor handles
- [ ] Progress indicators
- [ ] Results display
- [ ] Error handling

### Day 16: Backend Service
- [ ] Create `backend/services/cold_start.py`
- [ ] Function: `seed_from_competitors(handles, brand_id)`
- [ ] Concurrent Apify scraping (3 handles)
- [ ] ERS calculation and filtering
- [ ] ChromaDB storage with "competitor_seed" tag
- [ ] Test: Real competitor data

### Day 17: Integration
- [ ] Connect frontend to backend
- [ ] Test onboarding flow
- [ ] Handle timeouts (async if needed)
- [ ] Success/error messaging
- [ ] Documentation

**New Endpoint**: `POST /api/onboarding/seed`

---

## Phase 7B: Brand Drift Monitor (3 days)

### Day 18: Drift Calculation
- [ ] Create `backend/services/brand_drift.py`
- [ ] Function: `calculate_brand_drift(brand_id)`
- [ ] Function: `get_baseline_epm(brand_id)`
- [ ] Function: `get_rolling_epm(brand_id)`
- [ ] Function: `calculate_cosine_distance(vec1, vec2)`
- [ ] Test: Sample data validation

### Day 19: AWS Integration
- [ ] Create Lambda function: `brand_drift_monitor`
- [ ] Set up EventBridge schedule (weekly)
- [ ] Configure SNS for alerts
- [ ] DynamoDB table for drift history
- [ ] Test: Automated execution

### Day 20: Dashboard Widget
- [ ] Update `BrandDrift.tsx`
- [ ] Display current drift score
- [ ] Health indicator (color-coded)
- [ ] Historical trend chart (recharts)
- [ ] Alert history
- [ ] Test: UI responsiveness

**New Endpoints**: 
- `POST /api/drift/calculate`
- `GET /api/drift/history`

---

## Dependencies to Install

### Backend
```bash
pip install boto3==1.34.0
pip install beautifulsoup4==4.12.0
pip install numpy==1.26.0
```

### Frontend
```bash
npm install react-dropzone recharts
```

---

## Environment Variables to Add

```env
# AWS
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1

# Supabase Storage
SUPABASE_STORAGE_URL=https://rlirzjjecrbcfxzwdftp.storage.supabase.co
```

---

## Testing Checklist

### Phase 4
- [ ] Logo upload works for all formats
- [ ] Website scraping extracts content
- [ ] RAG context improves responses
- [ ] No performance degradation

### Phase 5
- [ ] ERS calculation accurate
- [ ] Top 20% filter correct
- [ ] ChromaDB queries fast (<100ms)
- [ ] Content quality improved

### Phase 6
- [ ] All 3 media formats generate
- [ ] Images high quality
- [ ] Carousels have 3-5 slides
- [ ] Video storyboards structured
- [ ] S3 storage working

### Phase 7
- [ ] Cold start completes <2 min
- [ ] Drift calculation accurate
- [ ] Alerts sent correctly
- [ ] Dashboard displays data

---

## Risk Mitigation

### High Risk Items
1. **AWS Bedrock Access**: Ensure account has Bedrock enabled
2. **Apify Rate Limits**: Implement exponential backoff
3. **30-second Timeout**: Use async processing for long operations
4. **Cost Management**: Monitor AWS usage closely

### Mitigation Strategies
- Test AWS services in sandbox first
- Implement request queuing
- Add background job processing
- Set up billing alerts

---

## Success Criteria

- [ ] All 5 features implemented
- [ ] No breaking changes to existing features
- [ ] Performance maintained or improved
- [ ] User satisfaction >85%
- [ ] Cost within budget ($50-100/month)

---

Ready to begin implementation!
