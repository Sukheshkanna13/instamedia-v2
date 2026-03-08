// ─── Brand DNA ───────────────────────────────────────────────────────────────
export interface BrandDNA {
  brand_id: string;
  brand_name: string;
  mission: string;
  tone_descriptors: string[];   // e.g. ["bold", "empathetic", "direct"]
  hex_colors: string[];   // e.g. ["#FF3CAC", "#00E5FF"]
  banned_words: string[];   // e.g. ["cheap", "simple"]
  typography: string;
  logo_url: string;
  updated_at?: string;
  connected_platforms?: string[]; // NEW: ["instagram", "linkedin", "twitter"]
}

// ─── AWS S3 Pre-Signed URL (NEW) ─────────────────────────────────────────────
export interface PresignedUrlResponse {
  upload_url: string;
  fields: Record<string, string>;
  filename: string;
}

// ─── OAuth Flow (NEW) ─────────────────────────────────────────────────────────
export interface OAuthInitResponse {
  auth_url: string;
  state: string;
}

// ─── ESG / Emotional Scoring ─────────────────────────────────────────────────
export type Verdict = "STRONG_MATCH" | "GOOD_MATCH" | "WEAK_MATCH" | "MISMATCH" | "PARSE_ERROR";

export interface AnalysisResult {
  resonance_score: number;
  verdict: Verdict;
  emotional_archetype: string;
  what_works: string;
  what_is_missing: string;
  missing_signals: string[];
  rewrite_suggestion: string;
  banned_words_found: string[];
  confidence: "HIGH" | "MEDIUM" | "LOW";
  error?: string;
}

export interface AnalyzeResponse {
  success: boolean;
  draft: string;
  analysis: AnalysisResult;
  reference_posts: ReferencePost[];
  processing_time_seconds: number;
  db_size: number;
  banned_words_found: string[];
}

export interface ReferencePost {
  text: string;
  ers: number;
  semantic_sim: number;
  platform: string;
}

// ─── Content Ideas ────────────────────────────────────────────────────────────
export interface ContentIdea {
  id: string;
  title: string;
  hook: string;
  angle: string;
  platform: "Instagram" | "LinkedIn" | "Both";
  predicted_ers: number;
}

export interface IdeateResponse {
  success: boolean;
  result: { ideas: ContentIdea[] };
}

// ─── Studio Generated Post ────────────────────────────────────────────────────
export interface GeneratedPost {
  post_text: string;
  hashtags: string[];
  image_style_prompt: string;
  cta: string;
  word_count: number;
}

export interface StudioGenerateResponse {
  success: boolean;
  result: GeneratedPost;
}

// ─── Multi-Modal Media Generation (Phase 6) ───────────────────────────────────
export type MediaFormat = "image" | "carousel" | "video";

export interface CarouselSlide {
  slide_number: number;
  title: string;
  content: string;
  image_url?: string;
}

export interface VideoScene {
  scene_number: number;
  description: string;
  duration: string;
  image_url?: string;
}

export interface GeneratedMedia {
  format: MediaFormat;
  image_url?: string;                // For single image
  slides?: CarouselSlide[];       // For carousel (3-5 slides)
  storyboard?: VideoScene[];          // For video (5-8 scenes)
  caption: string;
  hashtags: string[];
  generation_time_seconds: number;
}

export interface MediaGenerateResponse {
  success: boolean;
  result: GeneratedMedia;
}

// ─── Scheduled Posts / Calendar ───────────────────────────────────────────────
export type PostStatus = "scheduled" | "published" | "draft";
export type Platform = "instagram" | "linkedin" | "twitter" | "tiktok" | "both";

export interface ScheduledPost {
  id: string;
  content: string;
  platform: Platform;
  scheduled_time: string;          // ISO datetime string
  brand_id: string;
  resonance_score: number;
  image_style: string;
  hashtags: string | string[];
  status: PostStatus;
  created_at: string;
}

export interface CalendarPost extends ScheduledPost {
  title?: string;   // derived from content preview for calendar display
  start: Date;
  end: Date;
}

// ─── Dashboard Stats ─────────────────────────────────────────────────────────
export interface DashboardStats {
  total_content: number;
  scheduled: number;
  published: number;
  avg_resonance_score: number;
  db_post_count: number;
}

export interface ERSStats {
  total_posts: number;
  avg_ers: number;
  max_ers: number;
  min_ers: number;
  top_posts: Array<{ text: string; ers: number; platform: string }>;
}

// ─── Generator ────────────────────────────────────────────────────────────────
export interface GeneratorVariation {
  text: string;
  emotional_angle: string;
  predicted_ers: number;
}

export interface GeneratorResponse {
  success: boolean;
  topic: string;
  result: {
    archetype_detected: string;
    variations: GeneratorVariation[];
  };
}

// ─── API state helpers ────────────────────────────────────────────────────────
export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export type Tab = "overview" | "dna" | "ideation" | "studio" | "calendar" | "library" | "connections" | "database" | "drift" | "coldstart" | "analytics" | "ads_manager";

export interface NavItem {
  id: Tab;
  label: string;
  icon: string;
}

// ─── ADs Intelligence ─────────────────────────────────────────────────────────

export interface AdScraperResult {
  platform: string;
  ad_id: string;
  headline: string;
  body: string;
  page_name?: string;
  channel_name?: string;
  preview_url: string;
  video_url?: string;
  impressions_lower?: number;
  spend_lower?: number;
  views?: number;
  efficiency_score: number;
  niche: string;
  similarity_score?: number;
}

export interface CampaignRecommendations {
  headlines?: string[];
  body_copies?: { short?: string; medium?: string; long?: string };
  hooks?: string[];
  ctas?: string[];
  creative_direction?: { visuals?: string; colors?: string; formats?: string; inspiration_from_top_ads?: string };
  targeting_suggestions?: { interests?: string[]; behaviors?: string[]; demographics?: string; lookalike_seed?: string };
  budget_allocation?: { META?: string; YOUTUBE?: string; rationale?: string };
  error?: string;
}

export interface AdRecommendationResponse {
  brief_used?: string;
  recommendations?: CampaignRecommendations;
  retrieved_ads?: AdScraperResult[];
  error?: string;
}

export interface MarketingIntelligenceResponse {
  market_research?: any;
  campaign_tuning?: any;
  analytics_insights?: any;
}

export interface FullCampaignResponse {
  scrape_summary?: any;
  ad_recommendations?: AdRecommendationResponse;
  marketing_intelligence?: MarketingIntelligenceResponse;
}
