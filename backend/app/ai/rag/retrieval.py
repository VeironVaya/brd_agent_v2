"""
app/ai/rag/retrieval.py
=======================
Production Semantic pgvector Retrieval Engine.
Executes cosine similarity vector searches against PostgreSQL reference chunks.
Exposes the single official contract: search_references(query, field_id=None, top_k=3).
"""

from __future__ import annotations

import os
from typing import Any
import psycopg

from .embeddings import EmbeddingGenerator, get_default_embedder
from .models import SearchResult


class PostgresSemanticStore:
    """Executes cosine similarity vector searches using PostgreSQL pgvector."""

    _REQUIRED_VARS = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")

    def __init__(self, conn: psycopg.Connection, embedder: EmbeddingGenerator | None = None) -> None:
        self._conn = conn
        self._embedder = embedder or get_default_embedder()

    def close(self) -> None:
        """Safely close underlying PostgreSQL connection."""
        if hasattr(self, "_conn") and self._conn and not self._conn.closed:
            self._conn.close()

    def __enter__(self) -> PostgresSemanticStore:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    @classmethod
    def from_env(cls) -> PostgresSemanticStore:
        rag_url = None
        try:
            from app.config import settings
            db_url = getattr(settings, "database_url", None)
            rag_url = getattr(settings, "rag_database_url", None)
            if db_url:
                rag_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        except Exception:
            pass

        if not rag_url:
            rag_url = os.environ.get("RAG_DATABASE_URL") or os.environ.get("DATABASE_URL")

        if rag_url:
            cleaned_url = rag_url.replace("postgresql+asyncpg://", "postgresql://")
            conn = psycopg.connect(cleaned_url, autocommit=True)
            return cls(conn)


        required_non_empty = [k for k in cls._REQUIRED_VARS if k != "DB_PASSWORD"]
        missing = [k for k in required_non_empty if not os.environ.get(k)]

        if missing:
            raise EnvironmentError(f"Missing required environment variable(s): {', '.join(missing)}")

        password = os.environ.get("DB_PASSWORD") or None

        conn = psycopg.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=password,
            autocommit=True,
        )
        return cls(conn)

    def search_semantic(
        self,
        query: str,
        field_id: str | None = None,
        top_k: int = 3,
        min_similarity: float = 0.0,
    ) -> list[SearchResult]:
        if not query or not query.strip() or top_k <= 0:
            return []

        query_vec = self._embedder.embed_text(query)
        vec_str = "[" + ",".join(str(x) for x in query_vec) + "]"

        sql = """
            SELECT
                rd.document_key,
                rd.title AS document_title,
                rc.field_id,
                rc.field_title,
                rc.chunk_index,
                rc.content,
                1.0 - (rc.embedding <=> %s::vector) AS similarity_score
            FROM reference_chunks rc
            JOIN reference_documents rd ON rc.document_id = rd.id
            WHERE rc.embedding IS NOT NULL
        """
        params: list[object] = [vec_str]

        if field_id is not None:
            sql += " AND rc.field_id = %s"
            params.append(field_id)

        sql += " ORDER BY rc.embedding <=> %s::vector ASC LIMIT %s"
        params.extend([vec_str, top_k])

        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

        results: list[SearchResult] = []
        for r in rows:
            sim_score = round(float(r[6]), 4)
            if sim_score >= min_similarity:
                results.append(
                    SearchResult(
                        document_key=r[0],
                        document_title=r[1],
                        field_id=r[2],
                        field_title=r[3],
                        chunk_index=r[4],
                        content=r[5],
                        similarity_score=sim_score,
                    )
                )

        return results

    def search_references(
        self,
        query: str,
        field_id: str | None = None,
        top_k: int = 3,
    ) -> list[SearchResult]:
        return self.search_semantic(query=query, field_id=field_id, top_k=top_k)


def search_references(
    query: str,
    field_id: str | None = None,
    top_k: int = 3,
    store: PostgresSemanticStore | None = None,
) -> list[SearchResult]:
    """
    Official single production retrieval contract function.
    FastEmbed query embedding -> pgvector cosine similarity -> Top-K SearchResult.
    Ensures connection is safely closed when instantiating from environment.
    """
    if store is not None:
        return store.search_references(query=query, field_id=field_id, top_k=top_k)

    with PostgresSemanticStore.from_env() as local_store:
        return local_store.search_references(query=query, field_id=field_id, top_k=top_k)
