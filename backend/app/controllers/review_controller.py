from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dtos.review_dtos import FlaggedItemDto, RecomputeReviewResponse
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services import conversation_service, review_service


async def recompute_review(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> RecomputeReviewResponse:
    await conversation_service.get_accessible(session, conversation_id, current_user.user_id, min_role="viewer")
    items = await review_service.recompute(session, conversation_id)
    return RecomputeReviewResponse(flagged_items=[FlaggedItemDto(**item) for item in items])
