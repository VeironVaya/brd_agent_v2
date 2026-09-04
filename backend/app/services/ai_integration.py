"""LiteLLM integration — wraps the real LLM call behind a strict prompt.

Follows the design in brainstorming/erd.md:
- Reads system prompt and per-section context
- Talks to Groq (llama-3.3-70b-versatile) / Gemini via LiteLLM
- Expects JSON output conforming to LLMReplySchema
- Translates the LLM response into an AgentReply dataclass
- Falls back to a deterministic dummy reply when no API keys are configured
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
import litellm
from pydantic import BaseModel, Field

try:
    import litellm.types.utils as _litellm_utils
    import litellm.types.llms.openai as _litellm_openai
    _litellm_utils.Message.model_rebuild(_types_namespace=vars(_litellm_openai))
except Exception:
    pass

from app.config import settings
from app.services.brd_rules import get_section_rules_prompt

DUMMY_AI_REPLY = "Got it — logged. (Dummy AI: Please set GEMINI_API_KEY or GROQ_API_KEY in .env)"


@dataclass
class AgentReply:
    reply_text: str
    answer_text: str | None = None
    completeness: int | None = None
    confidence: int | None = None
    confidence_reason: str | None = None
    confidence_components: dict | None = None
    missing_items: list[str] = field(default_factory=list)
    confidence_breakdown: dict | None = None


class LLMReplySchema(BaseModel):
    reply_text: str = Field(..., description="The chat reply to the user")
    answer_text: str | None = Field(None, description="The updated formal draft text for this section")
    completeness: int = Field(..., description="Completeness score 0-100")
    confidence: int | None = Field(None, description="Confidence score 0-100")
    missing_items: list[str] = Field(default_factory=list, description="List of missing information")
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
- CRITICAL: THIS IS AN IT/SOFTWARE DOCUMENT. DO NOT CONFUSE SYSTEM RETIREMENT WITH PERSONAL FINANCIAL RETIREMENT. Always assume contexts relate to IT infrastructure, software lifecycles, and business processes.
- Never accept vague or unmeasurable language — "fast," "seamless," "robust," "user-friendly," "intuitive," "scalable," "modern," "efficient" — without turning it into a number or a concrete, testable definition.
- Never phrase a requirement as a goal or benefit ("improve customer satisfaction") instead of a behavior ("the system shall ...").
- Never state a risk as a vague worry ("we might lose customers") instead of a concrete consequence tied to a specific cause.
- Never describe reporting or monitoring by name only ("we'll monitor it") — always name what's measured, how often, and who receives it.
- Never present an assumption as settled fact. Every assumption must be flagged.
- If the user hasn't told you something and there's no way to reasonably infer it, ASK a clarifying question instead of inventing an answer.
- You are in GROUNDED mode: Never invent plausible-sounding statistics, datasets, or sources. If a number is needed, ask the user.

# PROJECT CONTEXT
{project_evidence}
- IMPORTANT: If any information in the PROJECT CONTEXT (such as Impacted Stakeholders or Requestor Directorate) is relevant to the current section's requirements, you MUST proactively incorporate it into your generated `answer_text`.
- DO NOT ask the user to provide information that is already present in the PROJECT CONTEXT.

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
   - CRITICAL: If you determine that the section is fully complete and "missing_items" is empty, you MUST set "completeness" to exactly 100. Do not use 95 or 99.
7. DEFER TO QUALITY REVIEWER: Even if you set completeness to 100, DO NOT tell the user they are done or that they can proceed to the next section. Your work is subject to review by the Quality Gatekeeper (Agent 2), who may find issues you missed. Instead, say something like: 'I've incorporated your details into the draft. Please check the right panel to see if the Quality Reviewer has flagged any final issues before we move on.'
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

Example Output:
{{
  "reply_text": "To say we want to 'improve customer satisfaction' is too vague. What is the concrete, testable metric or behavior we are targeting?",
  "answer_text": "The system shall reduce cart abandonment rate by 15% in Q3.",
  "completeness": 50,
  "confidence": 90,
  "missing_items": ["Specific metric for customer satisfaction", "Target value"]
}}
"""


CHOICE_SECTION_PROMPT = """You are an expert, senior Business Analyst acting as a BRD (Business Requirement Document) Consultant.
Your task is to guide the user through a conversational interface.

# CURRENT SECTION CONTEXT
- Section Title: {room_title}
- Section Purpose: {room_purpose}

# RECENT CHAT HISTORY
{history_context}

# OBJECTIVE
This is a structured Choice Section (List of Values). 
DO NOT draft any answer text. DO NOT evaluate completeness. DO NOT flag missing items.
Your only job is to chat with the user, answer their questions, and help them brainstorm which options they should select. 
Remind them that to officially answer this section, they MUST click the "Choose options" button in the user interface.

Respond with a JSON object matching this exact schema:
{{
  "reply_text": "Your natural conversational response helping them brainstorm.",
  "answer_text": null,
  "completeness": 0,
  "confidence": null,
  "missing_items": []
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
    field_id: str | None = None,
    context_answers: dict[str, str] | None = None,
    judge_critique: dict | None = None,
    project_evidence: str | None = None,
    is_choice_section: bool = False,
) -> AgentReply:
    """Real AI Integration: LiteLLM routing processing room data and outputting AgentReply."""
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
            missing_items=missing_items,
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

    if is_choice_section:
        system_instruction = CHOICE_SECTION_PROMPT.format(
            room_title=room_title,
            room_purpose=room_purpose or "Not specified",
            history_context=history_context,
        )
    else:
        system_instruction = SYSTEM_PROMPT.format(
        project_evidence=project_evidence or "Not provided",
        section_rules_prompt=get_section_rules_prompt(room_id, context_answers or {}),
        room_title=room_title,
        room_purpose=room_purpose or "Not specified",
        current_answer_text=current_answer_text,
        current_completeness=current_completeness,
        current_missing_items=current_missing_items,
        history_context=history_context,
    )

    if judge_critique:
        system_instruction += "\n\n# EVALUATOR FEEDBACK (REFLECTION MODE)\n"
        system_instruction += "The Senior Reviewer reviewed your draft and found issues. You MUST fix your `answer_text`, ask clarifying questions to the user in `reply_text`, and update `missing_items` based on this feedback:\n"
        system_instruction += f"- Evaluator Confidence Score: {judge_critique.get('final_confidence', 0)}/100\n"
        system_instruction += f"- Evaluator Reason: {judge_critique.get('confidence_reason', '')}\n"
        
        breakdown = judge_critique.get('confidence_breakdown')
        if breakdown:
            system_instruction += "- Detailed Breakdown:\n"
            for k, v in breakdown.items():
                if isinstance(v, dict):
                    system_instruction += f"  * {k.replace('_', ' ').title()} ({v.get('score', 0)}/100): {v.get('reason', '')}\n"


    try:
        chat_completion = await litellm.acompletion(
            model="gemini/gemini-3.1-flash-lite",
            fallbacks=[
                "gemini/gemini-3.5-flash-lite",
                "gemini/gemini-3.5-flash",
                "gemini/gemini-3.6-flash",
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
        
        # For checking which agent is generated the message
        print(f"[LLM ROUTER] Response generated by: {chat_completion.model}")
        
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
            answer_text=current_answer_text if is_choice_section else llm_reply.answer_text,
            completeness=current_completeness if is_choice_section else llm_reply.completeness,
            confidence=None,
            missing_items=json.loads(current_missing_items) if is_choice_section else llm_reply.missing_items,
            confidence_breakdown=None,
        )
        
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return AgentReply(
            reply_text="I'm sorry, I encountered an internal error while processing that.",
            answer_text=current_answer_text,
            completeness=current_completeness,
            confidence=None,
            missing_items=(current_answer or {}).get("missing_items") or [],
            confidence_breakdown=None,
        )

GREETING_PROMPT = """
You are an AI assisting with a Business Requirement Document (BRD).
CRITICAL: THIS IS AN IT/SOFTWARE DOCUMENT. DO NOT CONFUSE SYSTEM RETIREMENT WITH PERSONAL FINANCIAL RETIREMENT. Always assume contexts relate to IT infrastructure, software lifecycles, and business processes.
The user has just opened the section: "{room_title}".
{section_rules_prompt}

Your task is to warmly welcome the user to this section and ask the first relevant question to get them started.
If there is context from previous sections, explicitly mention it in your greeting to show you remember.
For example: "Welcome to {room_title}! Based on your previous answer in [Section Name] where you mentioned [Detail], could you tell me..."

# OBJECTIVE
Respond with a JSON object matching this schema:
- 'reply_text': Your welcoming message and opening question.
- 'answer_text': ""
- 'missing_items': [List of strings detailing what specific information or data is required to fulfill this section based on the rules. Since the section is empty, this must list the core requirements.]
- 'completeness': 0
- 'confidence': 100
"""

async def get_greeting(
    *,
    room_id: str,
    room_title: str,
    context_answers: dict[str, str] | None = None,
) -> AgentReply:
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
            model="gemini/gemini-3.1-flash-lite",
            fallbacks=["gemini/gemini-3.5-flash-lite", "gemini/gemini-3.5-flash", "gemini/gemini-3.6-flash"],
            messages=[
                {
                    "role": "system",
                    "content": system_instruction,
                },
                {
                    "role": "user",
                    "content": "Generate the initial greeting.",
                }
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
            confidence_breakdown=None,
        )
        
    except Exception as e:
        print(f"AI Greeting Error: {e}")
        return AgentReply(
            reply_text=f"Welcome to {room_title}. Let's get started. What information do you have for this section?",
            answer_text="",
            completeness=0,
            confidence=None,
            missing_items=[],
            confidence_breakdown=None,
        )


