from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dtos.choice_dtos import SaveChoicesRequest, SaveChoicesResponse
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services import choice_section_service


async def save_choices(
    conversation_id: str,
    section_id: str,
    body: SaveChoicesRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> SaveChoicesResponse:
    answer = await choice_section_service.save_choices(
        session,
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        section_id=section_id,
        choice_data=body.choice_data,
    )
    await session.commit()
    return SaveChoicesResponse(**answer)