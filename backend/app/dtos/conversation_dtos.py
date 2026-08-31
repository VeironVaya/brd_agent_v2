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
    group_id: str | None = None


class ConversationListResponse(BaseModel):
    conversations: list[ConversationListItem]


class CreateConversationRequest(BaseModel):
    title: str
    context: str | None = None
    requestor_directorate: str | None = None
    impacted_stakeholders: list[str] = []
    group_id: str | None = None


class CreateConversationResponse(BaseModel):
    id: str


class RenameConversationRequest(BaseModel):
    title: str


class RenameConversationResponse(BaseModel):
    id: str
    title: str


class ConfidenceDimensionDto(BaseModel):
    score: int | None = None
    reason: str | None = None


class CriticalFlagDto(BaseModel):
    type: str
    reason: str
    excerpt: str | None = None


class ConfidenceBreakdownDto(BaseModel):
    final_confidence: int | None = None
    confidence_level: str | None = None
    grounding: ConfidenceDimensionDto | None = None
    reference_context: ConfidenceDimensionDto | None = None
    section_compliance: ConfidenceDimensionDto | None = None
    testability: ConfidenceDimensionDto | None = None
    consistency: ConfidenceDimensionDto | None = None
    review_status: str | None = None
    dependency_status: str | None = None
    critical_flags: list[CriticalFlagDto] | None = None
    critique_strengths: list[str] | None = None
    critique_issues: list[str] | None = None
    critique_suggestions: list[str] | None = None
    critique_summary: str | None = None
    judge_model: str | None = None
    evaluated_at: str | None = None


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
    confidence_breakdown: ConfidenceBreakdownDto | None = None



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
