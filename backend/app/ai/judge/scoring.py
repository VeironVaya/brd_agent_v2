"""Agent 2 — Deterministic Confidence & Component Scoring Engine.

Active deterministic scoring logic for Senior BA Reviewer / Judge:
- MET → 100, MOSTLY_MET → 75, PARTIALLY_MET → 50, NOT_MET → 0
- N_A strictly excluded from denominator
- Component averaging
- Dynamic weight renormalization when components are N_A
- Final confidence calculation (0-100)
- HIGH (>= 85), MEDIUM (60-84), LOW (< 60) classification
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

# ---------------------------------------------------------------------------
# Component weights (20% each, sum = 1.0)
# ---------------------------------------------------------------------------
COMPONENT_WEIGHTS: dict[str, float] = {
    "grounding": 0.20,
    "reference_context": 0.20,
    "section_compliance": 0.20,
    "testability": 0.20,
    "consistency": 0.20,
}

# ---------------------------------------------------------------------------
# Numeric mapping for rubric judgment labels
# N_A is intentionally excluded — callers must filter it before averaging
# ---------------------------------------------------------------------------
LABEL_TO_SCORE: dict[str, int] = {
    "MET": 100,
    "MOSTLY_MET": 75,
    "PARTIALLY_MET": 50,
    "NOT_MET": 0,
}

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
HIGH_THRESHOLD: int = 85
MEDIUM_THRESHOLD: int = 60
HIGH_CONFIDENCE_THRESHOLD: int = 85
MEDIUM_CONFIDENCE_THRESHOLD: int = 60


def calculate_component_score(judgments: Sequence[Any]) -> int | None:
    """Calculates the average score for a single component from its criterion judgments.

    Rules:
    - MET = 100, MOSTLY_MET = 75, PARTIALLY_MET = 50, NOT_MET = 0.
    - N_A criteria are strictly excluded from the denominator.
    - If ALL criteria are N_A (or list is empty), returns None (component is unavailable).
    """
    if not judgments:
        return None

    scored_values: list[int] = []
    for j in judgments:
        label = getattr(j, "label", j)
        # Convert enum or str to string value
        label_str = label.value if hasattr(label, "value") else str(label)
        if label_str != "N_A" and label_str in LABEL_TO_SCORE:
            scored_values.append(LABEL_TO_SCORE[label_str])

    if not scored_values:
        return None

    return round(sum(scored_values) / len(scored_values))


def calculate_final_confidence(component_scores: Mapping[str, int | None]) -> int:
    """Calculates the overall confidence score (0-100) from component scores.

    Rules:
    - Weighted average using COMPONENT_WEIGHTS (20% each).
    - If any component is None (all N_A), dynamically renormalizes weights
      of available components so they sum to 1.0.
    - If all components are None, returns 0.
    """
    available = {
        k: score for k, score in component_scores.items() if score is not None
    }
    if not available:
        return 0

    total_weight = sum(COMPONENT_WEIGHTS.get(k, 0.20) for k in available)
    if total_weight <= 0:
        return 0

    weighted_sum = sum(
        COMPONENT_WEIGHTS.get(k, 0.20) * score for k, score in available.items()
    )
    return round(weighted_sum / total_weight)


def determine_confidence_level(score: int | float) -> str:
    """Classifies confidence score into level name.

    If score is float in [0.0, 1.0], returns lowercase ('high', 'medium', 'low')
    with legacy thresholds (0.80, 0.65) for backward-compatibility.
    If score is integer (0-100), returns uppercase ('HIGH', 'MEDIUM', 'LOW')
    with Agent 2 production thresholds (85, 60).
    """
    if isinstance(score, float) and score <= 1.0:
        if score >= 0.80:
            return "high"
        elif score >= 0.65:
            return "medium"
        return "low"

    if score >= HIGH_CONFIDENCE_THRESHOLD:
        return "HIGH"
    elif score >= MEDIUM_CONFIDENCE_THRESHOLD:
        return "MEDIUM"
    return "LOW"


def determine_judge_confidence_level(score: int) -> str:
    """Map integer score 0-100 to HIGH / MEDIUM / LOW."""
    if score >= HIGH_THRESHOLD:
        return "HIGH"
    if score >= MEDIUM_THRESHOLD:
        return "MEDIUM"
    return "LOW"


def _calculate_component_scores(stage_a: Any) -> dict[str, int | None]:
    """Map Stage A judgment lists to integer component scores (0-100 or None)."""
    return {
        "grounding": calculate_component_score(stage_a.grounding_judgments),
        "reference_context": calculate_component_score(stage_a.reference_judgments),
        "section_compliance": calculate_component_score(stage_a.section_compliance_judgments),
        "testability": calculate_component_score(stage_a.clarity_judgments),
        "consistency": calculate_component_score(stage_a.consistency_judgments),
    }

