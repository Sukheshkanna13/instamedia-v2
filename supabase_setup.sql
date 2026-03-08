-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- 1. Create the posts_embeddings table for LangGraph RAG
create table if not exists public.posts_embeddings (
    id uuid primary key default gen_random_uuid(),
    document text not null,
    content text,
    embedding vector(768), -- text-embedding-004 uses 768 dimensions
    ers real default 0,
    likes integer default 0,
    comments integer default 0,
    shares integer default 0,
    platform text,
    metadata jsonb default '{}'::jsonb,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Recommended: create an index for faster similarity searches (HNSW)
create index on public.posts_embeddings using hnsw (embedding vector_cosine_ops);

-- 2. Create the match_posts function for LangGraph semantic search
create or replace function match_posts (
  query_embedding vector(768),
  match_threshold float,
  match_count int,
  filter_brand_id text default null,
  min_ers float default null
)
returns table (
  id uuid,
  document text,
  ers real,
  platform text,
  similarity float
)
language sql stable
as $$
  select
    posts_embeddings.id,
    posts_embeddings.document,
    posts_embeddings.ers,
    posts_embeddings.platform,
    1 - (posts_embeddings.embedding <=> query_embedding) as similarity
  from posts_embeddings
  where 1 - (posts_embeddings.embedding <=> query_embedding) > match_threshold
    and (
      filter_brand_id is null 
      or posts_embeddings.metadata->>'brand_id' = filter_brand_id 
      or posts_embeddings.metadata->>'brand_id' is null
    )
    and (min_ers is null or posts_embeddings.ers >= min_ers)
  order by posts_embeddings.embedding <=> query_embedding
  limit match_count;
$$;

-- 3. Create the brand_dna table for the frontend dashboard
create table if not exists public.brand_dna (
    id uuid primary key default gen_random_uuid(),
    brand_id text unique not null,
    brand_name text,
    mission text,
    tone_descriptors text, -- stored as JSON string from API
    hex_colors text, -- stored as JSON string from API
    banned_words text, -- stored as JSON string from API
    typography text,
    logo_url text,
    connected_platforms text, -- stored as JSON string from API
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 4. Create the scheduled_posts table for the calendar
create table if not exists public.scheduled_posts (
    id uuid primary key default gen_random_uuid(),
    brand_id text not null,
    content text,
    platform text,
    scheduled_time text,
    resonance_score real default 0,
    image_style text,
    hashtags text, -- stored as JSON string from API
    status text default 'scheduled',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create the storage bucket for brand logos if using Supabase Storage
insert into storage.buckets (id, name, public) 
values ('brand-logos', 'brand-logos', true) 
on conflict (id) do nothing;
