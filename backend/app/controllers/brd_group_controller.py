from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dtos.brd_group_dtos import (
    AddGroupCollaboratorRequest,
    AssignGroupRequest,
    CreateGroupRequest,
    GroupCollaboratorDto,
    GroupCollaboratorListResponse,
    GroupDto,
    GroupListResponse,
    UpdateGroupCollaboratorRoleRequest,
    UpdateGroupRequest,
)
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services import brd_group_service


def _to_group_dto(g: dict) -> GroupDto:
    return GroupDto(
        id=g["group_id"],
        title=g["title"],
        description=g["description"],
        created_at=g["created_at"],
        role=g["role"],
    )


async def list_groups(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> GroupListResponse:
    groups = await brd_group_service.list_for_user(session, current_user.user_id)
    return GroupListResponse(groups=[_to_group_dto(g) for g in groups])


async def create_group(
    body: CreateGroupRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> GroupDto:
    group = await brd_group_service.create(
        session,
        user_id=current_user.user_id,
        title=body.title,
        description=body.description,
    )
    await session.commit()
    return GroupDto(
        id=group.group_id,
        title=group.title,
        description=group.description,
        created_at=group.created_at,
        role="owner",
    )


async def update_group(
    group_id: str,
    body: UpdateGroupRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> GroupDto:
    group = await brd_group_service.update(
        session,
        group_id=group_id,
        user_id=current_user.user_id,
        title=body.title,
        description=body.description,
    )
    await session.commit()
    return GroupDto(
        id=group.group_id,
        title=group.title,
        description=group.description,
        created_at=group.created_at,
        role="owner",
    )


async def delete_group(
    group_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    await brd_group_service.delete(session, group_id=group_id, user_id=current_user.user_id)
    await session.commit()


async def assign_group(
    conversation_id: str,
    body: AssignGroupRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    await brd_group_service.assign_group(
        session,
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        group_id=body.group_id,
    )
    await session.commit()


# ── Group collaborator endpoints ──────────────────────────────────────────────

async def list_group_collaborators(
    group_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> GroupCollaboratorListResponse:
    collaborators = await brd_group_service.list_collaborators(
        session, group_id=group_id, owner_user_id=current_user.user_id
    )
    return GroupCollaboratorListResponse(
        collaborators=[GroupCollaboratorDto(**c) for c in collaborators]
    )


async def add_group_collaborator(
    group_id: str,
    body: AddGroupCollaboratorRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> GroupCollaboratorDto:
    collaborator = await brd_group_service.add_collaborator(
        session,
        group_id=group_id,
        owner_user_id=current_user.user_id,
        email=body.email,
        role=body.role,
    )
    await session.commit()
    return GroupCollaboratorDto(**collaborator)


async def update_group_collaborator_role(
    group_id: str,
    collaborator_id: str,
    body: UpdateGroupCollaboratorRoleRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> GroupCollaboratorDto:
    collaborator = await brd_group_service.update_collaborator_role(
        session,
        group_id=group_id,
        owner_user_id=current_user.user_id,
        collaborator_id=collaborator_id,
        role=body.role,
    )
    await session.commit()
    return GroupCollaboratorDto(**collaborator)


async def remove_group_collaborator(
    group_id: str,
    collaborator_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    await brd_group_service.remove_collaborator(
        session,
        group_id=group_id,
        owner_user_id=current_user.user_id,
        collaborator_id=collaborator_id,
    )
    await session.commit()
