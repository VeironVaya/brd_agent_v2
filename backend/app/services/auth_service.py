"""Real email+password registration/login — see erd.md's Auth decision:
SSO is deferred, not this. Password hashing via bcrypt directly (not
passlib, to sidestep its bcrypt>=4.1 compatibility issues); sessions are
stateless JWTs, not server-side session rows."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import EmailTakenError, InvalidCredentialsError, InvalidRegistrationError
from app.models.user import User
from app.repositories import user_repository

JWT_ALGORITHM = "HS256"
MIN_PASSWORD_LENGTH = 8


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _issue_token(user: User) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.jwt_expiry_days)
    payload = {"sub": user.user_id, "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


async def register(session: AsyncSession, *, email: str, password: str, name: str) -> tuple[User, str]:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise InvalidRegistrationError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
    if not name.strip():
        raise InvalidRegistrationError("Name is required.")

    existing = await user_repository.find_by_email(session, email)
    if existing is not None:
        raise EmailTakenError("An account with this email already exists.")

    user = User(email=email, password_hash=_hash_password(password), name=name.strip())
    await user_repository.insert(session, user)
    return user, _issue_token(user)


async def login(session: AsyncSession, *, email: str, password: str) -> tuple[User, str]:
    user = await user_repository.find_by_email(session, email)
    # Same error whether the email doesn't exist or the password is wrong —
    # api_contract.md §1: avoids leaking which emails are registered.
    if user is None or not _verify_password(password, user.password_hash):
        raise InvalidCredentialsError("Incorrect email or password.")
    return user, _issue_token(user)


async def get_user_from_token(session: AsyncSession, token: str) -> User | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return await user_repository.find_by_id(session, user_id)
