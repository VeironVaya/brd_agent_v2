from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ConversationListItem(BaseModel):
    id: str
    title: str
    updated_at: datetime
    answered_count: int


class ConversationListResponse(BaseModel):
    conversations: list[ConversationListItem]


class CreateConversationRequest(BaseModel):
    title: str
    context: str | None = None


class CreateConversationResponse(BaseModel):
    id: str


class RenameConversationRequest(BaseModel):
    title: str


class RenameConversationResponse(BaseModel):
    id: str
    title: str


class AnswerDto(BaseModel):
    status: str
    completeness: int | None = None
    confidence: int | None = None
    answer: str | None = None
    missing: list[str] = []
    flagged: bool | None = None


class CustomSectionNodeDto(BaseModel):
    id: str
    title: str
    purpose: str | None = None
    has_children: bool
    nest_under: str | None = None
    children: list[CustomSectionNodeDto] = []


class FlaggedItemDto(BaseModel):
    field_id: str
    label: str
    depends_on_label: str
    reason: str


class MessageDto(BaseModel):
    id: str
    role: str
    text: str


class ConversationDetailResponse(BaseModel):
    id: str
    title: str
    updated_at: datetime
    last_generated_at: datetime | None = None
    last_generated_version: str | None = None
    answered_count: int
    focused_field_id: str | None = None
    answers: dict[str, AnswerDto]
    custom_sections: list[CustomSectionNodeDto]
    flagged_items: list[FlaggedItemDto]
    messages: dict[str, list[MessageDto]]


CustomSectionNodeDto.model_rebuild()
