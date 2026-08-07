-- Parista Supabase schema
-- Tables: users, conversations, messages, psychology_kb_chunks, style_examples, paper_cache

-- Enable pgvector extension for the knowledge base embeddings
create extension if not exists vector;

-- Users — supports three access modes:
--   1. Telegram bot            -> telegram_id (persistent, from Telegram)
--   2. Web app without login   -> web_session_id (ephemeral, anonymous session)
--   3. Web app with login      -> email + auth_provider (persistent account via
--                                 Supabase Auth)
--
-- If we adopt Supabase's built-in auth (auth.users), this table can reference
-- it as a foreign key. If we handle auth manually, this remains a standalone
-- table. The FK reference is commented out so we can decide later without
-- blocking current progress:
--   user_id uuid references auth.users(id) on delete cascade,
create table if not exists users (
    id uuid primary key default gen_random_uuid(),
    telegram_id text unique,
    web_session_id text unique,
    email text unique,
    auth_provider text check (auth_provider in ('telegram', 'anonymous', 'email', 'google', 'github')),
    display_name text,
    last_login_at timestamptz,
    created_at timestamptz not null default now(),
    -- A user is valid if ANY of telegram_id, web_session_id, or email is set
    constraint users_identifier_check check (
        telegram_id is not null or web_session_id is not null or email is not null
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

-- RPC function for pgvector similarity search (used by vector_search_tool)
create or replace function match_psychology_kb_chunks(
    query_embedding vector(768),
    match_count int default 5
)
returns table (
    id uuid,
    source_title text,
    framework_name text,
    content text,
    similarity float
)
language plpgsql
as $$
begin
    return query
    select
        psychology_kb_chunks.id,
        psychology_kb_chunks.source_title,
        psychology_kb_chunks.framework_name,
        psychology_kb_chunks.content,
        1 - (psychology_kb_chunks.embedding <=> query_embedding) as similarity
    from psychology_kb_chunks
    order by psychology_kb_chunks.embedding <=> query_embedding
    limit match_count;
end;
$$;