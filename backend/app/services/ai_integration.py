"""DUMMY AI — placeholder only, centralized on purpose.

Nothing in this file is real intelligence. It exists so `chat_service.py`
has something to call today, with a return shape rich enough that the
*rest* of the pipeline (Answer updates, status transitions, flagged
detection, the frontend's DonutBadge/missing-items/assumption-pill
rendering) can be built and verified for real right now, without waiting
on the AI team's integration. When that's ready, they replace this
file's internals (`get_reply`'s body — the deterministic placeholder
math below) with a real model call; the signature is the actual
contract other code is written against and is expected to stay stable
(or change deliberately, in coordination) — see
`../../../implementation_spin2.md` §1.2 for the fuller writeup of this
seam.

Search the codebase for "DUMMY_AI" to find every place this is used.
"""

import os
import json
import asyncio
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import litellm

try:
    import litellm.types.utils as _litellm_utils
    import litellm.types.llms.openai as _litellm_openai
    _litellm_utils.Message.model_rebuild(_types_namespace=vars(_litellm_openai))
except Exception:
    pass

from app.config import settings
<<<<<<< HEAD
from app.rag import (
    CANONICAL_ANSWERABLE_FIELDS,
    CANONICAL_FIELDS_META,
    ReferenceCitation,
    assess_confidence,
    extract_canonical_gaps,
    search_references,
    validate_project_facts,
)



=======
from app.services.brd_rules import get_section_rules_prompt
>>>>>>> origin/master

DUMMY_AI_REPLY = "Got it — logged. (Dummy AI: Please set GEMINI_API_KEY or GROQ_API_KEY in .env)"


# Hardcoded dummy breakdown — replaced by the AI team with real computed values.
_DUMMY_CONFIDENCE_BREAKDOWN = {
    "grounding": {"score": 72, "reason": "[Dummy] Most claims are grounded in provided user inputs, but some numerical targets lack cited sources."},
    "reference_context": {"score": 85, "reason": "[Dummy] The answer aligns well with prior sections. Minor terminology drift detected."},
    "section_compliance": {"score": 60, "reason": "[Dummy] Some required sub-fields per the section template are still missing or vague."},
    "testability": {"score": 50, "reason": "[Dummy] The stated requirements lack measurable acceptance criteria in several places."},
    "consistency": {"score": 90, "reason": "[Dummy] No logical contradictions detected across the current section content."},
}


@dataclass
class AgentReply:
    reply_text: str
    answer_text: str | None = None
    completeness: int | None = None
    confidence: int | None = None
    confidence_reason: str | None = None
    confidence_components: dict | None = None
    missing_items: list[str] = field(default_factory=list)
    is_assumption: bool = False
    # AI team: populate this with the 5-dimension breakdown dict.
    # Shape: {"grounding": {"score": int, "reason": str}, ...}
    # Leave None if not yet computed — the frontend hides the panel gracefully.
    confidence_breakdown: dict | None = None


class LLMReplySchema(BaseModel):
    reply_text: str = Field(..., description="The chat reply to the user")
    answer_text: str | None = Field(None, description="The updated formal draft text for this section")
    completeness: int = Field(..., description="Completeness score 0-100")
    confidence: int = Field(..., description="Confidence score 0-100")
    missing_items: list[str] = Field(default_factory=list, description="List of missing information")
    is_assumption: bool = Field(default=False, description="True if AI made assumptions")
    confidence_breakdown: dict | None = Field(
        None,
        description=(
            "Optional 5-dimension confidence breakdown. "
            "Keys: grounding, reference_context, section_compliance, testability, consistency. "
            "Each value: {score: int 0-100, reason: str}."
        ),
    )


SYSTEM_PROMPT = """You are an expert, senior Business Analyst acting as a BRD (Business Requirement Document) Consultant.
Your task is to guide the user to complete the current BRD section through a conversational interface, adhering to a very strict quality bar.

# PERSONA AND STRICT QUALITY BAR
- Never accept vague or unmeasurable language — "fast," "seamless," "robust," "user-friendly," "intuitive," "scalable," "modern," "efficient" — without turning it into a number or a concrete, testable definition.
- Never phrase a requirement as a goal or benefit ("improve customer satisfaction") instead of a behavior ("the system shall ...").
- Never state a risk as a vague worry ("we might lose customers") instead of a concrete consequence tied to a specific cause.
- Never describe reporting or monitoring by name only ("we'll monitor it") — always name what's measured, how often, and who receives it.
- Never present an assumption as settled fact. Every assumption must be flagged.
- If the user hasn't told you something and there's no way to reasonably infer it, ASK a clarifying question instead of inventing an answer.
- You are in GROUNDED mode: Never invent plausible-sounding statistics, datasets, or sources. If a number is needed, ask the user.

# SECTION-SPECIFIC RULES
{section_rules_prompt}

# CORE RULES FOR CONVERSATION
1. ONLY discuss topics related to the current BRD section (see context below). If the user attempts to discuss a different section, politely inform them that you are currently focusing on the current section and refuse to process the unrelated input. 
2. NEVER offer to transition to or discuss another section. You do not have the ability to change the active section. If the current section is complete, tell the user they must click on the next section in the sidebar menu to proceed.
3. If the user provides input for a different section, you MUST return the exact `current_answer_text` for answer_text, `current_completeness` for completeness, and `current_missing_items` for missing_items without any modifications. DO NOT reset or alter the completeness or answer text based on unrelated inputs.
4. Ask ONE specific, clear follow-up question at a time if information is incomplete or violates the quality bar above.
5. Extract any definitive answers from the user into formal, professional business language for the "answer_text". The "answer_text" represents the final draft for THIS section only.
6. Evaluate completeness ("completeness"):
   - 0-30: Vague or barely relevant information, or uses unmeasurable language. Ask follow up.
   - 40-70: Good start, but missing key details or concrete numbers. Document them in "missing_items".
   - 80-100: Comprehensive, testable, grounded, and actionable. Acknowledge and move on.
7. If you must make assumptions to format the text, set "is_assumption" to true. CRITICAL: Set "is_assumption" to FALSE if you are simply asking a clarifying question or asking for more information.
8. EXPLICIT CONTEXT CITATION: When you reject an input or ask for clarification based on a prerequisite dependency (listed in SECTION-SPECIFIC RULES), you MUST explicitly cite the name of that prerequisite section and explicitly quote or summarize its drafted text in your `reply_text`. For example: "Based on the draft of 1.2 Business Objective where you stated 'X', your current input contradicts this because..."

# CURRENT SECTION CONTEXT
- Section Title: {room_title}
- Section Purpose: {room_purpose}
- Current Draft Content: {current_answer_text}
- Current Completeness: {current_completeness}
- Missing Items (Previously): {current_missing_items}

# RECENT CHAT HISTORY
{history_context}

# OBJECTIVE
Respond with a JSON object matching the exact schema.
- 'reply_text': Your natural conversational response to the user.
- 'answer_text': The formal updated draft content for THIS section, incorporating all known info according to the strict quality bar.
- 'missing_items': A JSON array of strings detailing what is still needed. MUST be an array `[]` if empty.
- 'completeness': Integer 0-100.
- 'confidence': Integer 0-100.
- 'is_assumption': Boolean.

Example Output:
{{
  "reply_text": "To say we want to 'improve customer satisfaction' is too vague. What is the concrete, testable metric or behavior we are targeting?",
  "answer_text": "The system shall reduce cart abandonment rate by 15% in Q3.",
  "completeness": 50,
  "confidence": 90,
  "missing_items": ["Specific metric for customer satisfaction", "Target value"],
  "is_assumption": false
}}
"""


async def get_reply(
    *,
    room_id: str,
    room_title: str,
    room_purpose: str | None,
    message_text: str,
    history: list[dict],
    current_answer: dict | None,
<<<<<<< HEAD
    field_id: str | None = None,
=======
    context_answers: dict[str, str] | None = None,
>>>>>>> origin/master
) -> AgentReply:
    """Official AI Integration: LiteLLM generation followed by Anti-Hallucination & Post-Generation RAG Validation."""
    if not settings.groq_api_key and not settings.gemini_api_key:
        turns_so_far = len(history) // 2 + 1
        completeness = min(100, turns_so_far * 34)
        confidence = min(90, 55 + turns_so_far * 12)
        missing_items = [] if completeness >= 100 else ["More detail needed before this can be marked complete."]

        previous_answer_text = (current_answer or {}).get("answer_text") or ""
        answer_text = f"{previous_answer_text} {message_text}".strip()

        return AgentReply(
            reply_text=DUMMY_AI_REPLY,
            answer_text=answer_text,
            completeness=completeness,
            confidence=confidence,
            confidence_reason=None,
            confidence_components=None,
            missing_items=missing_items,
            is_assumption=False,
            confidence_breakdown=_DUMMY_CONFIDENCE_BREAKDOWN,
        )


    # Inject API Keys and RAG URL into environment
    if settings.groq_api_key:
        os.environ["GROQ_API_KEY"] = settings.groq_api_key
    if settings.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
    if settings.rag_database_url:
        os.environ["RAG_DATABASE_URL"] = settings.rag_database_url

    # Format history
    history_context = "\n".join([f"{b['role'].upper()}: {b['text']}" for b in history[-10:]])

    # Format current answer context
    current_answer_text = (current_answer or {}).get("answer_text") or "None"
    current_completeness = (current_answer or {}).get("completeness") or 0
    current_missing_items = json.dumps((current_answer or {}).get("missing_items") or [])

    system_instruction = SYSTEM_PROMPT.format(
        section_rules_prompt=get_section_rules_prompt(room_id, context_answers or {}),
        room_title=room_title,
        room_purpose=room_purpose or "Not specified",
        current_answer_text=current_answer_text,
        current_completeness=current_completeness,
        current_missing_items=current_missing_items,
        history_context=history_context,
    )

    try:
        # STEP 1 & 2: Official SYSTEM_PROMPT Generation via LiteLLM
        chat_completion = await litellm.acompletion(
            model="groq/llama-3.3-70b-versatile",
            fallbacks=[
                "gemini/gemini-3.1-flash-lite",
                "gemini/gemini-flash-latest",
            ],
            messages=[
                {
                    "role": "system",
                    "content": system_instruction,
                },
                {
                    "role": "user",
                    "content": message_text,
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        response_text = chat_completion.choices[0].message.content

        # Sanitize empty arrays if any
        raw_data = json.loads(response_text)
        if "missing_items" in raw_data and isinstance(raw_data["missing_items"], dict):
            if not raw_data["missing_items"]:
                raw_data["missing_items"] = []
            else:
                raw_data["missing_items"] = [raw_data["missing_items"]]

        llm_reply = LLMReplySchema.model_validate(raw_data)

        generated_answer = llm_reply.answer_text
        final_confidence: int | None = None
        confidence_reason: str | None = None
        confidence_components: dict | None = None

        # STEP 3 & 4: Post-Generation Validation (ONLY for canonical leaf fields with generated answer)
        if (
            field_id
            and field_id in CANONICAL_ANSWERABLE_FIELDS
            and generated_answer
            and generated_answer.strip()
        ):
            # 1. Build Project C* Evidence strictly from official user/project sources
            user_evidence_parts: list[str] = []
            if current_answer and current_answer.get("answer_text"):
                user_evidence_parts.append(current_answer["answer_text"])
            user_evidence_parts.append(message_text)
            for h in history:
                if h.get("role") == "user" and h.get("text"):
                    user_evidence_parts.append(h["text"])

            project_evidence_text = "\n".join(user_evidence_parts)

            # 2. Anti-Hallucination Fact Validation
            val_result = validate_project_facts(generated_answer, project_evidence_text)

            if not val_result.is_safe:
                # UNSAFE: Do not calculate RAG confidence; require clarification
                final_confidence = None
                claims_str = ", ".join(val_result.unsupported_claims)
                confidence_reason = (
                    f"Draft contains unconfirmed claims: {claims_str}. Clarification required from user."
                )
                print(f"[ANTI-HALLUCINATION] Flagged unsafe claims in field {field_id}: {val_result.unsupported_claims}")
            else:
                # SAFE: Proceed to Post-Generation RAG Validation
                try:
                    # Retrieve Top-3 Reference BRDs using generated answer as query
                    raw_results = await asyncio.to_thread(search_references, generated_answer, field_id, 3)
                    retrieved_refs = [
                        ReferenceCitation.from_search_result(f"R{i}", r)
                        for i, r in enumerate(raw_results, start=1)
                    ]

                    canonical_info_needed = CANONICAL_FIELDS_META[field_id]["information_needed"]
                    canonical_gaps = extract_canonical_gaps(canonical_info_needed)

                    # Assess deterministic confidence (50% Ref Sim + 30% Field Align + 20% Canonical Coverage)
                    assessment = assess_confidence(
                        field_id=field_id,
                        generated_content=generated_answer,
                        retrieved_references=retrieved_refs,
                        total_canonical_gaps=len(canonical_gaps),
                        unresolved_gap_descriptions=llm_reply.missing_items or [],
                        embedder=None,
                        llm_client=None,
                    )

                    # Replace LLM confidence with deterministic RAG confidence
                    final_confidence = assessment.confidence_percentage
                    confidence_reason = assessment.reason
                    confidence_components = assessment.components.to_dict()
                    print(f"[RAG CONFIDENCE] Evaluated field {field_id}: {final_confidence}% ({assessment.confidence_level})")
                except Exception as rag_exc:
                    print(f"[RAG ERROR] Failed to evaluate RAG confidence for field {field_id}: {rag_exc}")
                    final_confidence = None
                    confidence_reason = "RAG reference validation temporarily unavailable."

        return AgentReply(
            reply_text=llm_reply.reply_text,
            answer_text=llm_reply.answer_text,
            completeness=llm_reply.completeness,
            confidence=final_confidence,
            confidence_reason=confidence_reason,
            confidence_components=confidence_components,
            missing_items=llm_reply.missing_items,
            is_assumption=llm_reply.is_assumption,
            # AI team: llm_reply.confidence_breakdown is None until the model
            # returns it. Fallback to dummy so the UI is always exercisable.
            confidence_breakdown=llm_reply.confidence_breakdown or _DUMMY_CONFIDENCE_BREAKDOWN,
        )

    except Exception as e:
        print(f"AI Generation Error: {e}")
        return AgentReply(
            reply_text="I'm sorry, I encountered an internal error while processing that.",
            answer_text=current_answer_text,
            completeness=current_completeness,
            confidence=None,
            confidence_reason=None,
            confidence_components=None,
            missing_items=(current_answer or {}).get("missing_items") or [],
            confidence_breakdown=_DUMMY_CONFIDENCE_BREAKDOWN,
        )




