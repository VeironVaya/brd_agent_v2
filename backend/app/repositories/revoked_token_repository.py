from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revoked_token import RevokedToken


async def insert(session: AsyncSession, *, jti: str, user_id: str, expires_at: datetime) -> RevokedToken:
    row = RevokedToken(jti=jti, user_id=user_id, expires_at=expires_at)
    session.add(row)
    await session.flush()
    return row


async def is_revoked(session: AsyncSession, jti: str) -> bool:
    result = await session.execute(select(RevokedToken.jti).where(RevokedToken.jti == jti))
    return result.scalar_one_or_none() is not None


async def delete_expired(session: AsyncSession) -> int:
    """Delete all revoked token rows whose expiry has passed.
    Safe to call at startup — returns the count of rows deleted."""
    result = await session.execute(
        delete(RevokedToken).where(RevokedToken.expires_at < datetime.now(timezone.utc))
    )
    await session.flush()
    return result.rowcount

