from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ConversationListItem(BaseModel):
    id: str
    title: str
    updated_at: datetime
    answered_count: int
    role: str
    owner_name: str | None = None
    owner_email: str | None = None


class ConversationListResponse(BaseModel):
    conversations: list[ConversationListItem]


class CreateConversationRequest(BaseModel):
    title: str
    context: str | None = None
    requestor_directorate: str | None = None
    impacted_stakeholders: list[str] = []


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
    confidence_reason: str | None = None
    confidence_components: dict | None = None
    answer: str | None = None
    missing: list[str] = []
    flagged: bool | None = None
    choice_data: dict | None = None



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
    requestor_directorate: str | None = None
    impacted_stakeholders: list[str] = []
    updated_at: datetime
    last_generated_at: datetime | None = None
    last_generated_version: str | None = None
    answered_count: int
    focused_field_id: str | None = None
    role: str
    answers: dict[str, AnswerDto]
    custom_sections: list[CustomSectionNodeDto]
    flagged_items: list[FlaggedItemDto]
    messages: dict[str, list[MessageDto]]


CustomSectionNodeDto.model_rebuild()
