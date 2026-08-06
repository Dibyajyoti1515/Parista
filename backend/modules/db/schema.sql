-- Parista Supabase schema
-- Tables: users, conversations, messages, psychology_kb_chunks, style_examples, paper_cache

-- Enable pgvector extension for the knowledge base embeddings
create extension if not exists vector;

-- Users (Telegram or web frontend)
create table if not exists users (
    id uuid primary key default gen_random_uuid(),
    telegram_id text unique,
    web_session_id text unique,
    created_at timestamptz not null default now(),
    -- At least one of telegram_id or web_session_id must be set
    constraint users_identifier_check check (
        telegram_id is not null or web_session_id is not null
    )
);

-- Conversations (multi-turn context)
create table if not exists conversations (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users(id) on delete cascade,
    created_at timestamptz not null default now()
);

-- Messages (single exchange in a conversation)
create table if not exists messages (
    id uuid primary key default gen_random_uuid(),
    conversation_id uuid not null references conversations(id) on delete cascade,
    role text not null check (role in ('user', 'agent')),
    content text not null,
    created_at timestamptz not null default now()
);

-- Psychology knowledge base chunks (core KB, pgvector)
create table if not exists psychology_kb_chunks (
    id uuid primary key default gen_random_uuid(),
    source_title text not null,
    domain text not null check (domain in ('romantic', 'family', 'workplace', 'general')),
    framework_name text,
    conflict_stage text check (conflict_stage in ('acute', 'reflection', 'resolution')),
    content text not null,
    embedding vector(768)
);

-- Index for similarity search on the embedding column
create index if not exists psychology_kb_chunks_embedding_idx
    on psychology_kb_chunks using hnsw (embedding vector_cosine_ops);

-- Style examples (Reddit-sourced tone layer)
create table if not exists style_examples (
    id uuid primary key default gen_random_uuid(),
    text text not null,
    tone text check (tone in ('casual', 'formal', 'playful', 'serious')),
    age_bracket_fit text,
    situation_type text,
    source_url text,
    fetched_at timestamptz not null default now()
);

-- Paper cache (real-time Semantic Scholar fallback)
create table if not exists paper_cache (
    id uuid primary key default gen_random_uuid(),
    query text not null,
    title text,
    abstract text,
    source_url text,
    fetched_at timestamptz not null default now()
);