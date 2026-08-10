from pydantic import BaseModel


class AddCollaboratorRequest(BaseModel):
    email: str
    role: str  # "editor" | "viewer"


class CollaboratorDto(BaseModel):
    id: str
    user_id: str
    email: str
    name: str
    role: str


class CollaboratorListResponse(BaseModel):
    collaborators: list[CollaboratorDto]


class UpdateCollaboratorRoleRequest(BaseModel):
    role: str
