// ─── Brand DNA ───────────────────────────────────────────────────────────────
export interface BrandDNA {
  brand_id:         string;
  brand_name:       string;
  mission:          string;
  tone_descriptors: string[];   // e.g. ["bold", "empathetic", "direct"]
  hex_colors:       string[];   // e.g. ["#FF3CAC", "#00E5FF"]
  banned_words:     string[];   // e.g. ["cheap", "simple"]
  typography:       string;
  logo_url:         string;
  updated_at?:      string;
}

// ─── ESG / Emotional Scoring ─────────────────────────────────────────────────
export type Verdict = "STRONG_MATCH" | "GOOD_MATCH" | "WEAK_MATCH" | "MISMATCH" | "PARSE_ERROR";

export interface AnalysisResult {
  resonance_score:     number;
  verdict:             Verdict;
  emotional_archetype: string;
  what_works:          string;
  what_is_missing:     string;
  missing_signals:     string[];
  rewrite_suggestion:  string;
  banned_words_found:  string[];
  confidence:          "HIGH" | "MEDIUM" | "LOW";
  error?:              string;
}

export interface AnalyzeResponse {
  success:                  boolean;
  draft:                    string;
  analysis:                 AnalysisResult;
  reference_posts:          ReferencePost[];
  processing_time_seconds:  number;
  db_size:                  number;
  banned_words_found:       string[];
}

export interface ReferencePost {
  text:         string;
  ers:          number;
  semantic_sim: number;
  platform:     string;
}

// ─── Content Ideas ────────────────────────────────────────────────────────────
export interface ContentIdea {
  id:            string;
  title:         string;
  hook:          string;
  angle:         string;
  platform:      "Instagram" | "LinkedIn" | "Both";
  predicted_ers: number;
}

export interface IdeateResponse {
  success: boolean;
  result:  { ideas: ContentIdea[] };
}

// ─── Studio Generated Post ────────────────────────────────────────────────────
export interface GeneratedPost {
  post_text:          string;
  hashtags:           string[];
  image_style_prompt: string;
  cta:                string;
  word_count:         number;
}

export interface StudioGenerateResponse {
  success: boolean;
  result:  GeneratedPost;
}

// ─── Scheduled Posts / Calendar ───────────────────────────────────────────────
export type PostStatus = "scheduled" | "published" | "draft";
export type Platform   = "instagram" | "linkedin" | "twitter" | "tiktok" | "both";

export interface ScheduledPost {
  id:               string;
  content:          string;
  platform:         Platform;
  scheduled_time:   string;          // ISO datetime string
  brand_id:         string;
  resonance_score:  number;
  image_style:      string;
  hashtags:         string | string[];
  status:           PostStatus;
  created_at:       string;
}

export interface CalendarPost extends ScheduledPost {
  title?: string;   // derived from content preview for calendar display
  start:  Date;
  end:    Date;
}

// ─── Dashboard Stats ─────────────────────────────────────────────────────────
export interface DashboardStats {
  total_content:       number;
  scheduled:           number;
  published:           number;
  avg_resonance_score: number;
  db_post_count:       number;
}

export interface ERSStats {
  total_posts: number;
  avg_ers:     number;
  max_ers:     number;
  min_ers:     number;
  top_posts:   Array<{ text: string; ers: number; platform: string }>;
}

// ─── Generator ────────────────────────────────────────────────────────────────
export interface GeneratorVariation {
  text:            string;
  emotional_angle: string;
  predicted_ers:   number;
}

export interface GeneratorResponse {
  success: boolean;
  topic:   string;
  result:  {
    archetype_detected: string;
    variations:         GeneratorVariation[];
  };
}

// ─── API state helpers ────────────────────────────────────────────────────────
export interface AsyncState<T> {
  data:    T | null;
  loading: boolean;
  error:   string | null;
}

export type Tab = "overview" | "dna" | "ideation" | "studio" | "calendar" | "library";

export interface NavItem {
  id:    Tab;
  label: string;
  icon:  string;
}
