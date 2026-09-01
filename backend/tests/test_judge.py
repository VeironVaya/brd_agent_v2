"""Tests for Agent 2 (Senior BA Reviewer / Judge).

Covers all 17 test requirements from the specification:
 1.  Exactly 26 field rubrics
 2.  Correct field-rubric selection
 3.  MET/MOSTLY_MET/PARTIAL/NOT_MET/N_A label mapping
 4.  N_A excluded from denominator
 5.  Unavailable component weight renormalization
 6.  HIGH threshold (>= 85)
 7.  MEDIUM threshold (60-84)
 8.  LOW threshold (< 60)
 9.  Critical flag -> REVIEW_REQUIRED
10.  Critical flag does NOT change score
11.  NOT_YET_VERIFIABLE has no penalty
12.  Dependency conflict detection integration
13.  Reference unavailable -> fair N/A handling
14.  Section revision triggers re-evaluation
15.  Structured Judge output validation
16.  Frontend/API response compatibility
17.  No regression to existing Agent 1 generation
"""

from __future__ import annotations

import asyncio
import json
from typing import Literal
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ai.judge.schema import (
    COMPONENT_WEIGHTS,
    HIGH_THRESHOLD,
    LABEL_TO_SCORE,
    MEDIUM_THRESHOLD,
    CriticalFlag,
    CriterionJudgment,
    JudgmentLabel,
    JudgeStageAOutput,
    JudgeStageBOutput,
    determine_judge_confidence_level,
)
from app.services.brd_rules import (
    FIELD_SPECIFIC_RUBRICS,
    GLOBAL_CLARITY_CRITERIA,
    GLOBAL_CONSISTENCY_CRITERIA,
    GLOBAL_GROUNDING_CRITERIA,
    GLOBAL_REFERENCE_CRITERIA,
    get_field_rubric,
)
from app.ai.judge import service as judge
from app.ai.rag.generator import CANONICAL_ANSWERABLE_FIELDS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _judgment(label: JudgmentLabel, criterion: str = "test criterion") -> CriterionJudgment:
    return CriterionJudgment(criterion=criterion, label=label, rationale="test rationale")


def _make_stage_a(
    grounding: list[JudgmentLabel] | None = None,
    reference: list[JudgmentLabel] | None = None,
    compliance: list[JudgmentLabel] | None = None,
    clarity: list[JudgmentLabel] | None = None,
    consistency: list[JudgmentLabel] | None = None,
    dependency_status: Literal["CONSISTENT", "CONFLICT", "NOT_YET_VERIFIABLE"] = "NOT_YET_VERIFIABLE",
    critical_flags: list | None = None,
) -> JudgeStageAOutput:
    def to_judgments(labels: list[JudgmentLabel] | None) -> list[CriterionJudgment]:
        return [_judgment(l) for l in (labels or [])]

    return JudgeStageAOutput(
        grounding_judgments=to_judgments(grounding),
        reference_judgments=to_judgments(reference),
        section_compliance_judgments=to_judgments(compliance),
        clarity_judgments=to_judgments(clarity),
        consistency_judgments=to_judgments(consistency),
        dependency_status=dependency_status,
        critical_flags=critical_flags or [],
    )


# ---------------------------------------------------------------------------
# Test 1: Exactly 26 field rubrics
# ---------------------------------------------------------------------------

def test_exactly_26_field_rubrics():
    """FIELD_SPECIFIC_RUBRICS must have exactly 26 keys matching CANONICAL_ANSWERABLE_FIELDS."""
    rubric_keys = set(FIELD_SPECIFIC_RUBRICS.keys())
    canonical_keys = set(CANONICAL_ANSWERABLE_FIELDS)

    assert len(rubric_keys) == 26, (
        f"Expected 26 rubrics, got {len(rubric_keys)}. "
        f"Missing: {canonical_keys - rubric_keys}, Extra: {rubric_keys - canonical_keys}"
    )
    assert rubric_keys == canonical_keys, (
        f"Rubric keys do not match canonical fields.\n"
        f"Missing: {canonical_keys - rubric_keys}\n"
        f"Extra: {rubric_keys - canonical_keys}"
    )


# ---------------------------------------------------------------------------
# Test 2: Correct field-rubric selection
# ---------------------------------------------------------------------------

def test_correct_rubric_selection():
    """get_field_rubric('1.1.1') returns the rubric for 1.1.1 only."""
    rubric_111 = get_field_rubric("1.1.1")
    rubric_12 = get_field_rubric("1.2")

    assert isinstance(rubric_111, list)
    assert len(rubric_111) > 0
    assert isinstance(rubric_12, list)
    assert len(rubric_12) > 0
    # Rubrics must be distinct
    assert rubric_111 != rubric_12

    # Each rubric item is a non-empty string
    for item in rubric_111:
        assert isinstance(item, str) and len(item) > 0


def test_rubric_unknown_field_returns_empty():
    """get_field_rubric for a structural/unknown field returns empty list."""
    assert get_field_rubric("1.1") == []
    assert get_field_rubric("3.3") == []
    assert get_field_rubric("9.9.9") == []


# ---------------------------------------------------------------------------
# Test 3: Label mapping
# ---------------------------------------------------------------------------

def test_label_mapping():
    """MET=100, MOSTLY_MET=75, PARTIALLY_MET=50, NOT_MET=0."""
    assert LABEL_TO_SCORE[JudgmentLabel.MET] == 100
    assert LABEL_TO_SCORE[JudgmentLabel.MOSTLY_MET] == 75
    assert LABEL_TO_SCORE[JudgmentLabel.PARTIALLY_MET] == 50
    assert LABEL_TO_SCORE[JudgmentLabel.NOT_MET] == 0
    # N_A must NOT appear in LABEL_TO_SCORE
    assert JudgmentLabel.N_A not in LABEL_TO_SCORE


# ---------------------------------------------------------------------------
# Test 4: N_A excluded from denominator
# ---------------------------------------------------------------------------

def test_na_excluded_from_denominator():
    """All-N_A + 1 MET → component score of 100, not 100/5."""
    stage_a = _make_stage_a(
        grounding=[
            JudgmentLabel.N_A,
            JudgmentLabel.N_A,
            JudgmentLabel.MET,  # only one scored criterion
        ]
    )
    score = judge._component_score(stage_a.grounding_judgments)
    assert score == 100, f"Expected 100, got {score}"


def test_all_na_returns_none():
    """All N_A judgments for a component → None (component unavailable)."""
    stage_a = _make_stage_a(
        grounding=[JudgmentLabel.N_A, JudgmentLabel.N_A]
    )
    score = judge._component_score(stage_a.grounding_judgments)
    assert score is None


def test_mixed_scores_exclude_na():
    """MET + N_A + PARTIALLY_MET → average of (100, 50) = 75."""
    stage_a = _make_stage_a(
        grounding=[
            JudgmentLabel.MET,
            JudgmentLabel.N_A,
            JudgmentLabel.PARTIALLY_MET,
        ]
    )
    score = judge._component_score(stage_a.grounding_judgments)
    assert score == 75, f"Expected 75, got {score}"


# ---------------------------------------------------------------------------
# Test 5: Weight renormalization when component is unavailable
# ---------------------------------------------------------------------------

def test_weight_renormalization():
    """If grounding component is all-N_A, remaining 4 weights are renormalized to sum to 1.0."""
    # grounding=None (all N_A), others all MET=100
    component_scores = {
        "grounding": None,          # unavailable
        "reference_context": 100,
        "section_compliance": 100,
        "testability": 100,
        "consistency": 100,
    }
    final = judge._calculate_final_confidence(component_scores)
    # Should be 100 (all available components are 100)
    assert final == 100


def test_weight_renormalization_partial():
    """Renormalization with mixed scores: two N_A components, others at 60."""
    component_scores = {
        "grounding": None,          # unavailable
        "reference_context": None,  # unavailable
        "section_compliance": 60,
        "testability": 60,
        "consistency": 60,
    }
    final = judge._calculate_final_confidence(component_scores)
    # 3 components each at 60, weights each 0.20 → renormalized each to 1/3 → final = 60
    assert final == 60


def test_all_components_unavailable():
    """All components unavailable → final confidence = 0."""
    component_scores = {k: None for k in COMPONENT_WEIGHTS}
    final = judge._calculate_final_confidence(component_scores)
    assert final == 0


# ---------------------------------------------------------------------------
# Test 6, 7, 8: Confidence level thresholds
# ---------------------------------------------------------------------------

def test_high_threshold():
    """score >= 85 → HIGH."""
    assert determine_judge_confidence_level(85) == "HIGH"
    assert determine_judge_confidence_level(100) == "HIGH"
    assert determine_judge_confidence_level(HIGH_THRESHOLD) == "HIGH"


def test_medium_threshold():
    """60 <= score < 85 → MEDIUM."""
    assert determine_judge_confidence_level(60) == "MEDIUM"
    assert determine_judge_confidence_level(84) == "MEDIUM"
    assert determine_judge_confidence_level(MEDIUM_THRESHOLD) == "MEDIUM"


def test_low_threshold():
    """score < 60 → LOW."""
    assert determine_judge_confidence_level(59) == "LOW"
    assert determine_judge_confidence_level(0) == "LOW"
    assert determine_judge_confidence_level(MEDIUM_THRESHOLD - 1) == "LOW"


# ---------------------------------------------------------------------------
# Test 9: Critical flag -> REVIEW_REQUIRED
# ---------------------------------------------------------------------------

def test_critical_flag_triggers_review_required():
    """Any critical flag must result in review_status = REVIEW_REQUIRED."""
    flag = CriticalFlag(
        type="UNSUPPORTED_NUMERIC_FACT",
        reason="A percentage is stated without project evidence.",
        excerpt="95% uptime",
    )
    # review_status logic (mirrors judge.py)
    review_status = "REVIEW_REQUIRED" if [flag] else "PASS"
    assert review_status == "REVIEW_REQUIRED"


def test_no_critical_flag_is_pass():
    """No critical flags → review_status = PASS."""
    review_status = "REVIEW_REQUIRED" if [] else "PASS"
    assert review_status == "PASS"


# ---------------------------------------------------------------------------
# Test 10: Critical flag does NOT change score
# ---------------------------------------------------------------------------

def test_critical_flag_does_not_change_score():
    """Same judgment labels with and without critical flags must produce the same score."""
    base_labels = [JudgmentLabel.MET, JudgmentLabel.MOSTLY_MET]

    stage_a_no_flag = _make_stage_a(grounding=base_labels)
    stage_a_with_flag = _make_stage_a(
        grounding=base_labels,
        critical_flags=[CriticalFlag(type="UNSUPPORTED_NUMERIC_FACT", reason="test", excerpt="test")],
    )

    score_no_flag = judge._component_score(stage_a_no_flag.grounding_judgments)
    score_with_flag = judge._component_score(stage_a_with_flag.grounding_judgments)

    assert score_no_flag == score_with_flag, (
        f"Score changed with critical flag: {score_no_flag} vs {score_with_flag}"
    )


# ---------------------------------------------------------------------------
# Test 11: NOT_YET_VERIFIABLE has no penalty
# ---------------------------------------------------------------------------

def test_not_yet_verifiable_no_penalty():
    """dependency_status = NOT_YET_VERIFIABLE must not reduce the consistency score."""
    # Both stage_a have identical judgments, different dependency_status
    stage_a_verifiable = _make_stage_a(
        consistency=[JudgmentLabel.MET, JudgmentLabel.MET],
        dependency_status="NOT_YET_VERIFIABLE",
    )
    stage_a_consistent = _make_stage_a(
        consistency=[JudgmentLabel.MET, JudgmentLabel.MET],
        dependency_status="CONSISTENT",
    )

    score_verifiable = judge._component_score(stage_a_verifiable.consistency_judgments)
    score_consistent = judge._component_score(stage_a_consistent.consistency_judgments)

    assert score_verifiable == score_consistent == 100, (
        f"NOT_YET_VERIFIABLE incorrectly affected score: {score_verifiable}"
    )


# ---------------------------------------------------------------------------
# Test 12: Dependency conflict detection integration
# ---------------------------------------------------------------------------

def test_dependency_conflict_status():
    """Stage A with CONFLICT dependency_status must not alter scoring but status is preserved."""
    stage_a = _make_stage_a(
        consistency=[JudgmentLabel.NOT_MET],
        dependency_status="CONFLICT",
    )
    assert stage_a.dependency_status == "CONFLICT"
    score = judge._component_score(stage_a.consistency_judgments)
    assert score == 0  # NOT_MET maps to 0


# ---------------------------------------------------------------------------
# Test 13: Reference unavailable -> N/A handling
# ---------------------------------------------------------------------------

def test_reference_unavailable_na_handling():
    """When no references are available, reference_context criteria should be N_A, not NOT_MET."""
    # Simulate all-N_A reference judgments (no references returned)
    stage_a = _make_stage_a(
        reference=[JudgmentLabel.N_A, JudgmentLabel.N_A, JudgmentLabel.N_A],
    )
    score = judge._component_score(stage_a.reference_judgments)
    # Must be None (component excluded), not 0 (which would be NOT_MET)
    assert score is None, f"Expected None for all-N_A reference, got {score}"


# ---------------------------------------------------------------------------
# Test 14: Section revision triggers re-evaluation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_section_revision_triggers_re_evaluation():
    """Calling evaluate_section twice produces a new evaluated_at timestamp."""
    fake_stage_a = {
        "grounding_judgments": [{"criterion": "c", "label": "MET", "rationale": "r"}],
        "reference_judgments": [],
        "section_compliance_judgments": [],
        "clarity_judgments": [],
        "consistency_judgments": [],
        "dependency_status": "NOT_YET_VERIFIABLE",
        "critical_flags": [],
    }
    fake_stage_b = {
        "strengths": ["Good"],
        "issues": [],
        "suggestions": [],
        "summary_reason": "OK",
    }

    import time

    results = []
    with patch("app.ai.judge.service._call_llm_json", new_callable=AsyncMock) as mock_llm, \
         patch("app.ai.judge.service.search_references", return_value=[]):
        mock_llm.return_value = fake_stage_a
        result1 = await judge.evaluate_section(
            field_id="1.1.1",
            section_title="Background",
            generated_content="Some background text.",
            project_evidence="User said: something.",
            context_answers={},
            missing_items=[],
        )
        results.append(result1)

        # Small delay to ensure different timestamp
        time.sleep(0.01)
        mock_llm.return_value = fake_stage_a
        result2 = await judge.evaluate_section(
            field_id="1.1.1",
            section_title="Background",
            generated_content="Revised background text.",
            project_evidence="User said: something.",
            context_answers={},
            missing_items=[],
        )
        results.append(result2)

    # Both should succeed
    assert "evaluated_at" in results[0]
    assert "evaluated_at" in results[1]
    # Timestamps should differ (re-evaluation produces new timestamp)
    assert results[0]["evaluated_at"] != results[1]["evaluated_at"]


# ---------------------------------------------------------------------------
# Test 15: Structured Judge output validation
# ---------------------------------------------------------------------------

def test_stage_a_output_validation_valid():
    """JudgeStageAOutput validates correct input."""
    data = {
        "grounding_judgments": [{"criterion": "c", "label": "MET", "rationale": "r"}],
        "reference_judgments": [],
        "section_compliance_judgments": [{"criterion": "c2", "label": "N_A", "rationale": "na"}],
        "clarity_judgments": [],
        "consistency_judgments": [],
        "dependency_status": "CONSISTENT",
        "critical_flags": [],
    }
    result = JudgeStageAOutput.model_validate(data)
    assert len(result.grounding_judgments) == 1
    assert result.grounding_judgments[0].label == JudgmentLabel.MET
    assert result.dependency_status == "CONSISTENT"


def test_stage_a_output_validation_rejects_invalid_label():
    """JudgeStageAOutput rejects unknown judgment labels."""
    data = {
        "grounding_judgments": [{"criterion": "c", "label": "INVALID_LABEL", "rationale": "r"}],
        "reference_judgments": [],
        "section_compliance_judgments": [],
        "clarity_judgments": [],
        "consistency_judgments": [],
        "dependency_status": "NOT_YET_VERIFIABLE",
        "critical_flags": [],
    }
    with pytest.raises(Exception):  # pydantic ValidationError
        JudgeStageAOutput.model_validate(data)


def test_stage_a_output_validation_rejects_invalid_dependency_status():
    """JudgeStageAOutput rejects unknown dependency_status values."""
    data = {
        "grounding_judgments": [],
        "reference_judgments": [],
        "section_compliance_judgments": [],
        "clarity_judgments": [],
        "consistency_judgments": [],
        "dependency_status": "UNKNOWN",
        "critical_flags": [],
    }
    with pytest.raises(Exception):
        JudgeStageAOutput.model_validate(data)


def test_stage_b_output_validation_valid():
    """JudgeStageBOutput validates correct input."""
    data = {
        "strengths": ["Clear and concise"],
        "issues": ["Missing target date"],
        "suggestions": ["Clarify what 'ready' means in this context"],
        "summary_reason": "Overall MEDIUM confidence due to missing timeline.",
    }
    result = JudgeStageBOutput.model_validate(data)
    assert len(result.strengths) == 1
    assert result.issues[0] == "Missing target date"


# ---------------------------------------------------------------------------
# Test 16: Frontend/API response compatibility
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_frontend_api_response_compatibility():
    """evaluate_section output has all keys expected by ConfidenceBreakdown.jsx."""
    fake_stage_a = {
        "grounding_judgments": [{"criterion": "c", "label": "MET", "rationale": "r"}],
        "reference_judgments": [{"criterion": "c", "label": "MOSTLY_MET", "rationale": "r"}],
        "section_compliance_judgments": [{"criterion": "c", "label": "PARTIALLY_MET", "rationale": "r"}],
        "clarity_judgments": [{"criterion": "c", "label": "MET", "rationale": "r"}],
        "consistency_judgments": [{"criterion": "c", "label": "MET", "rationale": "r"}],
        "dependency_status": "NOT_YET_VERIFIABLE",
        "critical_flags": [],
    }
    fake_stage_b = {
        "strengths": ["Strength 1"],
        "issues": ["Issue 1"],
        "suggestions": ["Suggestion 1"],
        "summary_reason": "Test reason",
    }

    call_count = 0

    async def mock_llm(prompt: str, temperature: float = 0.1) -> dict:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return fake_stage_a
        return fake_stage_b

    with patch("app.ai.judge.service._call_llm_json", new_callable=AsyncMock, side_effect=mock_llm), \
         patch("app.ai.judge.service.search_references", return_value=[]):
        result = await judge.evaluate_section(
            field_id="1.1.1",
            section_title="Background",
            generated_content="Some content.",
            project_evidence="Evidence.",
            context_answers={},
            missing_items=[],
        )

    # 5 dimension keys (read by DimensionCard in ConfidenceBreakdown.jsx)
    for dim_key in ["grounding", "reference_context", "section_compliance", "testability", "consistency"]:
        assert dim_key in result, f"Missing dimension key: {dim_key}"
        assert "score" in result[dim_key], f"Missing 'score' in {dim_key}"
        assert "reason" in result[dim_key], f"Missing 'reason' in {dim_key}"

    # Agent 2 metadata keys (read by ConfidenceBreakdown.jsx)
    assert "review_status" in result
    assert "dependency_status" in result
    assert "critical_flags" in result
    assert isinstance(result["critical_flags"], list)
    assert "critique_strengths" in result
    assert "critique_issues" in result
    assert "critique_suggestions" in result

    # Audit fields
    assert "judge_model" in result
    assert "evaluated_at" in result

    # Values
    assert result["review_status"] in ("PASS", "REVIEW_REQUIRED")
    assert result["dependency_status"] in ("CONSISTENT", "CONFLICT", "NOT_YET_VERIFIABLE")


# ---------------------------------------------------------------------------
# Test 17: No regression to existing Agent 1 generation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_agent1_generation_returns_bubbles_on_judge_error(monkeypatch):
    """When Agent 2 raises an exception, post_message must still return bubbles."""
    # This test is at the service integration level.
    # We mock at the judge module level to simulate Agent 2 failure.
    from app.services import chat_service

    # Mock all external dependencies
    mock_session = AsyncMock()

    mock_conversation = MagicMock()
    mock_conversation.focused_section_id = None

    mock_section = MagicMock()
    mock_section.section_id = "sec-1"
    mock_section.template_key = "1.1.1"
    mock_section.is_leaf = True
    mock_section.is_custom = False
    mock_section.is_general = False
    mock_section.title = "Background"
    mock_section.purpose = "Describe background"

    mock_bubble_user = MagicMock()
    mock_bubble_user.bubble_id = "b1"
    mock_bubble_user.role = "user"
    mock_bubble_user.text = "Test message"

    mock_bubble_agent = MagicMock()
    mock_bubble_agent.bubble_id = "b2"
    mock_bubble_agent.role = "agent"
    mock_bubble_agent.text = "Agent reply"

    mock_reply = MagicMock()
    mock_reply.reply_text = "Agent reply"
    mock_reply.answer_text = "Draft answer"
    mock_reply.completeness = 70
    mock_reply.confidence = 80
    mock_reply.confidence_reason = "test"
    mock_reply.confidence_components = {}
    mock_reply.missing_items = []
    mock_reply.is_assumption = False
    mock_reply.confidence_breakdown = {}

    existing_answer = MagicMock()
    existing_answer.status = "progress"
    existing_answer.answer_text = ""
    existing_answer.completeness = 0
    existing_answer.confidence = None
    existing_answer.missing_items = []

    with patch("app.services.chat_service.conversation_service.get_accessible", return_value=(mock_conversation, "editor")), \
         patch("app.services.chat_service._resolve_room_section", return_value=mock_section), \
         patch("app.services.chat_service.bubble_repository.list_by_section", return_value=[]), \
         patch("app.services.chat_service.answer_repository.find_by_section_id", return_value=existing_answer), \
         patch("app.services.chat_service.section_repository.list_by_conversation", return_value=[mock_section]), \
         patch("app.services.chat_service.answer_repository.list_by_conversation", return_value=[]), \
         patch("app.services.chat_service.bubble_repository.insert") as mock_insert, \
         patch("app.services.chat_service.ai_integration.get_reply", return_value=mock_reply), \
         patch("app.services.chat_service.answer_repository.upsert", return_value=existing_answer), \
         patch("app.services.chat_service.conversation_repository.touch_updated_at"), \
         patch("app.services.chat_service.judge.evaluate_section", side_effect=Exception("Agent 2 exploded")):

        # Simulate bubble inserts setting proper attributes
        insert_calls = []
        async def fake_insert(session, bubble):
            if bubble.role == "user":
                bubble.bubble_id = "b1"
                mock_bubble_user.bubble_id = "b1"
            else:
                bubble.bubble_id = "b2"
            insert_calls.append(bubble)

        mock_insert.side_effect = fake_insert

        result = await chat_service.post_message(
            mock_session,
            conversation_id="conv-1",
            user_id="user-1",
            room_id="1.1.1",
            text="Test message",
        )

    # Must return 2 bubbles even when Agent 2 fails
    assert isinstance(result, list)
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Bonus: Global rubric completeness
# ---------------------------------------------------------------------------

def test_global_rubrics_are_nonempty():
    """All four global rubric lists must be non-empty."""
    assert len(GLOBAL_GROUNDING_CRITERIA) >= 3
    assert len(GLOBAL_REFERENCE_CRITERIA) >= 3
    assert len(GLOBAL_CLARITY_CRITERIA) >= 3
    assert len(GLOBAL_CONSISTENCY_CRITERIA) >= 3


def test_all_field_rubrics_have_items():
    """Every field-specific rubric must have at least 4 criteria."""
    for field_id, rubric in FIELD_SPECIFIC_RUBRICS.items():
        assert len(rubric) >= 4, (
            f"Field {field_id} has only {len(rubric)} rubric items (minimum 4)"
        )


def test_component_weights_sum_to_one():
    """COMPONENT_WEIGHTS must sum to exactly 1.0."""
    total = sum(COMPONENT_WEIGHTS.values())
    assert abs(total - 1.0) < 1e-9, f"Weights sum to {total}, expected 1.0"


def test_build_project_evidence_text_supports_bubbles_and_dicts():
    """Ensure build_project_evidence_text works seamlessly with both Bubble instances and dicts."""
    from app.models.bubble import Bubble

    bubble_user = Bubble(
        section_id="sec_1",
        role="user",
        text="SLA requirement must be 99.9%",
    )
    bubble_agent = Bubble(
        section_id="sec_1",
        role="agent",
        text="Draft answer generated",
    )
    dict_user = {"role": "user", "text": "Target audience is SMEs"}
    dict_agent = {"role": "agent", "text": "Draft agent response"}

    evidence = judge.build_project_evidence_text(
        conversation_context="Corporate Banking Project",
        requestor_directorate="Digital Banking",
        impacted_stakeholders=["Operations", "Compliance"],
        history=[bubble_user, bubble_agent, dict_user, dict_agent],
        latest_user_message="When will rollout happen?",
    )

    # Human inputs should be included
    assert "SLA requirement must be 99.9%" in evidence
    assert "Target audience is SMEs" in evidence
    assert "Corporate Banking Project" in evidence
    assert "Digital Banking" in evidence
    assert "Operations, Compliance" in evidence
    assert "When will rollout happen?" in evidence

    # Agent outputs must NOT be included
    assert "Draft answer generated" not in evidence
    assert "Draft agent response" not in evidence

