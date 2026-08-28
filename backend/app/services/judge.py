"""Backward-compatibility re-export for app.ai.judge.

Agent 2 (Senior BA Reviewer / Judge) now lives in `app.ai.judge`.
This module is retained for backward compatibility with existing tests,
calibration fixtures, and callers.
"""

from app.ai.judge import (
    _build_criteria_str,
    _build_stage_a_summary,
    _calculate_component_scores,
    _calculate_final_confidence,
    _classify_user_input,
    _component_score,
    build_project_evidence_text,
    calculate_component_score,
    calculate_final_confidence,
    determine_confidence_level,
    determine_judge_confidence_level,
    evaluate_section,
)
from app.ai.judge.service import _call_llm_json, search_references

__all__ = [
    "_build_criteria_str",
    "_build_stage_a_summary",
    "_calculate_component_scores",
    "_calculate_final_confidence",
    "_call_llm_json",
    "_classify_user_input",
    "_component_score",
    "build_project_evidence_text",
    "calculate_component_score",
    "calculate_final_confidence",
    "determine_confidence_level",
    "determine_judge_confidence_level",
    "evaluate_section",
    "search_references",
]
