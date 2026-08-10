"""Real email+password registration/login — see erd.md's Auth decision:
SSO is deferred, not this. Password hashing via bcrypt directly (not
passlib, to sidestep its bcrypt>=4.1 compatibility issues); sessions are
stateless JWTs, not server-side session rows — except for logout, which
needs one point of server-side state no matter what (a stateless token
can't un-verify itself). Each issued token carries a unique `jti`;
logout records that `jti` in `revoked_tokens` (erd.md), and every
token verification checks it there. Tokens issued before this existed
have no `jti` and simply can't be explicitly revoked — they still expire
normally on their own `exp`, so this is a one-time transitional gap, not
an ongoing one."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import EmailTakenError, InvalidCredentialsError, InvalidRegistrationError
from app.models.user import User
from app.repositories import revoked_token_repository, user_repository
from app.utils.ids import new_id

JWT_ALGORITHM = "HS256"
MIN_PASSWORD_LENGTH = 8


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def _issue_token(user: User) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiry_hours)
    payload = {"sub": user.user_id, "exp": expires_at, "jti": new_id()}
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def _decode(token: str) -> dict | None:
    try:
        # jwt.decode already rejects an expired token on its own (raises
        # ExpiredSignatureError, a PyJWTError subclass) — the revoked_tokens
        # check below only ever needs to catch a logout before expiry.
        return jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


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
    payload = _decode(token)
    if payload is None:
        return None

    jti = payload.get("jti")
    if jti and await revoked_token_repository.is_revoked(session, jti):
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None
    return await user_repository.find_by_id(session, user_id)


async def logout(session: AsyncSession, token: str) -> None:
    """Records this token's `jti` as revoked, effective immediately —
    every subsequent get_user_from_token call for it 401s from here on,
    even though the token itself remains signature-valid until its exp.
    A token with no `jti` (issued before this existed) or an already
    garbage/expired token has nothing to revoke; silently no-ops rather
    than erroring, since the caller's goal ("make sure this token can't
    be used again") is already satisfied either way."""
    payload = _decode(token)
    if payload is None:
        return
    jti = payload.get("jti")
    user_id = payload.get("sub")
    if not jti or not user_id:
        return
    if await revoked_token_repository.is_revoked(session, jti):
        return  # already logged out (e.g. a duplicate/retried request) — idempotent no-op
    exp = payload.get("exp")
    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else datetime.now(timezone.utc)
    await revoked_token_repository.insert(session, jti=jti, user_id=user_id, expires_at=expires_at)
