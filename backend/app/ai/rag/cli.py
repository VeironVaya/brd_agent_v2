"""
app/rag/cli.py
==============
CLI tool for operators to ingest approved reference BRDs into PostgreSQL + pgvector.

Usage:
    python -m app.rag.cli --all
    python -m app.rag.cli --document 1
    python -m app.rag.cli --all --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

from app.config import settings
from .embeddings import EmbeddingGenerator
from .ingest.chunker import create_chunks
from .ingest.loader import load_document
from .ingest.parser import parse_document
from .ingest.repository import ReferenceRepository
from .ingest.validator import validate_ingest


BACKEND_DIR = Path(__file__).resolve().parents[2]
CORPUS_PATH = Path(__file__).resolve().parent / "config" / "reference_corpus.json"
SOURCE_DIR = BACKEND_DIR / "data" / "reference_brds"


def load_corpus() -> list[dict]:
    if not CORPUS_PATH.exists():
        raise FileNotFoundError(f"Corpus configuration not found at {CORPUS_PATH}")
    config = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    return config["documents"]


def find_source_file(sequence: int) -> Path:
    pattern = re.compile(rf"^\s*{sequence}\s*-\s*")
    matches = [
        p for p in SOURCE_DIR.iterdir()
        if p.is_file() and p.suffix.lower() == ".docx" and pattern.match(p.name)
    ]
    if not matches:
        raise FileNotFoundError(f"No DOCX found for sequence {sequence} in {SOURCE_DIR}")
    if len(matches) > 1:
        raise RuntimeError(f"Multiple DOCX files found for sequence {sequence}: {[p.name for p in matches]}")
    return matches[0]


def ingest_single(
    doc_meta: dict,
    embedder: EmbeddingGenerator | None = None,
    dry_run: bool = False,
) -> dict:
    seq = doc_meta["sequence"]
    doc_key = doc_meta.get("document_key") or doc_meta.get("document_id")
    if not doc_key or not isinstance(doc_key, str):
        raise ValueError(f"Document at sequence {seq} is missing a valid 'document_key' or 'document_id'")

    title = doc_meta["title"]
    status = doc_meta.get("approval_status", "approved")

    docx_path = find_source_file(seq)
    loaded = load_document(docx_path)
    parsed = parse_document(loaded)
    chunks = create_chunks(doc_key, parsed)
    report = validate_ingest(doc_meta, parsed, chunks)

    if not report.is_valid:
        print(f"[{doc_key}] Validation FAILED: {report.errors}", file=sys.stderr)
        return {"document_key": doc_key, "status": "failed", "errors": report.errors}

    for warn in report.warnings:
        print(f"[{doc_key}] Warning: {warn}")

    if not dry_run:
        embedder_instance = embedder or EmbeddingGenerator()
        contents = [c.content for c in chunks]
        embeddings = embedder_instance.embed_batch(contents) if contents else []

        with ReferenceRepository.connect() as repo:
            result = repo.save_document_with_chunks(
                document_meta=doc_meta,
                loaded=loaded,
                chunks=chunks,
                embeddings=embeddings,
            )
            inserted_chunks = result.get("inserted_chunks", len(chunks))

        print(f"[{doc_key}] Ingested {inserted_chunks} chunks successfully.")
        return {"document_key": doc_key, "status": "success", "chunks": inserted_chunks}

    else:
        print(f"[{doc_key}] DRY-RUN: {len(chunks)} chunks prepared.")
        return {"document_key": doc_key, "status": "dry_run", "chunks": len(chunks)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest reference BRDs into PostgreSQL pgvector.")
    parser.add_argument("--all", action="store_true", help="Ingest all reference documents")
    parser.add_argument("--document", type=int, help="Ingest single document by sequence number (1-15)")
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate without saving to DB")
    args = parser.parse_args()

    corpus = load_corpus()
    embedder = None if args.dry_run else EmbeddingGenerator()

    if args.all:
        for doc in corpus:
            ingest_single(doc, embedder=embedder, dry_run=args.dry_run)
    elif args.document:
        doc = next((d for d in corpus if d["sequence"] == args.document), None)
        if not doc:
            print(f"Document with sequence {args.document} not found in corpus.", file=sys.stderr)
            sys.exit(1)
        ingest_single(doc, embedder=embedder, dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()



