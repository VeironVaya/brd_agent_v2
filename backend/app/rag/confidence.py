"""Backward-compatibility re-export for confidence scoring.

Active Agent 2 deterministic confidence calculation has moved to `app.ai.judge.scoring`.
Legacy 50/30/20 confidence utilities have moved to `app.ai.rag.legacy_confidence`.
This module is retained strictly for backward compatibility with legacy tests.
"""

from app.ai.judge.scoring import (
    COMPONENT_WEIGHTS,
    HIGH_CONFIDENCE_THRESHOLD,
    LABEL_TO_SCORE,
    MEDIUM_CONFIDENCE_THRESHOLD,
    calculate_component_score,
    calculate_final_confidence,
    determine_confidence_level,
)

from app.ai.rag.legacy_confidence import (
    assess_confidence,
    calculate_canonical_coverage,
    calculate_field_alignment,
    calculate_reference_similarity,
    cosine_similarity,
    generate_confidence_explanation,
)

__all__ = [
    "COMPONENT_WEIGHTS",
    "HIGH_CONFIDENCE_THRESHOLD",
    "LABEL_TO_SCORE",
    "MEDIUM_CONFIDENCE_THRESHOLD",
    "assess_confidence",
    "calculate_canonical_coverage",
    "calculate_component_score",
    "calculate_field_alignment",
    "calculate_final_confidence",
    "calculate_reference_similarity",
    "cosine_similarity",
    "determine_confidence_level",
    "generate_confidence_explanation",
]
