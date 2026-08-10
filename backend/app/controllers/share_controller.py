from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dtos.share_dtos import (
    AddCollaboratorRequest,
    CollaboratorDto,
    CollaboratorListResponse,
    UpdateCollaboratorRoleRequest,
)
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services import share_service


async def add_collaborator(
    conversation_id: str,
    body: AddCollaboratorRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CollaboratorDto:
    collaborator = await share_service.add_collaborator(
        session, conversation_id=conversation_id, owner_user_id=current_user.user_id, email=body.email, role=body.role
    )
    await session.commit()
    return CollaboratorDto(**collaborator)


async def list_collaborators(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CollaboratorListResponse:
    collaborators = await share_service.list_collaborators(
        session, conversation_id=conversation_id, owner_user_id=current_user.user_id
    )
    return CollaboratorListResponse(collaborators=[CollaboratorDto(**c) for c in collaborators])


async def update_collaborator_role(
    conversation_id: str,
    collaborator_id: str,
    body: UpdateCollaboratorRoleRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CollaboratorDto:
    collaborator = await share_service.update_role(
        session,
        conversation_id=conversation_id,
        owner_user_id=current_user.user_id,
        collaborator_id=collaborator_id,
        role=body.role,
    )
    await session.commit()
    return CollaboratorDto(**collaborator)


async def remove_collaborator(
    conversation_id: str,
    collaborator_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    await share_service.remove_collaborator(
        session, conversation_id=conversation_id, owner_user_id=current_user.user_id, collaborator_id=collaborator_id
    )
    await session.commit()
