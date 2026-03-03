import type {
  BrandDNA, AnalyzeResponse, IdeateResponse,
  StudioGenerateResponse, ScheduledPost, DashboardStats,
  ERSStats, GeneratorResponse, PresignedUrlResponse, OAuthInitResponse,
  MediaGenerateResponse
} from "../types";

const BASE = "";

// API Gateway timeout protection: 28s client-side timeout (1s buffer before 29s gateway timeout)
const API_TIMEOUT_MS = 28000;

// Retry configuration
const MAX_RETRIES = 2;
const RETRY_DELAY_MS = 1000;

interface RequestOptions extends RequestInit {
  timeout?: number;
  retries?: number;
}

async function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function requestWithTimeout<T>(
  path: string,
  init?: RequestOptions
): Promise<T> {
  const timeout = init?.timeout ?? API_TIMEOUT_MS;
  const retries = init?.retries ?? 0;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const res = await fetch(`${BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: res.statusText }));

      // Check if error suggests retry
      if (res.status === 503 && retries > 0) {
        await sleep(RETRY_DELAY_MS);
        return requestWithTimeout<T>(path, { ...init, retries: retries - 1 });
      }

      throw new Error((err as { error: string; retry?: boolean }).error ?? res.statusText);
    }

    return res.json() as Promise<T>;
  } catch (error) {
    clearTimeout(timeoutId);

    // Handle timeout errors
    if (error instanceof Error && error.name === 'AbortError') {
      if (retries > 0) {
        await sleep(RETRY_DELAY_MS);
        return requestWithTimeout<T>(path, { ...init, retries: retries - 1 });
      }
      throw new Error('Request timed out. The AI is taking longer than expected. Please try again.');
    }

    throw error;
  }
}

const post = <T>(path: string, body: unknown, options?: RequestOptions) =>
  requestWithTimeout<T>(path, {
    method: "POST",
    body: JSON.stringify(body),
    retries: MAX_RETRIES,
    ...options
  });

const get = <T>(path: string, options?: RequestOptions) =>
  requestWithTimeout<T>(path, { retries: MAX_RETRIES, ...options });

// ─── API surface ─────────────────────────────────────────────────────────────
export const api = {
  health: () => get<{
    status: string; posts_in_chromadb: number;
    supabase_connected: boolean; llm_provider: string
  }>("/api/health"),

  seed: () => post<{ success: boolean; added: number; total: number }>("/api/seed", {}),

  // Brand DNA
  getBrandDNA: (brandId = "default") =>
    get<{ success: boolean; data: Partial<BrandDNA> }>(`/api/brand-dna?brand_id=${brandId}`),

  saveBrandDNA: (data: Partial<BrandDNA>) =>
    post<{ success: boolean }>("/api/brand-dna", data),

  // ESG Core - with extended timeout for large operations
  analyze: (draft: string, brandId = "default") =>
    post<AnalyzeResponse>("/api/analyze", { draft, brand_id: brandId }, { timeout: 25000 }),

  // S3 Pre-Signed URL for CSV upload (NEW - bypasses API Gateway 10MB limit)
  getPresignedUrl: (brandId = "default") =>
    get<PresignedUrlResponse>(`/api/esg/presigned-url?brand_id=${brandId}`),

  // Upload CSV directly to S3 using pre-signed URL
  uploadToS3: async (presignedData: PresignedUrlResponse, file: File) => {
    const formData = new FormData();
    Object.entries(presignedData.fields).forEach(([key, value]) => {
      formData.append(key, value);
    });
    formData.append('file', file);

    const response = await fetch(presignedData.upload_url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload file to S3');
    }

    return presignedData.filename;
  },

  // Trigger ESG ingestion after S3 upload
  ingestESG: (filename: string, brandId = "default") =>
    post<{ success: boolean; message: string; status: string }>(
      "/api/esg/upload",
      { filename, brand_id: brandId },
      { timeout: 25000 } // May trigger async Step Functions for large CSVs
    ),

  // Ideation - with extended timeout for LLM generation
  ideate: (brandId = "default", focusArea?: string) =>
    post<IdeateResponse>("/api/ideate", { brand_id: brandId, focus_area: focusArea }, { timeout: 25000 }),

  // Studio - with extended timeout for LLM generation
  studioGenerate: (params: {
    idea_title: string; idea_hook: string;
    angle: string; platform: string; brand_id?: string;
  }) => post<StudioGenerateResponse>("/api/studio/generate", params, { timeout: 25000 }),

  // Multi-Modal Media Generation (Phase 6) - with extended timeout for image generation
  generateMedia: (params: {
    caption: string;
    hashtags: string[];
    format: 'image' | 'carousel' | 'video';
    brand_id?: string;
  }) => post<MediaGenerateResponse>("/api/studio/generate-media", params, { timeout: 45000 }),

  // Generator (simple)
  generate: (topic: string) =>
    post<GeneratorResponse>("/api/generate", { topic }, { timeout: 25000 }),

  // OAuth Flow (NEW)
  initiateOAuth: (platform: 'instagram' | 'linkedin' | 'twitter') =>
    get<OAuthInitResponse>(`/api/auth/${platform}`),

  // Calendar / Posts
  schedulePost: (params: Partial<ScheduledPost>) =>
    post<{ success: boolean; post: ScheduledPost }>("/api/posts/schedule", params),

  deletePost: (postId: string, brandId = "default") =>
    requestWithTimeout<{ success: boolean; message: string }>(`/api/posts/${postId}?brand_id=${brandId}`, { method: "DELETE" }),

  reschedulePost: (postId: string, newTime: string, brandId = "default") =>
    requestWithTimeout<{ success: boolean; post: ScheduledPost }>(`/api/posts/${postId}/reschedule`, { method: "PUT", body: JSON.stringify({ scheduled_time: newTime, brand_id: brandId }) }),

  getCalendarPosts: (brandId = "default") =>
    get<{ success: boolean; posts: ScheduledPost[] }>(`/api/posts/calendar?brand_id=${brandId}`),

  getRecentPosts: (brandId = "default", limit = 5) =>
    get<{ success: boolean; posts: ScheduledPost[] }>(`/api/posts/recent?brand_id=${brandId}&limit=${limit}`),

  getPostStats: (brandId = "default") =>
    get<DashboardStats>(`/api/posts/stats?brand_id=${brandId}`),

  // ERS stats
  getERSStats: () => get<ERSStats>("/api/stats"),

  getPosts: () => get<{ posts: Array<{ text: string; ers: number; likes: number; comments: number; shares: number; platform: string }> }>("/api/posts"),

  // Database Expansion (NEW)
  scrapePosts: (keywords: string, platforms: string[], count: number = 20) =>
    post<{
      success: boolean;
      scraped_posts: Array<{
        text: string;
        likes: number;
        comments: number;
        shares: number;
        platform: string;
        emotion: string;
        ers: number;
      }>;
      added_count: number;
      mode: string;
      message: string;
    }>("/api/database/scrape", { keywords, platforms, count }),

  addScrapedPosts: (posts: Array<{
    text: string;
    likes: number;
    comments: number;
    shares: number;
    platform: string;
  }>) =>
    post<{
      success: boolean;
      added_count: number;
      total_posts: number;
      message: string;
    }>("/api/database/add-posts", { posts }),

  getDatabaseStats: () =>
    get<{
      total_posts: number;
      avg_ers: number;
      max_ers: number;
      min_ers: number;
      platforms: Record<string, number>;
      emotions: Record<string, number>;
      sources: Record<string, number>;
    }>("/api/database/stats"),
};
