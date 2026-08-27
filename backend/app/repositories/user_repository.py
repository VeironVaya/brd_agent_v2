from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def find_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def find_by_id(session: AsyncSession, user_id: str) -> User | None:
    result = await session.execute(select(User).where(User.user_id == user_id))
    return result.scalar_one_or_none()


async def find_many_by_ids(session: AsyncSession, user_ids: list[str]) -> list[User]:
    """Batch lookup — one IN query instead of one query per id."""
    if not user_ids:
        return []
    result = await session.execute(select(User).where(User.user_id.in_(user_ids)))
    return list(result.scalars().all())


async def insert(session: AsyncSession, user: User) -> User:
    session.add(user)
    await session.flush()
    return user

