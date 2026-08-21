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
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import litellm

from app.config import settings

DUMMY_AI_REPLY = "Got it — logged. (Dummy AI: Please set GEMINI_API_KEY or GROQ_API_KEY in .env)"


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
Depending on the "Section Title" (see context below), you MUST enforce the following specific rules for that section when generating "answer_text" and asking follow-ups:

**1. Introduction**
- **1.1.1 Background**: Must state the actual trigger (the event, problem, or decision behind it), not a restated objective.
- **1.1.2 Business and Market Analysis**: Must cite something concrete (a named benchmark, a competitor behavior), not a general claim of importance.
- **1.1.3 Relevant Historical Data**: Must reference specific data, incidents, or metrics grounding the need. If none exist, say so explicitly and flag it as an assumption.
- **1.2 Business Objective**: The underlying business problem and why it matters now. Not a feature name — the actual goal.
- **1.3 Purpose of this Business Requirement**: What this specific document is meant to achieve or authorize.
- **1.4 Program Type**: A specific category: new product/service, enhancement, regulatory compliance, migration, retirement, etc. Not "a project."
- **1.5 Business Risk**: Concrete risks of doing this *and* of not doing it. Each risk names a specific cause and consequence.

**2. Benefit Analysis**
- **2.1 Summary**: What improves, for whom, and by how much. A real figure is required. Never state units with no number and no explanation of why. If pending, state "pending baseline confirmation".
- **2.2 Assumption and Calculation**: The numbers and assumptions behind any benefit claim, with every assumption used in the calculation stated explicitly, not implied.

**3. Service Description**
- **3.1 General Requirement**: A numbered list. Each item is a concrete, testable "the system shall ..." behavior.
- **3.2 Product / Service Specification**: The actual specification of what's being built or changed, not a summary of the objective.
- **3.3.1 Business process impact**: What existing processes change, and how.
- **3.3.2 Description**: Description of the new or changed process itself.
- **3.3.3 Security**: Concrete controls/requirements, not "it will be secure."
- **3.3.4 Organization and policy**: The specific org/policy implication: who owns what, what changes.
- **3.3.5 Service Delivery Plan**: How the service is delivered operationally (Write "Not applicable" if not a new application).
- **3.4 Complain Handling**: The specific mechanism for handling related customer complaints.
- **3.5 Reporting**: What gets reported, to whom, and how often. Name mechanism, audience, and frequency — all three.
- **3.6 Monitoring**: What gets monitored, how, and who is alerted (Write "Not applicable" if not required).
- **3.7 Settlement Plan**: (Write "Not applicable" if no financial settlement is involved).
- **3.8 Assumptions and Dependencies**: Every value elsewhere in the document that wasn't explicitly confirmed goes here in plain language, along with other systems, teams, contracts, or approvals this relies on. Dependencies must be named specifically.

**4. Release Plan**
- **4.1 Target Ready for Service**: A concrete date or milestone, or an explicit reason it's still pending (e.g. "pending sprint planning") — never "soon" or "TBD" with no reason.
- **4.2 Commercial Launch**: Commercial launch plan and timing, same standard as 4.1.
- **4.3 Internal Socialization Plan**: How internal teams are informed/trained ahead of launch (or "Not applicable").
- **4.4 Rollout Scenario**: Phased, pilot, big-bang, or other rollout approach (or "Not applicable").

**5. Product/Service Retirement Plan**
- What happens to this product/service at end of life, or an explicit note that no retirement plan applies yet.

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
    room_title: str,
    room_purpose: str | None,
    message_text: str,
    history: list[dict],
    current_answer: dict | None,
) -> AgentReply:
    """Real AI Integration: LiteLLM routing processing room data and outputting AgentReply."""
    # if not settings.gemini_api_key and not settings.groq_api_key:
    #     return AgentReply(
    #         reply_text=DUMMY_AI_REPLY,

    # ini kalo groq dulu baru gemini        
    if not settings.groq_api_key and not settings.gemini_api_key:
        return AgentReply(
            reply_text="Got it — logged. (Dummy AI: Please set GROQ_API_KEY or GEMINI_API_KEY in .env)",
            answer_text=(current_answer or {}).get("answer_text") or f"{message_text}",
            completeness=50,
            confidence=90,
            missing_items=["Missing API Key"],
            is_assumption=False,
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
        room_title=room_title,
        room_purpose=room_purpose or "Not specified",
        current_answer_text=current_answer_text,
        current_completeness=current_completeness,
        current_missing_items=current_missing_items,
        history_context=history_context,
    )

    try:
        chat_completion = await litellm.acompletion(
            # model="gemini/gemini-1.5-flash",
            # fallbacks=["gemini/gemini-flash-latest"],

            # ini kalo gemini dulu baru groq
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
