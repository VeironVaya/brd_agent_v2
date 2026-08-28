"""Backward-compatibility re-export for app.ai.judge.schema.

Agent 2 schemas and scoring now live in `app.ai.judge`.
This module is retained for backward compatibility.
"""

from app.ai.judge.schema import (
    COMPONENT_WEIGHTS,
    CriticalFlag,
    CriticalFlagType,
    CriterionJudgment,
    HIGH_THRESHOLD,
    JudgeStageAOutput,
    JudgeStageBOutput,
    JudgmentLabel,
    LABEL_TO_SCORE,
    MEDIUM_THRESHOLD,
    determine_judge_confidence_level,
)

__all__ = [
    "COMPONENT_WEIGHTS",
    "CriticalFlag",
    "CriticalFlagType",
    "CriterionJudgment",
    "HIGH_THRESHOLD",
    "JudgeStageAOutput",
    "JudgeStageBOutput",
    "JudgmentLabel",
    "LABEL_TO_SCORE",
    "MEDIUM_THRESHOLD",
    "determine_judge_confidence_level",
]
