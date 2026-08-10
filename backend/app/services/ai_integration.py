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

import json
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from groq import AsyncGroq

from app.config import settings


@dataclass
class AgentReply:
    reply_text: str
    answer_text: str | None = None
    completeness: int | None = None
    confidence: int | None = None
    missing_items: list[str] = field(default_factory=list)
    is_assumption: bool = False


class LLMReplySchema(BaseModel):
    reply_text: str = Field(..., description="The chat reply to the user")
    answer_text: str | None = Field(None, description="The updated formal draft text for this section")
    completeness: int = Field(..., description="Completeness score 0-100")
    confidence: int = Field(..., description="Confidence score 0-100")
    missing_items: list[str] = Field(default_factory=list, description="List of missing information")
    is_assumption: bool = Field(default=False, description="True if AI made assumptions")


SYSTEM_PROMPT = """You are an expert Business Analyst acting as a BRD (Business Requirement Document) Consultant.
Your task is to guide the user to complete the current BRD section through a conversational interface.

# CORE RULES
1. ONLY discuss topics related to the current BRD section.
2. Ask ONE specific, clear follow-up question at a time if information is incomplete.
3. Extract any definitive answers from the user into formal, professional business language for the "answer_text".
4. Evaluate completeness ("completeness"):
   - 0-30: Vague or barely relevant information. Ask follow up.
   - 40-70: Good start, but missing key details. Document them in "missing_items".
   - 80-100: Comprehensive and actionable. Acknowledge and move on.

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
- 'answer_text': The formal updated draft content for this section, incorporating all known info.
- 'missing_items': A JSON array of strings detailing what is still needed. MUST be an array `[]` if empty.
- 'completeness': Integer 0-100.
- 'confidence': Integer 0-100.
- 'is_assumption': Boolean.

Example Output:
{{
  "reply_text": "Got it. Who is the primary target audience for this feature?",
  "answer_text": "The main business goal is to increase user retention by 20% in Q3.",
  "completeness": 50,
  "confidence": 90,
  "missing_items": ["Primary target audience", "Success metrics for Q4"],
  "is_assumption": false
}}
"""


async def get_reply(
    *,
    room_title: str,
    room_purpose: str | None,
    message_text: str,
    history: list[dict],
    current_answer: dict | None,
) -> AgentReply:
    """Real AI Integration: Groq LLM processing room data and outputting AgentReply."""
    if not settings.groq_api_key:
        return AgentReply(
            reply_text="Got it — logged. (Dummy AI: Please set GROQ_API_KEY in .env)",
            answer_text=(current_answer or {}).get("answer_text") or f"{message_text}",
            completeness=50,
            confidence=90,
            missing_items=["Missing API Key"],
            is_assumption=False,
        )

    # Format history
    history_context = "\n".join([f"{b['role'].upper()}: {b['text']}" for b in history[-10:]])

    # Format current answer context
    current_answer_text = (current_answer or {}).get("answer_text") or "None"
    current_completeness = (current_answer or {}).get("completeness") or 0
    current_missing_items = ", ".join((current_answer or {}).get("missing_items") or []) or "None"

    system_instruction = SYSTEM_PROMPT.format(
        room_title=room_title,
        room_purpose=room_purpose or "Not specified",
        current_answer_text=current_answer_text,
        current_completeness=current_completeness,
        current_missing_items=current_missing_items,
        history_context=history_context,
    )

    client = AsyncGroq(api_key=settings.groq_api_key)
    
    try:
        chat_completion = await client.chat.completions.create(
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
            model="llama-3.3-70b-versatile",
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
        
        return AgentReply(
            reply_text=llm_reply.reply_text,
            answer_text=llm_reply.answer_text,
            completeness=llm_reply.completeness,
            confidence=llm_reply.confidence,
            missing_items=llm_reply.missing_items,
            is_assumption=llm_reply.is_assumption,
        )
        
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return AgentReply(
            reply_text="I'm sorry, I encountered an internal error while processing that.",
            answer_text=current_answer_text,
            completeness=current_completeness,
            missing_items=(current_answer or {}).get("missing_items") or [],
        )
