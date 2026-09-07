"""app/rag/confidence.py
=====================
Deterministic Confidence Calculation Engine.

Calculates confidence scores from structured Agent 2 rubric judgments:
- Evidence Grounding & Traceability (20%)
- Reference & Business Context Alignment (20%)
- Section-Specific Compliance (20%)
- Clarity, Testability & Actionability (20%)
- Consistency & Dependency Integrity (20%)

N_A criteria are strictly excluded from the denominator.
If an entire component is N_A, remaining component weights are dynamically renormalized.
"""

from __future__ import annotations

import warnings
from typing import Any, Mapping, Sequence
from pathlib import Path
import json

from .models import ConfidenceAssessment, ConfidenceComponents, ReferenceCitation
from .embeddings import EmbeddingGenerator
from .llm_client import LLMClient

# ---------------------------------------------------------------------------
# Agent 2 Deterministic Confidence Configuration & Engine (Single Source of Truth)
# Re-exported from app.ai.judge.scoring for backward-compatibility.
# ---------------------------------------------------------------------------
from app.ai.judge.scoring import (
    COMPONENT_WEIGHTS,
    HIGH_CONFIDENCE_THRESHOLD,
    HIGH_THRESHOLD,
    LABEL_TO_SCORE,
    MEDIUM_CONFIDENCE_THRESHOLD,
    MEDIUM_THRESHOLD,
    calculate_component_score,
    calculate_final_confidence,
    determine_confidence_level,
    determine_judge_confidence_level,
)


# ---------------------------------------------------------------------------
# Legacy RAG Confidence Functions (DEPRECATED from active production scoring)
# Kept strictly for backward compatibility with existing tests and RAG CLI.
# ---------------------------------------------------------------------------

BRD_FIELDS_PATH = Path(__file__).resolve().parent / "config" / "brd_fields.json"
DEFAULT_REFERENCE_SIMILARITY_WEIGHT = 0.50
DEFAULT_FIELD_ALIGNMENT_WEIGHT = 0.30
DEFAULT_CANONICAL_COVERAGE_WEIGHT = 0.20
DEFAULT_REF_TOP_WEIGHTS = (0.50, 0.30, 0.20)

_FIELD_ANCHORS_CACHE: dict[str, str] = {}
_FIELD_EMBEDDINGS_CACHE: dict[str, list[float]] = {}


def _load_field_anchors() -> dict[str, str]:
    global _FIELD_ANCHORS_CACHE
    if _FIELD_ANCHORS_CACHE:
        return _FIELD_ANCHORS_CACHE
    if not BRD_FIELDS_PATH.exists():
        return {}
    data = json.loads(BRD_FIELDS_PATH.read_text(encoding="utf-8"))
    anchors = {}
    for f in data.get("fields", []):
        fid = f.get("field_id", "")
        title = f.get("title", "")
        big_q = f.get("big_question", "")
        info_needed = f.get("information_needed", "")
        anchors[fid] = f"{title}. {big_q}. {info_needed}".strip()
    _FIELD_ANCHORS_CACHE = anchors
    return _FIELD_ANCHORS_CACHE


def cosine_similarity(vec1: Sequence[float], vec2: Sequence[float]) -> float:
    """Calculates clamped cosine similarity [0.0, 1.0] between two vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    sim = dot / (norm1 * norm2)
    return max(0.0, min(1.0, float(sim)))


def calculate_reference_similarity(
    generated_text: str,
    references: Sequence[ReferenceCitation],
    embedder: EmbeddingGenerator | None = None,
    top_weights: tuple[float, ...] = DEFAULT_REF_TOP_WEIGHTS,
) -> float:
    """[DEPRECATED] Measures semantic similarity against Top-K references."""
    if not generated_text or not generated_text.strip() or not references:
        return 0.0
    embedder_instance = embedder or EmbeddingGenerator()
    gen_vec = embedder_instance.embed_text(generated_text)
    chunk_sims: list[float] = []
    for ref in references[: len(top_weights)]:
        ref_vec = embedder_instance.embed_text(ref.content)
        sim = cosine_similarity(gen_vec, ref_vec)
        chunk_sims.append(sim)
    if not chunk_sims:
        return 0.0
    weights = top_weights[: len(chunk_sims)]
    total_w = sum(weights)
    if total_w <= 0.0:
        return sum(chunk_sims) / len(chunk_sims)
    normalized_weights = [w / total_w for w in weights]
    weighted_sim = sum(w * s for w, s in zip(normalized_weights, chunk_sims))
    return max(0.0, min(1.0, round(float(weighted_sim), 4)))


def calculate_field_alignment(
    generated_text: str,
    field_id: str,
    embedder: EmbeddingGenerator | None = None,
) -> float:
    """[DEPRECATED] Measures semantic alignment between section and canonical anchor."""
    if not generated_text or not generated_text.strip() or not field_id:
        return 0.0
    anchors = _load_field_anchors()
    anchor_text = anchors.get(field_id)
    if not anchor_text:
        return 0.0
    embedder_instance = embedder or EmbeddingGenerator()
    gen_vec = embedder_instance.embed_text(generated_text)
    if field_id not in _FIELD_EMBEDDINGS_CACHE:
        _FIELD_EMBEDDINGS_CACHE[field_id] = embedder_instance.embed_text(anchor_text)
    anchor_vec = _FIELD_EMBEDDINGS_CACHE[field_id]
    sim = cosine_similarity(gen_vec, anchor_vec)
    return max(0.0, min(1.0, round(sim, 4)))


def calculate_canonical_coverage(
    total_canonical_gaps: int,
    unresolved_gap_count: int,
) -> float:
    """[DEPRECATED] Measures coverage of canonical information gaps."""
    if total_canonical_gaps <= 0:
        return 1.0
    resolved = max(0, total_canonical_gaps - unresolved_gap_count)
    coverage = resolved / total_canonical_gaps
    return max(0.0, min(1.0, round(coverage, 4)))


EXPLANATION_SYSTEM_PROMPT = """You are a helpful Business Analyst Assistant explaining a BRD Section Confidence Assessment to non-technical business stakeholders.

STRICT BUSINESS EXPLANATION RULES:
1. Do NOT change, question, or invent confidence scores or percentages.
2. Do NOT introduce new project facts, new requirements, or new unresolved topics.
3. Do NOT use technical jargon such as 'cosine similarity', 'vector embedding', 'pgvector', 'dot product', 'dimension', or 'semantic search'.
4. Base the explanation ONLY on the provided score components, confidence level, and unresolved information points.
5. Write in concise, professional, and clear Indonesian (1-2 sentences max).
6. Explain what is already well-covered and mention what key information is still needed if any.

OUTPUT FORMAT:
Return ONLY the plain text explanation without quotes or markdown formatting.
"""


def generate_confidence_explanation(
    assessment: ConfidenceAssessment,
    unresolved_gap_descriptions: Sequence[str],
    llm_client: LLMClient | None = None,
) -> str:
    """[DEPRECATED] Generates business reason for legacy assessment."""
    pct = assessment.confidence_percentage
    lvl = assessment.confidence_level.lower()
    if lvl == "high":
        base_desc = f"Isi section sangat selaras dengan standar BRD referensi ({pct}%) dan telah mencakup kebutuhan informasi utama."
    elif lvl == "medium":
        base_desc = f"Isi section sudah cukup sesuai dengan kebutuhan dan selaras dengan pola BRD referensi ({pct}%)."
    else:
        base_desc = f"Isi section masih memerlukan penyelarasan lebih lanjut dengan standar BRD referensi ({pct}%)."

    if unresolved_gap_descriptions:
        gaps_summary = ", ".join(unresolved_gap_descriptions[:3])
        fallback_reason = f"{base_desc} Namun, beberapa informasi penting seperti {gaps_summary} masih perlu dilengkapi."
    else:
        fallback_reason = base_desc

    if llm_client is None or not hasattr(llm_client, "generate"):
        return fallback_reason

    user_payload = [
        f"Confidence Score: {pct}%",
        f"Confidence Level: {lvl.capitalize()}",
        f"Reference Similarity: {int(assessment.components.reference_similarity * 100)}%",
        f"Field Alignment: {int(assessment.components.field_alignment * 100)}%",
        f"Canonical Coverage: {int(assessment.components.canonical_coverage * 100)}%",
    ]
    if unresolved_gap_descriptions:
        user_payload.append(f"Unresolved Information Needs: {', '.join(unresolved_gap_descriptions)}")
    else:
        user_payload.append("Unresolved Information Needs: None (All required information resolved)")

    prompt_text = "\n".join(user_payload)
    try:
        raw_reason = llm_client.generate(prompt=prompt_text, system_instruction=EXPLANATION_SYSTEM_PROMPT)
        cleaned = raw_reason.strip().strip('"').strip("'")
        forbidden = ["cosine", "vector", "embedding", "pgvector", "token", "dot product"]
        if any(f in cleaned.lower() for f in forbidden) or not cleaned:
            return fallback_reason
        return cleaned
    except Exception:
        return fallback_reason


def assess_confidence(
    field_id: str,
    generated_content: str,
    retrieved_references: Sequence[ReferenceCitation],
    total_canonical_gaps: int,
    unresolved_gap_descriptions: Sequence[str],
    embedder: EmbeddingGenerator | None = None,
    llm_client: LLMClient | None = None,
    weights: tuple[float, float, float] = (
        DEFAULT_REFERENCE_SIMILARITY_WEIGHT,
        DEFAULT_FIELD_ALIGNMENT_WEIGHT,
        DEFAULT_CANONICAL_COVERAGE_WEIGHT,
    ),
) -> ConfidenceAssessment:
    """[DEPRECATED] Legacy 50/30/20 formula.

    This function is DEPRECATED and should no longer be used for production
    confidence scoring. Use Agent 2 (`app.services.judge`) and
    `calculate_final_confidence` instead.
    """
    ref_sim = calculate_reference_similarity(
        generated_text=generated_content,
        references=retrieved_references,
        embedder=embedder,
    )
    field_align = calculate_field_alignment(
        generated_text=generated_content,
        field_id=field_id,
        embedder=embedder,
    )
    unresolved_count = len(unresolved_gap_descriptions)
    coverage = calculate_canonical_coverage(
        total_canonical_gaps=total_canonical_gaps,
        unresolved_gap_count=unresolved_count,
    )
    w_ref, w_align, w_cov = weights
    total_w = w_ref + w_align + w_cov
    raw_score = (w_ref * ref_sim + w_align * field_align + w_cov * coverage) / total_w if total_w > 0 else 0.0
    score = max(0.0, min(1.0, round(raw_score, 4)))
    percentage = round(score * 100)
    level = determine_confidence_level(score).lower()

    components = ConfidenceComponents(
        reference_similarity=ref_sim,
        field_alignment=field_align,
        canonical_coverage=coverage,
    )
    assessment_temp = ConfidenceAssessment(
        confidence_score=score,
        confidence_percentage=percentage,
        confidence_level=level,
        components=components,
        reason="",
    )
    reason = generate_confidence_explanation(
        assessment=assessment_temp,
        unresolved_gap_descriptions=unresolved_gap_descriptions,
        llm_client=llm_client,
    )
    return ConfidenceAssessment(
        confidence_score=score,
        confidence_percentage=percentage,
        confidence_level=level,
        components=components,
        reason=reason,
    )
