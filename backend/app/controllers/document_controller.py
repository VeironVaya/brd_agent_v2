from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dtos.document_dtos import GenerateDocumentRequest, GenerateDocumentResponse
from app.middleware.auth import get_current_user
from app.models.user import User
from app.services import document_service


async def generate_document(
    conversation_id: str,
    body: GenerateDocumentRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> GenerateDocumentResponse:
    result = await document_service.generate(
        session, conversation_id=conversation_id, user_id=current_user.user_id, format=body.format
    )
    await session.commit()
    return GenerateDocumentResponse(**result)
