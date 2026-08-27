from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CreateGroupRequest(BaseModel):
    title: str
    description: str | None = None


class UpdateGroupRequest(BaseModel):
    title: str
    description: str | None = None


class AssignGroupRequest(BaseModel):
    group_id: str | None = None


class GroupDto(BaseModel):
    id: str
    title: str
    description: str | None = None
    created_at: datetime
    role: str  # "owner" | "editor" | "viewer"


class GroupListResponse(BaseModel):
    groups: list[GroupDto]


# ── Group collaborator DTOs ───────────────────────────────────────────────────

class AddGroupCollaboratorRequest(BaseModel):
    email: str
    role: str  # "editor" | "viewer"


class UpdateGroupCollaboratorRoleRequest(BaseModel):
    role: str


class GroupCollaboratorDto(BaseModel):
    id: str
    user_id: str
    email: str
    name: str
    role: str


class GroupCollaboratorListResponse(BaseModel):
    collaborators: list[GroupCollaboratorDto]
