from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.user import User
from app.services import auth_service

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI dependency added to every /api/... controller. Decodes the
    Authorization: Bearer <token> header, loads the User, or 401s."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing or invalid authorization token.")

    user = await auth_service.get_user_from_token(session, credentials.credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Missing or invalid authorization token.")
    return user
