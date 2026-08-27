from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brd_group import BrdGroup


async def list_by_user(session: AsyncSession, user_id: str) -> list[BrdGroup]:
    result = await session.execute(
        select(BrdGroup)
        .where(BrdGroup.user_id == user_id)
        .order_by(BrdGroup.created_at.asc())
    )
    return list(result.scalars().all())


async def find_by_id_for_user(
    session: AsyncSession, group_id: str, user_id: str
) -> BrdGroup | None:
    result = await session.execute(
        select(BrdGroup).where(
            BrdGroup.group_id == group_id,
            BrdGroup.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def find_by_id(session: AsyncSession, group_id: str) -> BrdGroup | None:
    """Unscoped lookup — used by access checks that need to verify group existence
    before checking collaborator membership separately."""
    result = await session.execute(select(BrdGroup).where(BrdGroup.group_id == group_id))
    return result.scalar_one_or_none()


async def insert(session: AsyncSession, group: BrdGroup) -> BrdGroup:
    session.add(group)
    await session.flush()
    return group


async def update(
    session: AsyncSession,
    group: BrdGroup,
    title: str,
    description: str | None,
) -> BrdGroup:
    group.title = title
    group.description = description
    await session.flush()
    return group


async def delete(session: AsyncSession, group: BrdGroup) -> None:
    await session.delete(group)
    await session.flush()
