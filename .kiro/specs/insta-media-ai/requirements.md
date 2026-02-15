# Requirements Document: InstaMedia AI — Emotional Signal Engine

## AWS AI for Bharat Hackathon 2025 | Problem Track: AI for Media, Content & Digital Experiences

## Introduction

### 1.1 Purpose

This document defines the functional and non-functional requirements for **InstaMedia AI** — an AI-powered brand content intelligence platform that solves the *emotional resonance gap* in AI-generated marketing content.

The system builds a continuously learning **Emotional Signal Graph (ESG)** from a brand's historical engagement data, uses it to score every AI-generated draft for emotional authenticity, and ensures AI-produced content carries the same emotional weight as the brand's best human-written posts.

### 1.2 Problem Statement

Digital marketing teams face a compounding crisis:

- Content volume demands have increased **3–5× in three years**
- AI tools can generate content at scale — but they produce **emotionally hollow, generic outputs**
- Research shows AI-labeled content receives **lower trust, loyalty, and purchase intent** from Indian consumers
- Brand voice "drift" — the gradual degradation of a brand's emotional DNA at scale — has **no automated solution today**

**The core insight:** Every AI content tool solves the *production* problem (speed). Nobody has solved the *resonance* problem (does this content actually connect?).

### 1.3 Why AI is Essential — Not Just Helpful

This problem **cannot be solved with rule-based logic** because:

1. **Emotional resonance is non-deterministic.** The difference between a post that gets 10 shares and one that gets 10,000 shares cannot be captured in a rule like "use storytelling." It lives in the vector space between semantic meaning and audience emotional history.

2. **Brand voice is latent, not explicit.** No brand can fully articulate why their best posts work. The pattern only becomes visible when you embed hundreds of posts and look at the cluster topology — that requires machine learning.

3. **The pattern shifts over time.** What resonated in Q1 may not resonate in Q3 as audience composition and cultural context evolves. Static rules go stale; a continuously-learning ESG does not.

4. **Feedback loops require inference.** Predicting whether a new draft will resonate with a brand's *specific* audience requires generalizing from historical engagement patterns — the definition of a machine learning task.

### 1.4 Scope

The prototype covers the full brand content lifecycle:

- Brand identity setup (Brand DNA Vault)
- Emotional memory construction (ESG Engine)
- AI-conditioned content ideation
- Emotional alignment scoring (The Bouncer Agent)
- Content scheduling and calendar
- Post-publish ESG update loop

## Glossary

- **ESG (Emotional Signal Graph)**: A vector database containing embeddings of a brand's historical posts with engagement scores, used to measure emotional resonance of new content
- **ERS (Emotional Resonance Score)**: A 0-100 score calculated from engagement metrics: `log1p((likes×0.2)+(comments×0.5)+(shares×0.8))×10`
- **EPM (Emotional Persona Model)**: The learned representation of a brand's emotional signature derived from their ESG
- **Brand DNA Vault**: Central repository storing brand identity elements (mission, tone, colors, banned words, logo)
- **The Bouncer Agent**: The Emotional Aligner component that scores draft content against the brand's ESG
- **Semantic Similarity**: Cosine similarity between vector embeddings, measuring content similarity
- **Brand Drift**: When a brand's current emotional signature deviates significantly (>0.15 cosine distance) from its historical baseline
- **Cold Start**: The challenge of providing value to new brands with zero historical data
- **HITL (Human-in-the-Loop)**: Manual review and approval gate before content publishing
- **Content Calendar**: Scheduled timeline of posts with platform, time, and resonance scores
- **Ideation Agent**: Component that generates content ideas conditioned on Brand DNA and ESG patterns
- **Creative Studio**: Interface for generating full posts with real-time emotional alignment scoring
- **Reference Posts**: Top-performing historical posts retrieved from ESG that influenced a scoring decision
- **Banned Words**: User-defined list of terms that trigger automatic content flagging
- **SMB**: Small and Medium Business
- **D2C**: Direct-to-Consumer business model

## Requirements

## User Stories

### Primary User: Social Media / Content Manager at an Indian SME or D2C Brand

```
US-001  As a content manager, I want to upload my brand's past posts with
        engagement data so the AI can learn what content emotionally resonates
        with my specific Indian audience segment.

US-002  As a content creator, I want to type a draft post and instantly receive
        an emotional resonance score (0–100) with specific feedback on what
        emotional signals are missing, so I can improve before publishing.

US-003  As a marketer, I want AI to generate 3 post variations that are
        conditioned on my brand's highest-performing emotional patterns,
        not just generic prompts.

US-004  As a brand manager, I want to define banned words, tone descriptors,
        and brand colors in a central vault so all AI content respects these
        rules automatically.

US-005  As a content planner, I want a visual monthly calendar to manage my
        scheduled post queue and see what's coming up.

US-006  As a growth marketer, I want an alert when my brand's emotional
        signature drifts from its historical baseline so I can course-correct
        before audience trust erodes.

US-007  As a new brand with zero data, I want the system to bootstrap my
        Emotional Persona Model from a similar brand archetype so I get
        value from day one (cold-start solution).
```

### Secondary User: Digital Marketing Agency Managing Multiple Brand Clients

```
US-008  As an agency manager, I want to switch between brand profiles to manage
        content for multiple clients from a single dashboard.

US-009  As a content strategist, I want to see which emotional archetypes drive
        the highest resonance per brand to brief my human writers more effectively.
```

### Requirement 1: Brand DNA Vault

**User Story:** As a brand manager, I want to define my brand's core identity elements in one place, so that all AI-generated content automatically respects my brand guidelines.

#### Acceptance Criteria

1.1 WHEN a user enters their brand setup, THE System SHALL provide fields for: brand name, mission statement, typography direction, and industry category

1.2 WHEN a user defines tone descriptors, THE System SHALL support tag-based entry (e.g., "vulnerable", "direct", "playful", "authoritative") with visual tag chips

1.3 WHEN a user enters brand colors, THE System SHALL accept hex color codes and display a live color palette preview

1.4 WHEN a user creates a banned words list, THE System SHALL store it and automatically flag any AI-generated content containing those words

1.5 WHEN Brand DNA is saved, THE System SHALL persist all data to Supabase PostgreSQL with a unique brand_id

1.6 WHEN Brand DNA is updated, THE System SHALL inject the updated mission statement, tone descriptors, and banned words into all subsequent LLM generation prompts

1.7 THE System SHALL support logo upload via Supabase Storage with automatic image optimization

1.8 WHEN a user has not completed Brand DNA setup, THE System SHALL display a setup wizard and block access to content generation features

### Requirement 2: Emotional Signal Graph (ESG) Engine — Core AI Component

**User Story:** As a content manager, I want the system to learn from my brand's historical post performance, so that it can predict which new content will emotionally resonate with my audience.

#### Acceptance Criteria

2.1 WHEN a user uploads historical posts, THE System SHALL accept CSV files with columns: post_text, likes, comments, shares, platform, post_date

2.2 WHEN processing each post, THE System SHALL calculate Emotional Resonance Score (ERS) using the formula: `ERS = log1p((likes×0.2) + (comments×0.5) + (shares×0.8)) × 10`, clamped to range 0-100

2.3 WHEN calculating embeddings, THE System SHALL use `sentence-transformers/all-MiniLM-L6-v2` model running **locally** (no external API calls) to generate 384-dimensional vectors

2.4 WHEN storing embeddings, THE System SHALL persist vectors + ERS metadata + post_text to ChromaDB with cosine similarity indexing enabled

2.5 WHEN querying the ESG for similar content, THE System SHALL retrieve top-k results and re-rank using combined score: `combined_score = (semantic_similarity × 0.4) + (ERS/100 × 0.6)`

2.6 WHEN a new post is published and engagement data becomes available, THE System SHALL automatically update the ESG with the new post's embedding and ERS

2.7 WHEN the ESG contains sufficient data (>50 posts), THE System SHALL calculate the brand's Emotional Persona Model (EPM) as the centroid of top-performing post embeddings (ERS > 70)

2.8 WHEN calculating brand drift, THE System SHALL compute cosine distance between current EPM and historical baseline EPM, and trigger an alert if distance > 0.15

2.9 FOR cold-start scenarios (brands with <10 posts), THE System SHALL offer to bootstrap the ESG from a similar brand archetype cluster (e.g., "wellness D2C", "local food brand", "fashion startup")

2.10 THE System SHALL support incremental ESG updates without requiring full re-indexing

2.11 THE System SHALL persist ChromaDB data to disk for durability across server restarts

### Requirement 3: Content Ideation Agent

**User Story:** As a content creator, I want AI to suggest content ideas that are conditioned on my brand's emotional patterns, so that I start with concepts that have a higher probability of resonating.

#### Acceptance Criteria

3.1 WHEN a user requests content ideas, THE System SHALL accept a focus area input (e.g., "product launch", "festival campaign", "customer testimonials")

3.2 WHEN generating ideas, THE Ideation Agent SHALL query the ESG to retrieve top 5 highest-performing posts (by ERS) semantically similar to the focus area

3.3 WHEN constructing the LLM prompt, THE Ideation Agent SHALL inject: Brand DNA (mission + tone), focus area, and reference post excerpts from ESG

3.4 WHEN calling the LLM, THE Ideation Agent SHALL use Gemini 1.5 Flash or Groq Llama 3.1 (free tier) to generate 5 distinct content ideas

3.5 FOR each generated idea, THE System SHALL return: title, opening hook, emotional angle, target platform (Instagram/LinkedIn/Twitter), and predicted ERS range

3.6 WHEN ideas are displayed, THE System SHALL show which reference posts from the ESG influenced each idea (explainability)

3.7 WHEN a user selects an idea, THE System SHALL allow one-click transition to Creative Studio with the idea pre-loaded as context

3.8 THE Ideation Agent SHALL complete generation within 5 seconds for optimal user experience

### Requirement 4: Creative Studio + Emotional Aligner (The Bouncer)

**User Story:** As a content creator, I want to generate a full post and immediately see its emotional resonance score with actionable feedback, so that I can iterate until the content meets my brand's emotional standards.

#### Acceptance Criteria

4.1 WHEN a user enters a topic or selects an idea from Ideation, THE Creative Studio SHALL generate a complete post including: main copy, hashtags, call-to-action, and image style brief

4.2 WHEN generating content, THE System SHALL inject Brand DNA (mission, tone, banned words) into the LLM prompt to ensure brand alignment

4.3 WHEN content is generated, THE System SHALL display it in a split-screen view: generated content on left, Emotional Aligner score panel on right

4.4 WHEN scoring content, THE Emotional Aligner (Bouncer Agent) SHALL:
   - Embed the draft post using the same sentence-transformer model
   - Query the ESG for top 3 most similar historical posts
   - Calculate semantic similarity and weighted ERS scores
   - Return a JSON response with: resonance_score (0-100), verdict ("Approved" / "Needs Work" / "Rejected"), emotional_archetype, what_works[], what_is_missing[], missing_signals[], rewrite_suggestion

4.5 WHEN displaying the score, THE System SHALL use color coding: green (>70), yellow (50-70), red (<50)

4.6 WHEN banned words are detected in the draft, THE System SHALL display an inline alert with the specific flagged words highlighted

4.7 WHEN the Emotional Aligner provides feedback, THE System SHALL display the top 3 reference posts from the ESG that influenced the scoring decision (explainability)

4.8 WHEN a rewrite suggestion is provided, THE System SHALL offer a one-click "Apply Suggestion" button that replaces the current draft

4.9 WHEN a user is satisfied with the content and score, THE System SHALL provide a "Schedule Post" button that transitions to the Calendar module

4.10 THE Emotional Aligner SHALL complete analysis within 5 seconds to maintain interactive editing flow

4.11 THE System SHALL support iterative editing: each time the user modifies the draft, the Emotional Aligner SHALL automatically re-score the updated content

4.12 THE System SHALL log all generated content and scores to Supabase for analytics and continuous learning

### Requirement 5: Content Calendar

**User Story:** As a content planner, I want a visual calendar to manage my scheduled posts, so that I can see my content pipeline at a glance and maintain consistent publishing.

#### Acceptance Criteria

5.1 WHEN a user navigates to the Calendar module, THE System SHALL display a monthly grid view with current month by default

5.2 WHEN displaying calendar days, THE System SHALL show post content previews (first 50 characters) for each scheduled post

5.3 WHEN a user clicks on a calendar day, THE System SHALL display all posts scheduled for that day in a detailed view with: full content, platform, scheduled time, resonance score, status

5.4 WHEN storing scheduled posts, THE System SHALL persist to Supabase with fields: content, platform, scheduled_time, status (draft/scheduled/published), resonance_score, image_url, brand_id

5.5 WHEN a post is scheduled from Creative Studio, THE System SHALL add it to the calendar with status "scheduled"

5.6 THE System SHALL support post statuses: "draft" (saved but not scheduled), "scheduled" (queued for publishing), "published" (live on platform)

5.7 WHEN displaying posts, THE System SHALL use visual indicators to differentiate status: gray (draft), blue (scheduled), green (published)

5.8 THE System SHALL allow users to navigate between months using previous/next month buttons

5.9 THE System SHALL highlight the current day in the calendar view

5.10 WHEN a user edits a scheduled post, THE System SHALL update the calendar view in real-time without requiring page refresh

### Requirement 6: Overview Dashboard

**User Story:** As a brand manager, I want a dashboard that shows my content metrics and system status at a glance, so that I can quickly assess my brand's content health.

#### Acceptance Criteria

6.1 WHEN a user navigates to the Overview module, THE System SHALL display key metrics: total content count, scheduled posts count, average resonance score, ESG memory size (number of posts)

6.2 WHEN displaying metrics, THE System SHALL use visual cards with icons and large numbers for quick scanning

6.3 WHEN showing average resonance score, THE System SHALL use color coding: green (>70), yellow (50-70), red (<50)

6.4 THE Dashboard SHALL display system status indicators: LLM provider (Gemini/Groq), Supabase connection status, ESG status (posts indexed)

6.5 THE Dashboard SHALL show an "Upcoming Posts" feed with the next 3 scheduled posts including: content preview, platform, scheduled time, resonance score

6.6 THE Dashboard SHALL show a "Recent Activity" feed with the last 4 actions: posts created, posts scheduled, posts published, ESG updates

6.7 WHEN the ESG is empty or has <10 posts, THE Dashboard SHALL display a prominent call-to-action to upload historical data

6.8 WHEN brand drift is detected (EPM distance > 0.15), THE Dashboard SHALL display a warning alert with explanation and recommended actions

6.9 THE Dashboard SHALL refresh metrics automatically when new content is created or scheduled

### Requirement 7: ESG Update Loop (Post-Publish Learning)

**User Story:** As a growth marketer, I want the system to continuously learn from my published content's performance, so that the emotional resonance predictions improve over time.

#### Acceptance Criteria

7.1 WHEN a post is published and engagement data becomes available (24-48 hours post-publish), THE System SHALL accept manual entry of: likes, comments, shares

7.2 WHEN engagement data is entered, THE System SHALL calculate the actual ERS using the standard formula

7.3 WHEN actual ERS is calculated, THE System SHALL compare it to the predicted ERS from the Emotional Aligner and log the prediction error

7.4 WHEN updating the ESG, THE System SHALL embed the published post and add it to ChromaDB with its actual ERS

7.5 WHEN the ESG is updated, THE System SHALL recalculate the Emotional Persona Model (EPM) to reflect the new data

7.6 WHEN prediction errors exceed 20% consistently (>5 posts), THE System SHALL trigger a model recalibration alert

7.7 THE System SHALL maintain a prediction accuracy log for analytics: predicted_ERS, actual_ERS, error_percentage, post_id, timestamp

7.8 THE System SHALL support bulk engagement data import via CSV for updating multiple published posts at once

### Requirement 8: Brand Drift Detection and Alerts

**User Story:** As a brand manager, I want to be alerted when my content's emotional signature drifts from my brand's historical baseline, so that I can course-correct before losing audience trust.

#### Acceptance Criteria

8.1 WHEN the ESG contains >50 posts, THE System SHALL establish a baseline EPM from the top 20% highest-performing posts

8.2 WHEN new content is published and added to the ESG, THE System SHALL calculate a rolling EPM from the most recent 30 posts

8.3 WHEN calculating drift, THE System SHALL compute cosine distance between baseline EPM and rolling EPM

8.4 WHEN drift distance exceeds 0.15, THE System SHALL trigger a "Brand Drift Alert" visible on the Dashboard

8.5 WHEN displaying the alert, THE System SHALL show: drift magnitude, trend direction (moving toward/away from baseline), and specific emotional signals that have changed

8.6 THE System SHALL provide actionable recommendations: "Review recent posts", "Return to top-performing themes", "Analyze audience feedback"

8.7 THE System SHALL allow users to acknowledge the alert and set a new baseline if the drift is intentional (brand evolution)

8.8 THE System SHALL log all drift events for historical analysis: timestamp, drift_magnitude, baseline_EPM, rolling_EPM

### Requirement 9: Cold-Start Solution for New Brands

**User Story:** As a new brand with no historical data, I want the system to provide value from day one by bootstrapping my emotional model from similar brands, so that I don't have to wait months to use the platform.

#### Acceptance Criteria

9.1 WHEN a new brand has <10 posts in their ESG, THE System SHALL offer a cold-start bootstrap option

9.2 WHEN bootstrapping, THE System SHALL present brand archetype options: "Wellness D2C", "Local Food Brand", "Fashion Startup", "Tech SaaS", "Education Platform", "Fitness & Health"

9.3 WHEN a user selects an archetype, THE System SHALL load a pre-trained ESG cluster containing 50-100 high-performing posts from similar brands

9.4 WHEN using bootstrapped ESG, THE System SHALL clearly indicate in the UI that scores are based on "Similar Brand Patterns" until the brand has >20 posts of their own

9.5 WHEN the brand's own ESG reaches 20 posts, THE System SHALL automatically transition from bootstrapped ESG to brand-specific ESG

9.6 THE System SHALL allow users to switch archetype if the initial selection doesn't feel aligned

9.7 THE System SHALL maintain separate storage for bootstrapped ESG and brand-specific ESG to prevent data contamination

## Non-Functional Requirements

### Performance

| ID | Requirement |
|----|-------------|
| NF-101 | Emotional Aligner SHALL complete analysis within 5 seconds |
| NF-102 | ChromaDB semantic query SHALL return in < 500ms for up to 1,000 posts |
| NF-103 | Sentence-transformer embedding SHALL run locally — zero external API dependency |
| NF-104 | ESG update pipeline SHALL run asynchronously and not block the UI |
| NF-105 | Dashboard metrics SHALL load within 2 seconds |
| NF-106 | Content generation SHALL complete within 8 seconds |
| NF-107 | Calendar view SHALL render within 1 second for up to 100 scheduled posts |

### Cost (Prototype Must Be $0)

| ID | Requirement |
|----|-------------|
| NF-201 | Prototype MUST operate at $0 marginal cost using free-tier services only |
| NF-202 | LLM calls SHALL use Gemini 1.5 Flash (free: 15 req/min, 1M tokens/day) or Groq (free) |
| NF-203 | Vector store SHALL use ChromaDB — local, open source, no cost |
| NF-204 | Database SHALL use Supabase free tier (500MB, 50k rows) |
| NF-205 | Embeddings SHALL run via sentence-transformers — local, no API cost |
| NF-206 | Frontend hosting SHALL use Vercel/Netlify free tier or local development |
| NF-207 | Backend SHALL run on local Flask server or free-tier cloud hosting |

### Responsible AI (Non-Negotiable)

| ID | Requirement |
|----|-------------|
| NF-301 | System SHALL always require human review before any post is published |
| NF-302 | System SHALL display which reference posts drove each AI scoring decision |
| NF-303 | Banned word detection SHALL name the specific flagged words visibly |
| NF-304 | System SHALL NOT auto-publish — human approval gate is required |
| NF-305 | AI-generated content SHALL be labeled as AI-assisted in internal metadata |
| NF-306 | System SHALL provide explainability for all Emotional Aligner scores |
| NF-307 | System SHALL allow users to override AI recommendations at any time |
| NF-308 | System SHALL log all AI decisions for audit and transparency |

### Usability

| ID | Requirement |
|----|-------------|
| NF-401 | Core workflow (idea → generate → score → schedule) SHALL complete in < 3 minutes |
| NF-402 | All error states SHALL show actionable messages, not raw API errors |
| NF-403 | UI SHALL be responsive and functional on screens ≥ 1024px |
| NF-404 | System SHALL provide inline help tooltips for all technical terms (ESG, ERS, EPM) |
| NF-405 | System SHALL use consistent color coding: green (good), yellow (warning), red (critical) |
| NF-406 | System SHALL provide visual feedback for all async operations (loading states) |

### Reliability

| ID | Requirement |
|----|-------------|
| NF-501 | System SHALL gracefully handle LLM API failures with retry logic (3 attempts, exponential backoff) |
| NF-502 | System SHALL persist ChromaDB data to disk for durability across restarts |
| NF-503 | System SHALL validate all user inputs and display clear error messages for invalid data |
| NF-504 | System SHALL handle concurrent users without data corruption (Supabase transactions) |
| NF-505 | System SHALL backup ESG data daily to prevent data loss |

### Security

| ID | Requirement |
|----|-------------|
| NF-601 | System SHALL store Supabase credentials in environment variables, never in code |
| NF-602 | System SHALL use Supabase Row Level Security (RLS) to isolate brand data |
| NF-603 | System SHALL sanitize all user inputs to prevent injection attacks |
| NF-604 | System SHALL use HTTPS for all API communications in production |
| NF-605 | System SHALL implement rate limiting on API endpoints to prevent abuse |

## Tech Stack Requirements

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | React + TypeScript + Vite | Type safety, fast DX, no framework lock-in |
| Backend | Python Flask | Lightweight, instant REST APIs, excellent ML library support |
| Embeddings | sentence-transformers (local) | Zero cost, 384-dim vectors, runs offline |
| Vector DB | ChromaDB (persistent, local) | Open source, cosine similarity built-in, $0 |
| LLM | Gemini 1.5 Flash / Groq Llama 3.1 | Free tiers adequate for prototype scale |
| Database | Supabase PostgreSQL | Free tier, REST API, production-ready auth |
| Storage | Supabase Storage | Logo/asset hosting for Brand DNA |
| Cloud | AWS (EC2, S3, CloudFront) | Hackathon sponsor, production deployment path |

## AWS Integration Opportunities (Future Roadmap)

| AWS Service | Use Case | Stage |
|------------|----------|-------|
| Amazon S3 | Store brand assets, CSVs, post media | Production |
| AWS EC2 / Elastic Beanstalk | Host Flask backend | Production |
| Amazon Bedrock | Replace Gemini with Claude/Titan for enterprise clients | V2 |
| Amazon Comprehend | Supplement comment sentiment analysis | V2 |
| Amazon Rekognition | Analyze image content for visual ESG | V3 |
| Amazon SageMaker | Fine-tune embedding model on Indian language content | V3 |
| CloudFront + S3 | CDN for React frontend | Production |

## Success Metrics

| Metric | Target |
|--------|--------|
| Emotional Aligner prediction accuracy (predicted vs actual ERS) | < 15% delta after 50 posts |
| End-to-end draft scoring latency | < 5 seconds |
| User task completion rate (idea → schedule) | > 85% error-free |
| Banned word detection recall | 100% |
| Cold-start EPM satisfaction (user rating) | > 3.5 / 5.0 |
| Dashboard load time | < 2 seconds |
| ESG query response time | < 500ms |
| User retention (return within 7 days) | > 60% |
