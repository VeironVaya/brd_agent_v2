"""Agent 1 — Drafter Data Contracts & Schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from pydantic import BaseModel, Field

DUMMY_AI_REPLY = "Got it — logged. (Dummy AI: Please set GEMINI_API_KEY or GROQ_API_KEY in .env)"


@dataclass
class AgentReply:
    reply_text: str
    answer_text: str | None = None
    completeness: int | None = None
    confidence: int | None = None  # None: Agent 2 is single source of truth
    confidence_reason: str | None = None
    confidence_components: dict | None = None
    missing_items: list[str] = field(default_factory=list)
    is_assumption: bool = False
    confidence_breakdown: dict | None = None


class LLMReplySchema(BaseModel):
    reply_text: str = Field(..., description="The chat reply to the user")
    answer_text: str | None = Field(None, description="The updated formal draft text for this section")
    completeness: int = Field(..., description="Completeness score 0-100")
    missing_items: list[str] = Field(default_factory=list, description="List of missing information")
    is_assumption: bool = Field(default=False, description="True if AI made assumptions")

