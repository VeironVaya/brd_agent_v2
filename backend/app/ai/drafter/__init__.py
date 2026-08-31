"""Agent 1 — Conversational BRD Drafter Subsystem."""

from app.ai.drafter.prompt import SYSTEM_PROMPT
from app.ai.drafter.prompt import GREETING_PROMPT, SYSTEM_PROMPT
from app.ai.drafter.schema import AgentReply, DUMMY_AI_REPLY, LLMReplySchema
from app.ai.drafter.service import get_reply
from app.ai.drafter.service import get_greeting, get_reply

__all__ = [
    "AgentReply",
    "DUMMY_AI_REPLY",
    "GREETING_PROMPT",
    "LLMReplySchema",
    "SYSTEM_PROMPT",
    "get_greeting",
    "get_reply",
]


