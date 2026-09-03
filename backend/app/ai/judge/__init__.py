"""Agent 2 — Senior Business Analyst Reviewer / Judge Subsystem."""

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
from app.ai.judge.scoring import (
    HIGH_CONFIDENCE_THRESHOLD,
    MEDIUM_CONFIDENCE_THRESHOLD,
    _calculate_component_scores,
    calculate_component_score,
    calculate_final_confidence,
    determine_confidence_level,
)
from app.services.brd_rules import (
    FIELD_SPECIFIC_RUBRICS,
    GLOBAL_CLARITY_CRITERIA,
    GLOBAL_CONSISTENCY_CRITERIA,
    GLOBAL_GROUNDING_CRITERIA,
    GLOBAL_REFERENCE_CRITERIA,
    get_field_rubric,
)
from app.ai.judge.prompt import (
    JUDGE_STAGE_A_PROMPT,
    JUDGE_STAGE_B_PROMPT,
    build_stage_a_context,
    build_stage_b_context,
)
from app.ai.judge.service import (
    _build_criteria_str,
    _build_stage_a_summary,
    _calculate_final_confidence,
    _classify_user_input,
    _component_score,
    build_project_evidence_text,
    evaluate_section,
)

__all__ = [
    "COMPONENT_WEIGHTS",
    "CriticalFlag",
    "CriticalFlagType",
    "CriterionJudgment",
    "FIELD_SPECIFIC_RUBRICS",
    "GLOBAL_CLARITY_CRITERIA",
    "GLOBAL_CONSISTENCY_CRITERIA",
    "GLOBAL_GROUNDING_CRITERIA",
    "GLOBAL_REFERENCE_CRITERIA",
    "HIGH_CONFIDENCE_THRESHOLD",
    "HIGH_THRESHOLD",
    "JUDGE_STAGE_A_PROMPT",
    "JUDGE_STAGE_B_PROMPT",
    "JudgeStageAOutput",
    "JudgeStageBOutput",
    "JudgmentLabel",
    "LABEL_TO_SCORE",
    "MEDIUM_CONFIDENCE_THRESHOLD",
    "MEDIUM_THRESHOLD",
    "_build_criteria_str",
    "_build_stage_a_summary",
    "_calculate_component_scores",
    "_calculate_final_confidence",
    "_classify_user_input",
    "_component_score",
    "build_project_evidence_text",
    "build_stage_a_context",
    "build_stage_b_context",
    "calculate_component_score",
    "calculate_final_confidence",
    "determine_confidence_level",
    "determine_judge_confidence_level",
    "evaluate_section",
    "get_field_rubric",
]

