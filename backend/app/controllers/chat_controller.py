from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dtos.chat_dtos import MessageDto, PostMessageRequest, PostMessageResponse
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services import chat_service


async def post_message(
    conversation_id: str,
    room_id: str,
    body: PostMessageRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> PostMessageResponse:
    messages = await chat_service.post_message(
        session,
        conversation_id=conversation_id,
        user_id=current_user.user_id,
        room_id=room_id,
        text=body.text,
    )
    await session.commit()
    return PostMessageResponse(messages=[MessageDto(**m) for m in messages])
