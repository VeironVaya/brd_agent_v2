"""Backward-compatibility re-export for app.ai.judge.rubrics.

Agent 2 rubrics now live in `app.ai.judge.rubrics`.
This module is retained for backward compatibility.
"""

from app.ai.judge.rubrics import (
    FIELD_SPECIFIC_RUBRICS,
    GLOBAL_CLARITY_CRITERIA,
    GLOBAL_CONSISTENCY_CRITERIA,
    GLOBAL_GROUNDING_CRITERIA,
    GLOBAL_REFERENCE_CRITERIA,
    get_field_rubric,
)

__all__ = [
    "FIELD_SPECIFIC_RUBRICS",
    "GLOBAL_CLARITY_CRITERIA",
    "GLOBAL_CONSISTENCY_CRITERIA",
    "GLOBAL_GROUNDING_CRITERIA",
    "GLOBAL_REFERENCE_CRITERIA",
    "get_field_rubric",
]
