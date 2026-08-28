"""Pydantic models for Agent 2 (Senior BA Reviewer/Judge) structured I/O.

Agent 2 operates in two stages:
  Stage A — VERIFIER + GRADER: returns structured judgment labels
  Stage B — CRITIC: returns prose critique using Stage A + calculated scores

The final output of both stages is merged into the `confidence_breakdown`
JSONB column on the Answer model, which the frontend reads directly.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.ai.judge.scoring import (
    COMPONENT_WEIGHTS,
    HIGH_THRESHOLD,
    LABEL_TO_SCORE,
    MEDIUM_THRESHOLD,
    determine_judge_confidence_level,
)


# ---------------------------------------------------------------------------
# Judgment labels
# ---------------------------------------------------------------------------

class JudgmentLabel(str, Enum):
    MET = "MET"
    MOSTLY_MET = "MOSTLY_MET"
    PARTIALLY_MET = "PARTIALLY_MET"
    NOT_MET = "NOT_MET"
    N_A = "N_A"


# ---------------------------------------------------------------------------
# V1 Critical flag types
# ---------------------------------------------------------------------------

class CriticalFlagType(str, Enum):
    UNSUPPORTED_NUMERIC_FACT = "UNSUPPORTED_NUMERIC_FACT"
    CONTRADICTORY_CONFIRMED_FACT = "CONTRADICTORY_CONFIRMED_FACT"
    INVENTED_BUSINESS_RULE = "INVENTED_BUSINESS_RULE"
    INVENTED_ROLE_OR_OWNER = "INVENTED_ROLE_OR_OWNER"
    INVENTED_VENDOR_OR_SYSTEM = "INVENTED_VENDOR_OR_SYSTEM"
    INVENTED_POLICY_OR_REGULATION = "INVENTED_POLICY_OR_REGULATION"
    MATERIAL_SCOPE_LEAK = "MATERIAL_SCOPE_LEAK"
    HARD_DEPENDENCY_CONFLICT = "HARD_DEPENDENCY_CONFLICT"


# ---------------------------------------------------------------------------
# Per-criterion judgment
# ---------------------------------------------------------------------------

class CriterionJudgment(BaseModel):
    criterion: str = Field(..., description="Short rubric item label")
    label: JudgmentLabel = Field(..., description="Judgment label")
    rationale: str = Field(
        ..., description="One-sentence explanation of why this label was chosen"
    )

    @field_validator("label", mode="before")
    @classmethod
    def normalize_label(cls, v: Any) -> Any:
        if isinstance(v, str):
            v_clean = v.strip().upper().replace("/", "_").replace("-", "_").replace(" ", "_")
            if v_clean in ("N_A", "NA", "NOT_APPLICABLE", "NOT_YET_VERIFIABLE", "UNVERIFIABLE"):
                return JudgmentLabel.N_A
            if v_clean == "MOSTLY_MET":
                return JudgmentLabel.MOSTLY_MET
            if v_clean == "PARTIALLY_MET":
                return JudgmentLabel.PARTIALLY_MET
            if v_clean == "NOT_MET":
                return JudgmentLabel.NOT_MET
            if v_clean == "MET":
                return JudgmentLabel.MET
        return v


# ---------------------------------------------------------------------------
# Critical flag
# ---------------------------------------------------------------------------

class CriticalFlag(BaseModel):
    type: str = Field(..., description="One of the V1 critical flag types")
    reason: str = Field(..., description="Explanation of the critical issue")
    excerpt: str = Field(
        default="", description="Short offending text fragment from the generated content"
    )


# ---------------------------------------------------------------------------
# Stage A output — VERIFIER + GRADER
# ---------------------------------------------------------------------------

class JudgeStageAOutput(BaseModel):
    """Structured output from Agent 2 Stage A (LLM call #1).

    Each *_judgments list contains one CriterionJudgment per rubric item
    for that component. The backend maps labels → scores and calculates
    component percentages + final confidence.
    """

    # Component 1 — Evidence Grounding & Traceability
    grounding_judgments: list[CriterionJudgment] = Field(
        default_factory=list,
        description="Judgments for the Evidence Grounding & Traceability component",
    )

    # Component 2 — Reference & Business Context Alignment
    reference_judgments: list[CriterionJudgment] = Field(
        default_factory=list,
        description="Judgments for the Reference & Business Context Alignment component",
    )

    # Component 3 — Section-Specific Compliance (field-specific rubric)
    section_compliance_judgments: list[CriterionJudgment] = Field(
        default_factory=list,
        description="Judgments for the Section-Specific Compliance component (field rubric)",
    )

    # Component 4 — Clarity, Testability & Actionability
    clarity_judgments: list[CriterionJudgment] = Field(
        default_factory=list,
        description="Judgments for the Clarity, Testability & Actionability component",
    )

    # Component 5 — Consistency & Dependency Integrity
    consistency_judgments: list[CriterionJudgment] = Field(
        default_factory=list,
        description="Judgments for the Consistency & Dependency Integrity component",
    )

    # Dependency check result
    dependency_status: Literal["CONSISTENT", "CONFLICT", "NOT_YET_VERIFIABLE"] = Field(
        default="NOT_YET_VERIFIABLE",
        description="Overall dependency integrity status",
    )

    # Critical flags (may be empty)
    critical_flags: list[CriticalFlag] = Field(
        default_factory=list,
        description="V1 critical issues detected in the generated content",
    )


# ---------------------------------------------------------------------------
# Stage B output — CRITIC
# ---------------------------------------------------------------------------

class JudgeStageBOutput(BaseModel):
    """Structured output from Agent 2 Stage B (LLM call #2).

    Stage B receives Stage A judgments + backend-calculated scores and
    produces human-readable critique. It MUST NOT introduce new project
    facts. Suggestions are recommendations/questions, not approved
    requirements.
    """

    strengths: list[str] = Field(
        default_factory=list, description="Key strengths of the generated section"
    )
    issues: list[str] = Field(
        default_factory=list, description="Identified issues in the generated section"
    )
    suggestions: list[str] = Field(
        default_factory=list,
        description="Recommended improvements or clarifying questions",
    )
    summary_reason: str = Field(
        default="",
        description="One-paragraph summary explaining the overall confidence level",
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

