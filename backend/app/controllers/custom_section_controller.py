from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dtos.custom_section_dtos import (
    AddCustomSectionRequest,
    AddCustomSectionResponse,
    RenameCustomSectionRequest,
    RenameCustomSectionResponse,
)
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services import custom_section_service


async def add_custom_section(
    conversation_id: str,
    body: AddCustomSectionRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> AddCustomSectionResponse:
    section = await custom_section_service.add_node(
        session,
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        target=body.target.model_dump() if body.target else None,
        title=body.title,
        has_children=body.has_children,
        purpose=body.purpose,
    )
    await session.commit()
    return AddCustomSectionResponse(
        id=section.section_id, title=section.title, purpose=section.purpose, has_children=not section.is_leaf
    )


async def rename_custom_section(
    conversation_id: str,
    section_id: str,
    body: RenameCustomSectionRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> RenameCustomSectionResponse:
    section = await custom_section_service.rename_node(
        session,
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        section_id=section_id,
        title=body.title,
    )
    await session.commit()
    return RenameCustomSectionResponse(id=section.section_id, title=section.title)


async def remove_custom_section(
    conversation_id: str,
    section_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    await custom_section_service.remove_node(
        session, conversation_id=conversation_id, user_id=current_user.user_id, section_id=section_id
    )
    await session.commit()
