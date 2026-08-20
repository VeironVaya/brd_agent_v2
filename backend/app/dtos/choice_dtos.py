from typing import Any

from pydantic import BaseModel


class SaveChoicesRequest(BaseModel):
    choice_data: dict[str, Any]


class SaveChoicesResponse(BaseModel):
    status: str
    completeness: int | None = None
    confidence: int | None = None
    answer: str | None = None
    missing: list[str] = []
    choice_data: dict[str, Any]