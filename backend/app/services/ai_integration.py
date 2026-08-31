"""Backward-compatibility re-export for app.ai.drafter.

Agent 1 (Drafter) now lives in `app.ai.drafter`.
This module is retained strictly for backward compatibility with existing tests and callers.
"""

from app.ai.drafter import (
    AgentReply,
    DUMMY_AI_REPLY,
    GREETING_PROMPT,
    LLMReplySchema,
    SYSTEM_PROMPT,
    get_greeting,
    get_reply,
)
from app.rag import search_references

__all__ = [
    "AgentReply",
    "DUMMY_AI_REPLY",
    "GREETING_PROMPT",
    "LLMReplySchema",
    "SYSTEM_PROMPT",
    "get_greeting",
    "get_reply",
    "search_references",
]

