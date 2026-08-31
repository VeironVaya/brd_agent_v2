"""Agent 1 — Conversational BRD Drafter / Elicitor Service.

Agent 1 is solely responsible for generating and revising BRD section drafts
and chat replies based on the official SYSTEM_PROMPT.

Agent 1 DOES NOT evaluate or calculate production confidence. All confidence
scoring, grading, and critique are the exclusive responsibility of Agent 2
(Senior Business Analyst Reviewer / Judge in `app.ai.judge`).
"""

from __future__ import annotations

import json
import os
import litellm

try:
    import litellm.types.utils as _litellm_utils
    import litellm.types.llms.openai as _litellm_openai
    _litellm_utils.Message.model_rebuild(_types_namespace=vars(_litellm_openai))
except Exception:
    pass

from app.core.config import settings
from app.services.brd_rules import get_section_rules_prompt
from app.ai.drafter.prompt import SYSTEM_PROMPT
from app.ai.drafter.prompt import GREETING_PROMPT, SYSTEM_PROMPT
from app.ai.drafter.schema import AgentReply, DUMMY_AI_REPLY, LLMReplySchema


async def get_reply(
    *,
    room_id: str,
    room_title: str,
    room_purpose: str | None,
    message_text: str,
    history: list[dict],
    current_answer: dict | None,
    field_id: str | None = None,
    context_answers: dict[str, str] | None = None,
) -> AgentReply:
    """Agent 1 Generation: LiteLLM generation strictly following the official SYSTEM_PROMPT.

    Does NOT calculate confidence. Production confidence is calculated
    exclusively by Agent 2 (app.ai.judge).
    """
    if not settings.groq_api_key and not settings.gemini_api_key:
        turns_so_far = len(history) // 2 + 1
        completeness = min(100, turns_so_far * 34)
        missing_items = [] if completeness >= 100 else ["More detail needed before this can be marked complete."]

        previous_answer_text = (current_answer or {}).get("answer_text") or ""
        answer_text = f"{previous_answer_text} {message_text}".strip()

        return AgentReply(
            reply_text=DUMMY_AI_REPLY,
            answer_text=answer_text,
            completeness=completeness,
            confidence=None,
            confidence_reason=None,
            confidence_components=None,
            missing_items=missing_items,
            is_assumption=False,
            confidence_breakdown=None,
        )

    # Inject API Keys into environment for LiteLLM
    if settings.groq_api_key:
        os.environ["GROQ_API_KEY"] = settings.groq_api_key
    if settings.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = settings.gemini_api_key

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
        chat_completion = await litellm.acompletion(
            model="groq/llama-3.3-70b-versatile",
            fallbacks=[
                "gemini/gemini-2.0-flash",
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

        # Agent 1 returns generation results only.
        # Confidence fields are None here because Agent 2 is the single source of truth.
        return AgentReply(
            reply_text=llm_reply.reply_text,
            answer_text=llm_reply.answer_text,
            completeness=llm_reply.completeness,
            confidence=None,
            confidence_reason=None,
            confidence_components=None,
            missing_items=llm_reply.missing_items,
            is_assumption=llm_reply.is_assumption,
            confidence_breakdown=None,
        )

    except Exception as e:
        print(f"[AGENT 1 GENERATION ERROR]: {e}")
        return AgentReply(
            reply_text="I'm sorry, I encountered an internal error while processing that.",
            answer_text=current_answer_text,
            completeness=current_completeness,
            confidence=None,
            confidence_reason=None,
            confidence_components=None,
            missing_items=(current_answer or {}).get("missing_items") or [],
            confidence_breakdown=None,
        )


async def get_greeting(
    *,
    room_id: str,
    room_title: str,
    context_answers: dict[str, str] | None = None,
) -> AgentReply:
    """Agent 1 Greeting: Generates warm initial greeting and opening question for empty room."""
    if not settings.groq_api_key and not settings.gemini_api_key:
        return AgentReply(
            reply_text=f"Welcome to {room_title}. Let's get started. What information do you have for this section?",
            answer_text="",
            completeness=0,
            confidence=None,
            missing_items=[],
            is_assumption=False,
            confidence_breakdown=None,
        )

    # Inject API Keys into environment for LiteLLM
    if settings.groq_api_key:
        os.environ["GROQ_API_KEY"] = settings.groq_api_key
    if settings.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = settings.gemini_api_key

    system_instruction = GREETING_PROMPT.format(
        section_rules_prompt=get_section_rules_prompt(room_id, context_answers or {}),
        room_title=room_title,
    )

    try:
        chat_completion = await litellm.acompletion(
            model="groq/llama-3.3-70b-versatile",
            fallbacks=["gemini/gemini-2.0-flash", "gemini/gemini-flash-latest"],
            messages=[
                {
                    "role": "system",
                    "content": system_instruction,
                },
                {
                    "role": "user",
                    "content": "Generate the initial greeting.",
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        response_text = chat_completion.choices[0].message.content
        raw_data = json.loads(response_text)
        if "missing_items" in raw_data and isinstance(raw_data["missing_items"], dict):
            raw_data["missing_items"] = []

        llm_reply = LLMReplySchema.model_validate(raw_data)

        return AgentReply(
            reply_text=llm_reply.reply_text,
            answer_text="",
            completeness=0,
            confidence=None,
            missing_items=llm_reply.missing_items,
            is_assumption=False,
            confidence_breakdown=None,
        )

    except Exception as e:
        print(f"[AGENT 1 GREETING ERROR]: {e}")
        return AgentReply(
            reply_text=f"Welcome to {room_title}. Let's get started. What information do you have for this section?",
            answer_text="",
            completeness=0,
            confidence=None,
            missing_items=[],
            is_assumption=False,
            confidence_breakdown=None,
        )


