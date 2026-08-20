from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dtos.conversation_dtos import (
    ConversationDetailResponse,
    ConversationListItem,
    ConversationListResponse,
    CreateConversationRequest,
    CreateConversationResponse,
    RenameConversationRequest,
    RenameConversationResponse,
)
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services import conversation_service


async def list_conversations(
    current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_db)
) -> ConversationListResponse:
    items = await conversation_service.list_for_user(session, current_user.user_id)
    return ConversationListResponse(conversations=[ConversationListItem(**item) for item in items])


async def create_conversation(
    body: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CreateConversationResponse:
    conversation = await conversation_service.create(
        session,
        user_id=current_user.user_id,
        title=body.title,
        context=body.context,
        requestor_directorate=body.requestor_directorate,
        impacted_stakeholders=body.impacted_stakeholders,
    )
    await session.commit()
    return CreateConversationResponse(id=conversation.conversation_id)


async def rename_conversation(
    conversation_id: str,
    body: RenameConversationRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> RenameConversationResponse:
    conversation = await conversation_service.rename(
        session, conversation_id=conversation_id, user_id=current_user.user_id, title=body.title
    )
    await session.commit()
    return RenameConversationResponse(id=conversation.conversation_id, title=conversation.title)


async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    await conversation_service.delete(session, conversation_id=conversation_id, user_id=current_user.user_id)
    await session.commit()


async def get_conversation_detail(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ConversationDetailResponse:
    detail = await conversation_service.get_detail(
        session, conversation_id=conversation_id, user_id=current_user.user_id
    )
    return ConversationDetailResponse(**detail)
