-- ═══════════════════════════════════════════════════════════
-- InstaMedia AI v2 — Supabase Schema
-- Run this entire file in your Supabase SQL Editor
-- Dashboard → SQL Editor → New Query → Paste → Run
-- ═══════════════════════════════════════════════════════════

-- ── BRAND DNA TABLE ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS brand_dna (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id        TEXT NOT NULL UNIQUE,     -- e.g. "default" or user's org ID
  brand_name      TEXT DEFAULT '',
  mission         TEXT DEFAULT '',
  tone_descriptors JSONB DEFAULT '[]',      -- ["empathetic", "bold"]
  hex_colors      JSONB DEFAULT '[]',       -- ["#FF3CAC", "#00E5FF"]
  banned_words    JSONB DEFAULT '[]',       -- ["cheap", "simple"]
  typography      TEXT DEFAULT '',
  logo_url        TEXT DEFAULT '',
  updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── SCHEDULED POSTS TABLE ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS scheduled_posts (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id        TEXT NOT NULL DEFAULT 'default',
  content         TEXT NOT NULL,
  platform        TEXT NOT NULL DEFAULT 'instagram',  -- instagram|linkedin|twitter|tiktok
  scheduled_time  TIMESTAMPTZ NOT NULL,
  status          TEXT NOT NULL DEFAULT 'scheduled',  -- scheduled|published|draft
  resonance_score INTEGER DEFAULT 0,       -- ERS score from the Emotional Aligner
  image_style     TEXT DEFAULT '',         -- AI-generated image style brief
  hashtags        JSONB DEFAULT '[]',      -- ["marketing", "startup"]
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── INDEXES ───────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_brand_dna_brand_id       ON brand_dna(brand_id);
CREATE INDEX IF NOT EXISTS idx_posts_brand_id            ON scheduled_posts(brand_id);
CREATE INDEX IF NOT EXISTS idx_posts_status              ON scheduled_posts(status);
CREATE INDEX IF NOT EXISTS idx_posts_scheduled_time      ON scheduled_posts(scheduled_time);

-- ── ROW LEVEL SECURITY (optional — enable for multi-user) ─────────────────────
-- ALTER TABLE brand_dna       ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE scheduled_posts ENABLE ROW LEVEL SECURITY;

-- For prototype: allow all anon reads/writes (fine for demo)
-- In production: scope to authenticated users

-- ── SEED SAMPLE DATA (optional — for demo purposes) ──────────────────────────
INSERT INTO brand_dna (brand_id, brand_name, mission, tone_descriptors, hex_colors, banned_words)
VALUES (
  'default',
  'Demo Brand',
  'We help founders build companies that outlast trends by staying deeply honest with their audience.',
  '["Vulnerable", "Bold", "Direct", "Human"]',
  '["#00D4B8", "#FF5757", "#A78BFA"]',
  '["cheap", "simple", "just", "amazing", "revolutionary"]'
) ON CONFLICT (brand_id) DO NOTHING;

-- ── VERIFY ────────────────────────────────────────────────────────────────────
SELECT 'brand_dna rows: ' || COUNT(*)::text AS check FROM brand_dna;
SELECT 'scheduled_posts rows: ' || COUNT(*)::text AS check FROM scheduled_posts;
