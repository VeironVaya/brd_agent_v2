from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dtos.auth_dtos import AuthResponse, LoginRequest, RegisterRequest, SessionResponse, UserDto
from app.middleware.auth import bearer_scheme, get_current_user
from app.models.user import User
from app.services import auth_service


async def register(body: RegisterRequest, session: AsyncSession = Depends(get_db)) -> AuthResponse:
    user, token = await auth_service.register(session, email=body.email, password=body.password, name=body.name)
    await session.commit()
    return AuthResponse(user=UserDto(id=user.user_id, email=user.email, name=user.name), token=token)


async def login(body: LoginRequest, session: AsyncSession = Depends(get_db)) -> AuthResponse:
    user, token = await auth_service.login(session, email=body.email, password=body.password)
    await session.commit()
    return AuthResponse(user=UserDto(id=user.user_id, email=user.email, name=user.name), token=token)


async def get_session(current_user: User = Depends(get_current_user)) -> SessionResponse:
    return SessionResponse(user=UserDto(id=current_user.user_id, email=current_user.email, name=current_user.name))


async def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db),
) -> None:
    # Requires a bearer token (unlike before) — logout now records that
    # specific token's jti as revoked (auth_service.logout), so it needs
    # to know which token it's invalidating. See api_contract.md §1.
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing or invalid authorization token.")
    await auth_service.logout(session, credentials.credentials)
    await session.commit()
