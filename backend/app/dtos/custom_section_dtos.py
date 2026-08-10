from typing import Literal

from pydantic import BaseModel


class TargetDto(BaseModel):
    kind: Literal["template", "custom"]
    id: str


class AddCustomSectionRequest(BaseModel):
    target: TargetDto | None = None
    title: str
    has_children: bool = False
    purpose: str | None = None


class AddCustomSectionResponse(BaseModel):
    id: str
    title: str
    purpose: str | None = None
    has_children: bool
    children: list = []


class RenameCustomSectionRequest(BaseModel):
    title: str


class RenameCustomSectionResponse(BaseModel):
    id: str
    title: str
