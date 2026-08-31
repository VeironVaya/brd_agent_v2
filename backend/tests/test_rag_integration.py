"""
tests/test_rag_integration.py
=============================
Focused Integration Test Suite verifying the complete end-to-end integration
between brd-app and brd-agent.

Verifies:
1. Canonical leaf template_key forwarding & taxonomy alignment.
2. Official SYSTEM_PROMPT priority & non-injection of Reference BRDs into generation prompt.
3. Anti-hallucination fact verification (unconfirmed numeric/metric claims).
4. Agent 1 Drafting Contract: generates draft, completeness, missing_items, leaves confidence as None.
5. Safe Canonical Section Flow: RAG retrieval uses exact field_id and draft answer; Agent 2 evaluation persists confidence, reason, and 5-dimension breakdown.
6. Unsupported Fact Flow: hard-validator findings reach Agent 2; critical contradiction produces REVIEW_REQUIRED without mathematical double-penalty.
7. General Chat Flow: executes Agent 1 normally, skips RAG retrieval, skips Agent 2, creates no Answer record.
8. DTO & API boundary: nullable component scores (None for N/A), full critique fields exposure, and backward compatibility.
"""

import json
from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient

from app.models.answer import Answer
from app.repositories import answer_repository, section_repository
from app.services import ai_integration, chat_service, document_service, template_service
from app.services.ai_integration import AgentReply
from app.dtos.conversation_dtos import (
    AnswerDto,
    ConfidenceBreakdownDto,
    ConfidenceDimensionDto,
    CriticalFlagDto,
    ConversationDetailResponse,
)
from app.ai.rag import (
    CANONICAL_FIELDS_META,
    CANONICAL_FIELD_ORDER,
    SearchResult,
    validate_project_facts,
)
from .helpers import create_conversation, register_and_login




# ---------------------------------------------------------------------------
# 1. Canonical Taxonomy Alignment Verification
# ---------------------------------------------------------------------------
def test_all_26_canonical_field_ids_match():
    """Verifies that all 26 brd-app leaf template_keys match brd-agent canonical IDs exactly."""
    app_leaves = template_service.FIELD_ORDER
    agent_fields = list(CANONICAL_FIELDS_META.keys())

    assert len(app_leaves) == 26
    assert len(agent_fields) == 26
    assert app_leaves == agent_fields
    assert app_leaves == CANONICAL_FIELD_ORDER


# ---------------------------------------------------------------------------
# 2. SYSTEM_PROMPT Integrity Check
# ---------------------------------------------------------------------------
def test_official_system_prompt_integrity():
    """Verifies that official SYSTEM_PROMPT contains the Business Analyst persona and no RAG injections."""
    prompt = ai_integration.SYSTEM_PROMPT
    assert "You are an expert, senior Business Analyst" in prompt
    assert "STRICT QUALITY BAR" in prompt
    assert "SECTION-SPECIFIC RULES" in prompt
    assert "RETRIEVED REFERENCE" not in prompt
    assert "[R1]" not in prompt


# ---------------------------------------------------------------------------
# 3. Anti-Hallucination Fact Verification Tests
# ---------------------------------------------------------------------------
def test_anti_hallucination_rejects_unconfirmed_numeric_facts():
    """C1 = 1 hour, Generated = 2 hours -> Unsafe."""
    project_evidence = "Invoice generation must complete within 1 hour."
    generated_text = "The system shall complete invoice generation within 2 hours."

    result = validate_project_facts(generated_text, project_evidence)
    assert result.is_safe is False
    assert "2" in result.unsupported_claims
    assert result.reason is not None


def test_anti_hallucination_accepts_supported_numeric_facts():
    """C1 = 1 hour, Generated = 1 hour -> Safe."""
    project_evidence = "Invoice generation must complete within 1 hour."
    generated_text = "The system shall complete invoice generation within 1 hour."

    result = validate_project_facts(generated_text, project_evidence)
    assert result.is_safe is True
    assert len(result.unsupported_claims) == 0


def test_anti_hallucination_rejects_unconfirmed_percentages_and_currencies():
    project_evidence = "We need automated billing retries."
    generated_text = "The system shall charge a fee of $500 with 99.99% reliability."

    result = validate_project_facts(generated_text, project_evidence)
    assert result.is_safe is False
    assert "$500" in result.unsupported_claims or "500" in result.unsupported_claims
    assert "99.99%" in result.unsupported_claims or "99.99" in result.unsupported_claims


# ---------------------------------------------------------------------------
# 4. Agent 1 Drafting Contract Test
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_agent1_drafting_contract_returns_draft_without_confidence():
    """Agent 1 Drafting Contract: requires room_id, produces draft content and completeness, but leaves confidence as None (Agent 2 owns confidence)."""
    mock_llm_response = {
        "reply_text": "I have documented the settlement retry rules.",
        "answer_text": "The system shall automatically retry failed recurring subscription payments.",
        "completeness": 80,
        "missing_items": ["Specific retry timing"],
        "is_assumption": False,
    }

    mock_chat_completion = AsyncMock()
    mock_chat_completion.choices = [
        AsyncMock(message=AsyncMock(content=json.dumps(mock_llm_response)))
    ]

    from app.config import settings

    with patch.object(settings, "groq_api_key", "test-key"), \
         patch("litellm.acompletion", new=AsyncMock(return_value=mock_chat_completion)):

        reply = await ai_integration.get_reply(
            room_id="3.7",
            room_title="Settlement Plan",
            room_purpose="Define settlement workflows",
            message_text="Failed recurring subscription payments should be retried automatically.",
            history=[],
            current_answer=None,
            field_id="3.7",
        )

        assert reply.reply_text == mock_llm_response["reply_text"]
        assert reply.answer_text == mock_llm_response["answer_text"]
        assert reply.completeness == 80
        assert reply.missing_items == ["Specific retry timing"]
        # Agent 1 contract: confidence fields must remain None
        assert reply.confidence is None
        assert reply.confidence_reason is None
        assert reply.confidence_components is None
        assert reply.confidence_breakdown is None


# ---------------------------------------------------------------------------
# 5. Post-Generation Flow: Safe Canonical Section Orchestration
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_safe_canonical_section_orchestrates_rag_and_agent2_confidence(client: AsyncClient):
    """Canonical Section Safe Flow:
    1. Agent 1 drafts section with completeness=80, confidence=None
    2. Hard validator PASS
    3. RAG search_references called with generated answer_text and exact field_id '3.7'
    4. Agent 2 evaluate_section invoked for canonical field
    5. Agent 2 confidence, reason, and 5-dimension breakdown persisted to Answer and returned by API
    6. Agent 1 completeness (80) is preserved.
    """
    auth = await register_and_login(client)
    headers = auth["headers"]
    conv_id = await create_conversation(client, headers, title="Payment Gateway BRD")

    mock_agent1_reply = AgentReply(
        reply_text="I have documented the settlement retry rules.",
        answer_text="The system shall automatically retry failed recurring subscription payments.",
        completeness=80,
        confidence=None,
        confidence_reason=None,
        missing_items=["Specific retry timing"],
        is_assumption=False,
    )

    mock_search_results = [
        SearchResult(
            document_key="doc1",
            document_title="Sample BRD",
            field_id="3.7",
            field_title="Settlement Plan",
            chunk_index=0,
            content="Failed recurring subscription payments are retried automatically.",
            similarity_score=0.88,
        )
    ]

    mock_agent2_result = {
        "final_confidence": 85,
        "confidence_level": "HIGH",
        "confidence_reason": "Evaluated with HIGH confidence (85%). Strong grounding in user requirements.",
        "component_scores": {
            "grounding": 90,
            "reference_context": 85,
            "section_compliance": 80,
            "testability": 85,
            "consistency": 85,
        },
        "review_status": "PASS",
        "dependency_status": "NOT_YET_VERIFIABLE",
        "critical_flags": [],
        "confidence_breakdown": {
            "final_confidence": 85,
            "confidence_level": "HIGH",
            "grounding": {"score": 90, "reason": "Consistent with user requirements."},
            "reference_context": {"score": 85, "reason": "Aligned with payment standards."},
            "section_compliance": {"score": 80, "reason": "Meets section criteria."},
            "testability": {"score": 85, "reason": "Clear retry logic."},
            "consistency": {"score": 85, "reason": "Consistent across sections."},
            "review_status": "PASS",
            "dependency_status": "NOT_YET_VERIFIABLE",
            "critical_flags": [],
            "critique_strengths": ["Clear retry mechanism."],
            "critique_issues": [],
            "critique_suggestions": ["Specify retry intervals if possible."],
            "critique_summary": "Evaluated with HIGH confidence (85%). Strong grounding in user requirements.",
            "judge_model": "gemini/gemini-2.0-flash",
            "evaluated_at": "2026-08-28T12:00:00Z",
        },
    }

    with patch("app.services.chat_service.ai_integration.get_reply", new=AsyncMock(return_value=mock_agent1_reply)), \
         patch("app.services.chat_service.search_references", return_value=mock_search_results) as mock_search, \
         patch("app.services.chat_service.judge.evaluate_section", new=AsyncMock(return_value=mock_agent2_result)) as mock_judge:

        # Post message to room 3.7
        res = await client.post(
            f"/api/conversations/{conv_id}/rooms/3.7/messages",
            json={"text": "Failed recurring subscription payments should be retried automatically."},
            headers=headers,
        )
        assert res.status_code == 200, res.text

        # Verify search_references was called with generated answer_text and exact field_id '3.7'
        mock_search.assert_called_once_with(mock_agent1_reply.answer_text, "3.7", 3)

        # Verify Agent 2 was invoked
        mock_judge.assert_called_once()
        judge_call_kwargs = mock_judge.call_args.kwargs
        assert judge_call_kwargs["field_id"] == "3.7"
        assert judge_call_kwargs["generated_content"] == mock_agent1_reply.answer_text
        assert "PASS" in judge_call_kwargs["validator_findings"]

        # Fetch conversation details via API
        detail_res = await client.get(f"/api/conversations/{conv_id}", headers=headers)
        assert detail_res.status_code == 200
        data = detail_res.json()

        answer_37 = data["answers"].get("3.7")
        assert answer_37 is not None
        assert answer_37["status"] == "progress"
        assert answer_37["completeness"] == 80  # Agent 1 completeness
        assert answer_37["confidence"] == 85  # Agent 2 confidence
        assert answer_37["confidence_reason"] == mock_agent2_result["confidence_reason"]

        # Breakdown checks
        breakdown = answer_37["confidence_breakdown"]
        assert breakdown is not None
        assert breakdown["final_confidence"] == 85
        assert breakdown["confidence_level"] == "HIGH"
        assert breakdown["review_status"] == "PASS"
        assert breakdown["grounding"]["score"] == 90
        assert breakdown["critique_strengths"] == ["Clear retry mechanism."]


# ---------------------------------------------------------------------------
# 6. Post-Generation Flow: Unsupported Fact & Contradiction Handling
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_unsupported_fact_passes_findings_to_agent2_and_persists_review_required(client: AsyncClient):
    """Unsupported fact flow:
    1. User context/message: 'Invoice generation must complete within 1 hour.'
    2. Agent 1 draft hallucinates: 'The system shall complete invoice generation within 2 hours.'
    3. Hard validator flags unsupported numeric claim '2'.
    4. Hard validator findings reach Agent 2 evaluate_section.
    5. Agent 2 identifies critical contradiction and flags REVIEW_REQUIRED.
    6. Critical flag does not mathematically subtract score (separate from numerical confidence).
    """
    auth = await register_and_login(client)
    headers = auth["headers"]
    res = await client.post(
        "/api/conversations",
        json={"title": "Billing SLA BRD", "context": "Invoice generation must complete within 1 hour."},
        headers=headers,
    )
    assert res.status_code == 201, res.text
    conv_id = res.json()["id"]

    mock_agent1_reply = AgentReply(
        reply_text="I set the SLA to 2 hours.",
        answer_text="The system shall complete invoice generation within 2 hours.",
        completeness=90,
        confidence=None,
        confidence_reason=None,
        missing_items=[],
        is_assumption=False,
    )

    mock_search_results = []

    mock_agent2_result = {
        "final_confidence": 70,
        "confidence_level": "MEDIUM",
        "confidence_reason": "SLA contradicts user requirement of 1 hour.",
        "component_scores": {
            "grounding": 50,
            "reference_context": None,
            "section_compliance": 80,
            "testability": 80,
            "consistency": 70,
        },
        "review_status": "REVIEW_REQUIRED",
        "dependency_status": "NOT_YET_VERIFIABLE",
        "critical_flags": [
            {
                "type": "UNSUPPORTED_NUMERIC_FACT",
                "reason": "Claimed 2 hours but user specified 1 hour.",
                "excerpt": "within 2 hours",
            }
        ],
        "confidence_breakdown": {
            "final_confidence": 70,
            "confidence_level": "MEDIUM",
            "grounding": {"score": 50, "reason": "Contradicts project context."},
            "reference_context": {"score": None, "reason": "No applicable criteria."},
            "section_compliance": {"score": 80, "reason": "Meets criteria."},
            "testability": {"score": 80, "reason": "Testable metric."},
            "consistency": {"score": 70, "reason": "Cross-section consistency."},
            "review_status": "REVIEW_REQUIRED",
            "dependency_status": "NOT_YET_VERIFIABLE",
            "critical_flags": [
                {
                    "type": "UNSUPPORTED_NUMERIC_FACT",
                    "reason": "Claimed 2 hours but user specified 1 hour.",
                    "excerpt": "within 2 hours",
                }
            ],
            "critique_strengths": ["Clear metric defined."],
            "critique_issues": ["2-hour SLA contradicts user requirement."],
            "critique_suggestions": ["Align SLA with user-specified 1 hour requirement."],
            "critique_summary": "SLA contradicts user requirement of 1 hour.",
            "judge_model": "gemini/gemini-2.0-flash",
            "evaluated_at": "2026-08-28T12:00:00Z",
        },
    }

    with patch("app.services.chat_service.ai_integration.get_reply", new=AsyncMock(return_value=mock_agent1_reply)), \
         patch("app.services.chat_service.search_references", return_value=mock_search_results), \
         patch("app.services.chat_service.judge.evaluate_section", new=AsyncMock(return_value=mock_agent2_result)) as mock_judge:

        # Post message to room 1.1.1
        res = await client.post(
            f"/api/conversations/{conv_id}/rooms/1.1.1/messages",
            json={"text": "Invoice generation must complete within 1 hour."},
            headers=headers,
        )
        assert res.status_code == 200, res.text

        # Verify Agent 2 received validator findings with FLAGGED UNSUPPORTED CLAIMS
        mock_judge.assert_called_once()
        judge_call_kwargs = mock_judge.call_args.kwargs
        assert "FLAGGED UNSUPPORTED CLAIMS" in judge_call_kwargs["validator_findings"]
        assert "2" in judge_call_kwargs["validator_findings"]

        # Fetch conversation details via API
        detail_res = await client.get(f"/api/conversations/{conv_id}", headers=headers)
        assert detail_res.status_code == 200
        data = detail_res.json()

        answer_111 = data["answers"].get("1.1.1")
        assert answer_111 is not None
        assert answer_111["confidence"] == 70  # Score is not mathematically subtracted by flag
        assert answer_111["confidence_breakdown"]["review_status"] == "REVIEW_REQUIRED"
        assert len(answer_111["confidence_breakdown"]["critical_flags"]) == 1
        assert answer_111["confidence_breakdown"]["critical_flags"][0]["type"] == "UNSUPPORTED_NUMERIC_FACT"


# ---------------------------------------------------------------------------
# 7. General Chat & Non-Canonical Section Skip Canonical Validation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_general_chat_skips_rag_and_agent2_evaluation(client: AsyncClient):
    """General chat is outside canonical BRD sections:
    - Agent 1 executes normally
    - RAG search_references is NOT invoked
    - Agent 2 evaluate_section is NOT invoked
    - No canonical BRD Answer record is created
    """
    auth = await register_and_login(client)
    headers = auth["headers"]
    conv_id = await create_conversation(client, headers, title="General Chat BRD")

    mock_agent1_reply = AgentReply(
        reply_text="Let's brainstorm overall project goals.",
        answer_text=None,
        completeness=0,
        confidence=None,
        confidence_reason=None,
        missing_items=[],
        is_assumption=False,
    )

    with patch("app.services.chat_service.ai_integration.get_reply", new=AsyncMock(return_value=mock_agent1_reply)) as mock_agent1, \
         patch("app.services.chat_service.search_references") as mock_search, \
         patch("app.services.chat_service.judge.evaluate_section") as mock_judge:

        # Post message to general room
        res = await client.post(
            f"/api/conversations/{conv_id}/rooms/general/messages",
            json={"text": "Hi, let's start the project."},
            headers=headers,
        )
        assert res.status_code == 200, res.text

        # Verify Agent 1 was called with room_id and field_id=None
        mock_agent1.assert_called_once()
        assert mock_agent1.call_args.kwargs["room_id"] is not None
        assert mock_agent1.call_args.kwargs["field_id"] is None

        # Verify RAG and Agent 2 were skipped
        mock_search.assert_not_called()
        mock_judge.assert_not_called()

        # Verify no answers were created for 'general'
        detail_res = await client.get(f"/api/conversations/{conv_id}", headers=headers)
        assert detail_res.status_code == 200
        data = detail_res.json()
        assert "general" not in data["answers"]


# ---------------------------------------------------------------------------
# 8. DTO Nullable Scores & Exposure Serialization Tests
# ---------------------------------------------------------------------------
def test_confidence_breakdown_dto_handles_nullable_component_scores():
    """N/A component scores (None) must parse and serialize as None/null, NOT 0."""
    data = {
        "grounding": {"score": None, "reason": "No applicable criteria."},
        "reference_context": {"score": 85, "reason": "Aligned."},
        "section_compliance": {"score": None, "reason": "Not applicable."},
        "testability": {"score": 75, "reason": "Clear."},
        "consistency": {"score": None, "reason": "Not applicable."},
        "review_status": "PASS",
        "dependency_status": "NOT_YET_VERIFIABLE",
    }
    dto = ConfidenceBreakdownDto.model_validate(data)
    assert dto.grounding is not None
    assert dto.grounding.score is None
    assert dto.section_compliance is not None
    assert dto.section_compliance.score is None
    assert dto.consistency is not None
    assert dto.consistency.score is None
    assert dto.reference_context is not None
    assert dto.reference_context.score == 85

    dumped = dto.model_dump()
    assert dumped["grounding"]["score"] is None
    assert dumped["grounding"]["score"] != 0


def test_confidence_breakdown_dto_full_critique_fields_survive_serialization():
    """All Agent 2 critique, flags, and audit fields serialize correctly in DTO."""
    data = {
        "final_confidence": 85,
        "confidence_level": "HIGH",
        "grounding": {"score": 90, "reason": "Good"},
        "reference_context": {"score": 85, "reason": "Good"},
        "section_compliance": {"score": 80, "reason": "Good"},
        "testability": {"score": 85, "reason": "Good"},
        "consistency": {"score": 85, "reason": "Good"},
        "review_status": "REVIEW_REQUIRED",
        "dependency_status": "CONFLICT",
        "critical_flags": [{"type": "CONTRADICTION", "reason": "Contradicts section 3.1", "excerpt": "foo"}],
        "critique_strengths": ["Clear requirements"],
        "critique_issues": ["Contradicts upstream"],
        "critique_suggestions": ["Align with 3.1"],
        "critique_summary": "Review required due to contradiction.",
        "judge_model": "gemini/gemini-2.0-flash",
        "evaluated_at": "2026-08-28T14:00:00Z",
    }
    dto = ConfidenceBreakdownDto.model_validate(data)
    assert dto.review_status == "REVIEW_REQUIRED"
    assert dto.dependency_status == "CONFLICT"
    assert dto.critical_flags is not None
    assert len(dto.critical_flags) == 1
    assert dto.critical_flags[0].type == "CONTRADICTION"
    assert dto.critical_flags[0].excerpt == "foo"
    assert dto.critique_strengths == ["Clear requirements"]
    assert dto.critique_issues == ["Contradicts upstream"]
    assert dto.critique_suggestions == ["Align with 3.1"]
    assert dto.critique_summary == "Review required due to contradiction."
    assert dto.judge_model == "gemini/gemini-2.0-flash"
    assert dto.evaluated_at == "2026-08-28T14:00:00Z"


def test_backward_compatibility_with_minimal_breakdown():
    """Old records with missing critique fields still validate and do not crash."""
    minimal_data = {
        "grounding": {"score": 80, "reason": "Grounding ok"},
        "reference_context": {"score": 75, "reason": "Ref ok"},
    }
    dto = ConfidenceBreakdownDto.model_validate(minimal_data)
    assert dto.grounding is not None
    assert dto.grounding.score == 80
    assert dto.review_status is None
    assert dto.critical_flags is None
    assert dto.critique_strengths is None
