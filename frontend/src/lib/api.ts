import type {
  BrandDNA, AnalyzeResponse, IdeateResponse,
  StudioGenerateResponse, ScheduledPost, DashboardStats,
  ERSStats, GeneratorResponse
} from "../types";

const BASE = "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error((err as { error: string }).error ?? res.statusText);
  }
  return res.json() as Promise<T>;
}

const post = <T>(path: string, body: unknown) =>
  request<T>(path, { method: "POST", body: JSON.stringify(body) });

const get = <T>(path: string) => request<T>(path);

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

  // ESG Core
  analyze: (draft: string, brandId = "default") =>
    post<AnalyzeResponse>("/api/analyze", { draft, brand_id: brandId }),

  // Ideation
  ideate: (brandId = "default", focusArea?: string) =>
    post<IdeateResponse>("/api/ideate", { brand_id: brandId, focus_area: focusArea }),

  // Studio
  studioGenerate: (params: {
    idea_title: string; idea_hook: string;
    angle: string; platform: string; brand_id?: string;
  }) => post<StudioGenerateResponse>("/api/studio/generate", params),

  // Generator (simple)
  generate: (topic: string) =>
    post<GeneratorResponse>("/api/generate", { topic }),

  // Calendar / Posts
  schedulePost: (params: Partial<ScheduledPost>) =>
    post<{ success: boolean; post: ScheduledPost }>("/api/posts/schedule", params),

  getCalendarPosts: (brandId = "default") =>
    get<{ success: boolean; posts: ScheduledPost[] }>(`/api/posts/calendar?brand_id=${brandId}`),

  getRecentPosts: (brandId = "default", limit = 5) =>
    get<{ success: boolean; posts: ScheduledPost[] }>(`/api/posts/recent?brand_id=${brandId}&limit=${limit}`),

  getPostStats: (brandId = "default") =>
    get<DashboardStats>(`/api/posts/stats?brand_id=${brandId}`),

  // ERS stats
  getERSStats: () => get<ERSStats>("/api/stats"),

  getPosts: () => get<{ posts: Array<{ text: string; ers: number; likes: number; comments: number; shares: number; platform: string }> }>("/api/posts"),
};
