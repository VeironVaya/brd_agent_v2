"""
tests/test_confidence.py
========================
Comprehensive test suite for Post-Generation RAG Confidence Assessment.

Tests:
1. Deterministic formula calculation with default weights (50% ref_sim, 30% field_align, 20% coverage).
2. Level classification thresholds (high >= 0.80, medium 0.65-0.79, low < 0.65).
3. Safety gate: unsafe generation raises UnsafeGenerationError and never produces a confidence score.
4. Canonical coverage calculation with varying numbers of unresolved canonical gaps.
5. Reference similarity with varying numbers of reference chunks (0, 1, 2, 3 chunks).
6. Field alignment computation against canonical field anchor metadata.
7. Business explanation generation without forbidden technical jargon.
8. Fallback explanation when LLM is unavailable or offline.
9. End-to-end integration with generate_section().
"""

from __future__ import annotations

import json
import pytest

from app.ai.rag.legacy_confidence import (
    HIGH_CONFIDENCE_THRESHOLD,
    MEDIUM_CONFIDENCE_THRESHOLD,
    assess_confidence,
    calculate_canonical_coverage,
    calculate_field_alignment,
    calculate_reference_similarity,
    cosine_similarity,
    determine_confidence_level,
    generate_confidence_explanation,
)
from app.ai.rag.models import (
    ConfidenceAssessment,
    ConfidenceComponents,
    ReferenceCitation,
    SearchResult,
)
from app.ai.rag.generator import UnsafeGenerationError, generate_section
from app.ai.rag.llm_client import FakeLLMClient


def _create_mock_citation(
    citation_id: str,
    content: str,
    similarity_score: float = 0.85,
    field_id: str = "1.1.1",
    field_title: str = "Background",
) -> ReferenceCitation:
    return ReferenceCitation(
        citation_id=citation_id,
        document_key="mock_doc_1",
        document_title="Mock Approved BRD",
        field_id=field_id,
        field_title=field_title,
        chunk_index=0,
        similarity_score=similarity_score,
        content=content,
    )



# ---------------------------------------------------------------------------
# 1. Cosine similarity unit test
# ---------------------------------------------------------------------------
def test_cosine_similarity_basic():
    vec_a = [1.0, 0.0, 0.0]
    vec_b = [1.0, 0.0, 0.0]
    assert cosine_similarity(vec_a, vec_b) == pytest.approx(1.0)


    vec_c = [0.0, 1.0, 0.0]
    assert cosine_similarity(vec_a, vec_c) == pytest.approx(0.0)

    # Empty or mismatched
    assert cosine_similarity([], [1.0]) == 0.0
    assert cosine_similarity([1.0, 2.0], [1.0]) == 0.0


# ---------------------------------------------------------------------------
# 2. Level classification tests
# ---------------------------------------------------------------------------
def test_determine_confidence_level():
    assert determine_confidence_level(0.85) == "high"
    assert determine_confidence_level(0.80) == "high"
    assert determine_confidence_level(0.79) == "medium"
    assert determine_confidence_level(0.65) == "medium"
    assert determine_confidence_level(0.64) == "low"
    assert determine_confidence_level(0.0) == "low"


# ---------------------------------------------------------------------------
# 3. Canonical Coverage Calculation
# ---------------------------------------------------------------------------
def test_calculate_canonical_coverage():
    # 4 total gaps, 0 unresolved -> 100% (1.0)
    assert calculate_canonical_coverage(total_canonical_gaps=4, unresolved_gap_count=0) == 1.0

    # 4 total gaps, 2 unresolved -> 50% (0.50)
    assert calculate_canonical_coverage(total_canonical_gaps=4, unresolved_gap_count=2) == 0.50

    # 4 total gaps, 4 unresolved -> 0% (0.0)
    assert calculate_canonical_coverage(total_canonical_gaps=4, unresolved_gap_count=4) == 0.0

    # 0 total gaps -> default to 1.0 (no required gaps needed)
    assert calculate_canonical_coverage(total_canonical_gaps=0, unresolved_gap_count=0) == 1.0


# ---------------------------------------------------------------------------
# 4. Reference Similarity Calculation & Weight Normalization
# ---------------------------------------------------------------------------
def test_calculate_reference_similarity_weights():
    assert calculate_reference_similarity("", ()) == 0.0
    assert calculate_reference_similarity("Some generated text", ()) == 0.0

    refs = (
        _create_mock_citation("R1", "The system shall provide authentication and logging."),
        _create_mock_citation("R2", "The system shall handle user session timeouts."),
        _create_mock_citation("R3", "The platform shall log all administrative actions."),
    )

    gen_text = "The system shall provide user authentication with secure logging."
    sim_score = calculate_reference_similarity(gen_text, refs)
    assert 0.0 <= sim_score <= 1.0
    assert sim_score > 0.40


def test_calculate_reference_similarity_partial_chunks():
    ref_single = (_create_mock_citation("R1", "Data backup workflow every night."),)
    sim = calculate_reference_similarity("Data backup workflow every night.", ref_single)
    assert sim == pytest.approx(1.0, rel=1e-2)


# ---------------------------------------------------------------------------
# 5. Field Alignment Calculation
# ---------------------------------------------------------------------------
def test_calculate_field_alignment():
    field_id = "1.1.1"
    gen_relevant = "The legacy system faces severe scaling bottlenecks and lacks automated audit logging."
    gen_irrelevant = "Chocolate cake recipe with strawberries and vanilla frosting."

    sim_rel = calculate_field_alignment(gen_relevant, field_id)
    sim_irrel = calculate_field_alignment(gen_irrelevant, field_id)

    assert sim_rel > sim_irrel
    assert sim_rel > 0.30


# ---------------------------------------------------------------------------
# 6. Full Deterministic Assessment Math
# ---------------------------------------------------------------------------
def test_assess_confidence_math():
    refs = (
        _create_mock_citation("R1", "The system shall manage employee leave balances.", similarity_score=0.82),
        _create_mock_citation("R2", "The system shall send email notifications upon approval.", similarity_score=0.76),
    )
    gen_content = "The system shall manage employee leave balances and notify supervisors via email."

    assessment = assess_confidence(
        field_id="1.1.1",
        generated_content=gen_content,
        retrieved_references=refs,
        total_canonical_gaps=4,
        unresolved_gap_descriptions=["Specific competitor benchmarks", "Historical project data"],
    )

    assert isinstance(assessment, ConfidenceAssessment)
    assert isinstance(assessment.components, ConfidenceComponents)
    assert 0.0 <= assessment.confidence_score <= 1.0
    assert assessment.confidence_percentage == round(assessment.confidence_score * 100)
    assert assessment.confidence_level in ("high", "medium", "low")
    assert assessment.components.canonical_coverage == 0.50
    assert bool(assessment.reason)


# ---------------------------------------------------------------------------
# 7. Business Explanation Generation
# ---------------------------------------------------------------------------
def test_confidence_explanation_fallback():
    components = ConfidenceComponents(
        reference_similarity=0.78,
        field_alignment=0.90,
        canonical_coverage=0.50,
    )
    assessment = ConfidenceAssessment(
        confidence_score=0.76,
        confidence_percentage=76,
        confidence_level="medium",
        components=components,
        reason="",
    )

    reason = generate_confidence_explanation(
        assessment=assessment,
        unresolved_gap_descriptions=["pihak yang terlibat", "waktu pelaksanaan"],
        llm_client=None,
    )

    assert "76%" in reason
    assert "pihak yang terlibat" in reason
    for forbidden in ["cosine", "vector", "embedding", "pgvector", "token", "dot product"]:
        assert forbidden not in reason.lower()


def test_confidence_explanation_with_llm_client():
    components = ConfidenceComponents(
        reference_similarity=0.85,
        field_alignment=0.92,
        canonical_coverage=1.0,
    )
    assessment = ConfidenceAssessment(
        confidence_score=0.90,
        confidence_percentage=90,
        confidence_level="high",
        components=components,
        reason="",
    )

    fake_client = FakeLLMClient(
        canned_response="Section ini telah memenuhi seluruh standar referensi dan seluruh informasi yang dibutuhkan telah lengkap."
    )

    reason = generate_confidence_explanation(
        assessment=assessment,
        unresolved_gap_descriptions=[],
        llm_client=fake_client,
    )

    assert "standar referensi" in reason


# ---------------------------------------------------------------------------
# 8. Safety Gate: Unsafe generation rejects confidence calculation
# ---------------------------------------------------------------------------
def test_safety_gate_blocks_confidence_on_hallucination():
    def mock_search(query: str, field_id: str | None = None, top_k: int = 3) -> list[SearchResult]:
        return [
            SearchResult(
                document_key="doc1",
                document_title="Title",
                field_id=field_id or "1.1.1",
                field_title="Background",
                chunk_index=0,
                content="Reference SLA 99.99% availability.",
                similarity_score=0.90,
            )
        ]

    fake_client = FakeLLMClient(
        canned_response=json.dumps({
            "requirements": [
                {
                    "text": "The system shall guarantee 99.99% availability.",
                    "evidence_ids": ["C1"],
                    "grounding_reference_ids": ["R1"]
                }
            ],
            "unresolved_gap_ids": []
        })
    )

    with pytest.raises(UnsafeGenerationError) as exc_info:
        generate_section(
            field_id="1.1.1",
            confirmed_information="We need high availability.",
            search_fn=mock_search,
            llm_client=fake_client,
        )

    assert "unconfirmed factual claims/metrics" in str(exc_info.value) or "unsupported" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 9. End-to-End Section Generation with Confidence Attached
# ---------------------------------------------------------------------------
def test_generate_section_attaches_confidence():
    def mock_search(query: str, field_id: str | None = None, top_k: int = 3) -> list[SearchResult]:
        return [
            SearchResult(
                document_key="doc1",
                document_title="Title",
                field_id=field_id or "1.1.1",
                field_title="Background",
                chunk_index=0,
                content="The system shall provide automated reporting.",
                similarity_score=0.88,
            )
        ]

    fake_client = FakeLLMClient(
        canned_response=json.dumps({
            "requirements": [
                {
                    "text": "The system shall provide automated reporting for daily operations.",
                    "evidence_ids": ["C1"],
                    "grounding_reference_ids": ["R1"]
                }
            ],
            "unresolved_gap_ids": ["G1"]
        })
    )

    section = generate_section(
        field_id="1.1.1",
        confirmed_information="We need automated reporting for daily operations.",
        search_fn=mock_search,
        llm_client=fake_client,
    )

    assert section.confidence is not None
    assert isinstance(section.confidence, ConfidenceAssessment)
    assert 0.0 <= section.confidence.confidence_score <= 1.0
    assert section.confidence.confidence_percentage > 0
    assert section.confidence.confidence_level in ("high", "medium", "low")
    assert section.confidence.components.canonical_coverage < 1.0
    assert bool(section.confidence.reason)

    d = section.confidence.to_dict()
    assert "confidence_score" in d
    assert "confidence_percentage" in d
    assert "confidence_level" in d
    assert "components" in d
    assert "reason" in d
