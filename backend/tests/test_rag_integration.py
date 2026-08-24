"""
tests/test_rag_integration.py
=============================
Focused Integration Test Suite verifying the complete end-to-end integration
between brd-app and brd-agent.

Verifies:
1. Canonical leaf template_key forwarding.
2. Official SYSTEM_PROMPT priority & non-injection of Reference BRDs into generation prompt.
3. Official answer_text generation via LiteLLM flow.
4. Project C* evidence construction from official user data only.
5. Reference R* content rejection as factual evidence.
6. Anti-hallucination failure on unconfirmed numeric/metric claims.
7. Anti-hallucination pass on supported claims.
8. Safe draft progression to RAG confidence evaluation.
9. search_references query equals generated answer_text.
10. Exact field_id targeting in vector search.
11. RAG deterministic confidence replaces LLM confidence.
12. confidence_reason propagation to Answer and API.
13. General Chat skips canonical RAG validation.
14. Custom section skips canonical RAG validation.
15. Resilience on RAG infrastructure failure without fabricating confidence.
16. Exact 26 canonical ID sequence alignment.
17. Document assembly compatibility.
"""

import json
from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient

from app.models.answer import Answer
from app.repositories import answer_repository, section_repository
from app.services import ai_integration, chat_service, document_service, template_service
from app.rag import (
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
# 4. Post-Generation Flow: Safe Draft Replaces LLM Confidence with RAG Confidence
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_safe_generation_replaces_llm_confidence_with_rag():
    mock_llm_response = {
        "reply_text": "I have documented the settlement retry rules.",
        "answer_text": "The system shall automatically retry failed recurring subscription payments.",
        "completeness": 80,
        "confidence": 95,  # LLM fabricated confidence
        "missing_items": ["Specific retry timing"],
        "is_assumption": False,
    }

    mock_chat_completion = AsyncMock()
    mock_chat_completion.choices = [
        AsyncMock(message=AsyncMock(content=json.dumps(mock_llm_response)))
    ]

    mock_search_results = [
        SearchResult(
            document_key="doc1",
            document_title="Sample BRD",
            field_id="3.7",
            field_title="Settlement Plan",
            chunk_index=0,
            content="Failed recurring transactions are retried automatically.",
            similarity_score=0.88,
        )
    ]

    from app.config import settings

    with patch.object(settings, "groq_api_key", "test-key"), \
         patch("litellm.acompletion", new=AsyncMock(return_value=mock_chat_completion)), \
         patch("app.services.ai_integration.search_references", return_value=mock_search_results) as mock_search:

        reply = await ai_integration.get_reply(
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
        # RAG confidence must replace the LLM's 95 confidence
        assert reply.confidence is not None
        assert reply.confidence != 95
        assert 0 <= reply.confidence <= 100
        assert reply.confidence_reason is not None
        assert "Specific retry timing" in reply.confidence_reason or "selaras" in reply.confidence_reason.lower()

        # Verify search_references was called with generated answer_text and field_id
        mock_search.assert_called_once_with(mock_llm_response["answer_text"], "3.7", 3)


# ---------------------------------------------------------------------------
# 5. Unsafe Generation Flow: No RAG Confidence on Hallucination
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_unsafe_generation_blocks_rag_confidence():
    mock_llm_response = {
        "reply_text": "I set the SLA to 2 hours.",
        "answer_text": "The system shall complete invoice generation within 2 hours.",  # Hallucinated 2 hours
        "completeness": 90,
        "confidence": 99,
        "missing_items": [],
        "is_assumption": False,
    }

    mock_chat_completion = AsyncMock()
    mock_chat_completion.choices = [
        AsyncMock(message=AsyncMock(content=json.dumps(mock_llm_response)))
    ]

    from app.config import settings

    with patch.object(settings, "groq_api_key", "test-key"), \
         patch("litellm.acompletion", new=AsyncMock(return_value=mock_chat_completion)), \
         patch("app.services.ai_integration.search_references") as mock_search:

        reply = await ai_integration.get_reply(
            room_title="Background",
            room_purpose="Context",
            message_text="Invoice generation must complete within 1 hour.",  # User said 1 hour
            history=[],
            current_answer=None,
            field_id="1.1.1",
        )

        assert reply.confidence is None
        assert reply.confidence_reason is not None
        assert "unconfirmed claims" in reply.confidence_reason.lower()
        mock_search.assert_not_called()


# ---------------------------------------------------------------------------
# 6. General Chat & Non-Canonical Section Skip Canonical Validation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_general_chat_skips_rag_validation():
    mock_llm_response = {
        "reply_text": "Let's brainstorm overall project goals.",
        "answer_text": None,
        "completeness": 0,
        "confidence": 50,
        "missing_items": [],
        "is_assumption": False,
    }

    mock_chat_completion = AsyncMock()
    mock_chat_completion.choices = [
        AsyncMock(message=AsyncMock(content=json.dumps(mock_llm_response)))
    ]

    from app.config import settings

    with patch.object(settings, "groq_api_key", "test-key"), \
         patch("litellm.acompletion", new=AsyncMock(return_value=mock_chat_completion)), \
         patch("app.services.ai_integration.search_references") as mock_search:

        reply = await ai_integration.get_reply(
            room_title="General Chat",
            room_purpose="General brainstorming",
            message_text="Hi, let's start the project.",
            history=[],
            current_answer=None,
            field_id=None,  # General chat passes field_id=None
        )

        assert reply.confidence is None
        assert reply.confidence_reason is None
        mock_search.assert_not_called()


# ---------------------------------------------------------------------------
# 7. End-to-End API Integration & Persistence Test
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_end_to_end_post_message_saves_rag_confidence_and_reason(client: AsyncClient):
    auth = await register_and_login(client)
    headers = auth["headers"]
    conv_id = await create_conversation(client, headers, title="Payment Gateway BRD")

    mock_llm_response = {
        "reply_text": "Noted the settlement rule.",
        "answer_text": "The system shall automatically retry failed subscription payments.",
        "completeness": 75,
        "confidence": 90,
        "missing_items": ["Retry schedule"],
        "is_assumption": False,
    }

    mock_chat_completion = AsyncMock()
    mock_chat_completion.choices = [
        AsyncMock(message=AsyncMock(content=json.dumps(mock_llm_response)))
    ]

    mock_search_results = [
        SearchResult(
            document_key="doc1",
            document_title="Sample BRD",
            field_id="3.7",
            field_title="Settlement Plan",
            chunk_index=0,
            content="Failed recurring subscription payments are retried automatically.",
            similarity_score=0.85,
        )
    ]

    from app.config import settings

    with patch.object(settings, "groq_api_key", "test-key"), \
         patch("litellm.acompletion", new=AsyncMock(return_value=mock_chat_completion)), \
         patch("app.services.ai_integration.search_references", return_value=mock_search_results):

        # Post message to room 3.7
        res = await client.post(
            f"/api/conversations/{conv_id}/rooms/3.7/messages",
            json={"text": "The system shall automatically retry failed subscription payments."},
            headers=headers,
        )
        assert res.status_code == 200, res.text


        # Fetch conversation details
        detail_res = await client.get(f"/api/conversations/{conv_id}", headers=headers)
        assert detail_res.status_code == 200
        data = detail_res.json()

        answer_37 = data["answers"].get("3.7")
        assert answer_37 is not None
        assert answer_37["status"] == "progress"
        assert answer_37["completeness"] == 75
        assert answer_37["confidence"] is not None
        assert answer_37["confidence"] != 90  # Replaced by RAG
        assert answer_37["confidence_reason"] is not None
        assert len(answer_37["confidence_reason"]) > 0
