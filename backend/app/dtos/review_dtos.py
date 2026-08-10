from pydantic import BaseModel


class FlaggedItemDto(BaseModel):
    field_id: str
    label: str
    depends_on_label: str
    reason: str


class RecomputeReviewResponse(BaseModel):
    flagged_items: list[FlaggedItemDto]
