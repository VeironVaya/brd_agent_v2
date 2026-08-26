from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.brd_group import BrdGroup
from app.models.group_collaborator import GroupCollaborator
from app.models.user import User


async def list_by_group(session: AsyncSession, group_id: str) -> list[GroupCollaborator]:
    result = await session.execute(
        select(GroupCollaborator)
        .where(GroupCollaborator.group_id == group_id)
        .order_by(GroupCollaborator.created_at.asc())
    )
    return list(result.scalars().all())


async def find_by_group_and_user(
    session: AsyncSession, group_id: str, user_id: str
) -> GroupCollaborator | None:
    result = await session.execute(
        select(GroupCollaborator).where(
            GroupCollaborator.group_id == group_id,
            GroupCollaborator.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def find_by_id(
    session: AsyncSession, group_collaborator_id: str
) -> GroupCollaborator | None:
    result = await session.execute(
        select(GroupCollaborator).where(
            GroupCollaborator.group_collaborator_id == group_collaborator_id
        )
    )
    return result.scalar_one_or_none()


async def insert(session: AsyncSession, gc: GroupCollaborator) -> GroupCollaborator:
    session.add(gc)
    await session.flush()
    return gc


async def update_role(
    session: AsyncSession, gc: GroupCollaborator, role: str
) -> GroupCollaborator:
    gc.role = role
    await session.flush()
    return gc


async def delete(session: AsyncSession, gc: GroupCollaborator) -> None:
    await session.delete(gc)
    await session.flush()


async def list_groups_for_user(
    session: AsyncSession, user_id: str
) -> list[tuple[BrdGroup, GroupCollaborator]]:
    """All groups this user is a collaborator on (not the owner)."""
    result = await session.execute(
        select(BrdGroup, GroupCollaborator)
        .join(GroupCollaborator, GroupCollaborator.group_id == BrdGroup.group_id)
        .where(GroupCollaborator.user_id == user_id)
        .order_by(BrdGroup.created_at.asc())
    )
    return [(row[0], row[1]) for row in result.all()]


async def list_with_user_details(
    session: AsyncSession, group_id: str
) -> list[tuple[GroupCollaborator, User]]:
    """Collaborators for a group with their user details (for the share modal)."""
    result = await session.execute(
        select(GroupCollaborator, User)
        .join(User, User.user_id == GroupCollaborator.user_id)
        .where(GroupCollaborator.group_id == group_id)
        .order_by(GroupCollaborator.created_at.asc())
    )
    return [(row[0], row[1]) for row in result.all()]
