"""One-time ingestion script for the Parista knowledge base.

Reads text content from ``data/core_papers/`` and ``data/markdown/``, chunks
each document into 300-500 word passages (preserving paragraph boundaries),
tags each chunk with domain / framework_name / conflict_stage via a manual
mapping keyed by filename, generates a 768-dim embedding with
``backend/modules/embeddings.py`` (gemini-embedding-001), and inserts each
chunk into the ``psychology_kb_chunks`` table via ``backend/modules/db/client.py``.

Run directly with::

    python -m backend.modules.ingestion.ingest_papers
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from backend.modules.chat.logging import get_logger
from backend.modules.db.client import get_supabase_client
from backend.modules.embeddings import get_embedding

logger = get_logger("ingestion")

# Repository root (two levels up from this file: backend/modules/ingestion).
REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIRS = (REPO_ROOT / "data" / "core_papers", REPO_ROOT / "data" / "markdown")

# Target chunk size in words (300-500 per the task).
MIN_CHUNK_WORDS = 300
MAX_CHUNK_WORDS = 500

# Manual mapping of curated source files to their known framework metadata.
# Keyed by filename (case-insensitive). Unknown files fall back to
# domain="general", framework_name=None, conflict_stage=None.
#
# Add entries here as curated sources are added to data/core_papers/ or
# data/markdown/.
SOURCE_METADATA: dict[str, dict] = {
    # Example entries — extend with the actual curated sources.
    # "downey_feldman_1996.txt": {
    #     "domain": "romantic",
    #     "framework_name": "Rejection Sensitivity",
    #     "conflict_stage": "acute",
    # },
    # "gottman_conflict_styles.md": {
    #     "domain": "romantic",
    #     "framework_name": "Gottman Conflict Styles",
    #     "conflict_stage": "reflection",
    # },
}

# File extensions treated as text.
TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".text"}


def iter_source_files() -> list[Path]:
    """Return all text files under the data directories, sorted by path."""
    files: list[Path] = []
    for data_dir in DATA_DIRS:
        if not data_dir.exists():
            continue
        for path in sorted(data_dir.iterdir()):
            if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
                files.append(path)
    return files


def read_text(path: Path) -> str:
    """Read a text file, tolerating common encodings."""
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    # Last resort: read with errors ignored.
    return path.read_text(encoding="utf-8", errors="ignore")


def chunk_text(text: str) -> list[str]:
    """Split text into 300-500 word chunks, preserving paragraph boundaries.

    Paragraphs are accumulated until the running chunk reaches at least
    ``MIN_CHUNK_WORDS`` words; a new chunk starts when adding the next
    paragraph would exceed ``MAX_CHUNK_WORDS``.
    """
    # Normalize whitespace and split into non-empty paragraphs.
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks: list[str] = []
    current: list[str] = []
    current_words = 0

    for paragraph in paragraphs:
        para_words = len(paragraph.split())

        # A single paragraph larger than MAX becomes its own chunk (split by
        # sentence boundaries as a fallback).
        if para_words > MAX_CHUNK_WORDS:
            if current:
                chunks.append("\n\n".join(current))
                current, current_words = [], 0
            chunks.extend(_split_oversized_paragraph(paragraph))
            continue

        # Start a new chunk if adding this paragraph would exceed MAX.
        if current and current_words + para_words > MAX_CHUNK_WORDS:
            chunks.append("\n\n".join(current))
            current, current_words = [], 0

        current.append(paragraph)
        current_words += para_words

        # Flush once we've reached the minimum size.
        if current_words >= MIN_CHUNK_WORDS:
            chunks.append("\n\n".join(current))
            current, current_words = [], 0

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def _split_oversized_paragraph(paragraph: str) -> list[str]:
    """Split a single oversized paragraph into sentence-bounded chunks."""
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    chunks: list[str] = []
    current: list[str] = []
    current_words = 0

    for sentence in sentences:
        sentence_words = len(sentence.split())
        if current and current_words + sentence_words > MAX_CHUNK_WORDS:
            chunks.append(" ".join(current))
            current, current_words = [], 0
        current.append(sentence)
        current_words += sentence_words

    if current:
        chunks.append(" ".join(current))

    return chunks


def metadata_for(path: Path) -> dict:
    """Return domain / framework_name / conflict_stage for a source file."""
    key = path.name.lower()
    meta = SOURCE_METADATA.get(key, {})
    return {
        "domain": meta.get("domain", "general"),
        "framework_name": meta.get("framework_name"),
        "conflict_stage": meta.get("conflict_stage"),
    }


def insert_chunk(client, content: str, meta: dict, embedding: list[float]) -> None:
    """Insert a single chunk into psychology_kb_chunks."""
    client.table("psychology_kb_chunks").insert(
        {
            "source_title": meta["source_title"],
            "domain": meta["domain"],
            "framework_name": meta["framework_name"],
            "conflict_stage": meta["conflict_stage"],
            "content": content,
            "embedding": embedding,
        }
    ).execute()


def ingest() -> None:
    """Run the full ingestion pipeline."""
    files = iter_source_files()
    if not files:
        print("No source files found in data/core_papers/ or data/markdown/.")
        print("Add curated text files there, then re-run this script.")
        return

    client = get_supabase_client()

    total_chunks = 0
    papers_processed = 0

    for path in files:
        text = read_text(path)
        chunks = chunk_text(text)
        meta = metadata_for(path)
        meta["source_title"] = path.stem

        for chunk in chunks:
            embedding = get_embedding(chunk)
            insert_chunk(client, chunk, meta, embedding)
            total_chunks += 1
            print(f"  chunk {total_chunks}: {path.name} ({len(chunk.split())} words)")

        papers_processed += 1
        print(f"Processed {path.name}: {len(chunks)} chunks")

    print(f"\nDone. Papers processed: {papers_processed}, total chunks inserted: {total_chunks}")


if __name__ == "__main__":
    try:
        ingest()
    except Exception as exc:  # pragma: no cover - top-level error reporting
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)