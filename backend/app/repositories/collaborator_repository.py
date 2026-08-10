from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collaborator import Collaborator
from app.models.conversation import Conversation


async def insert(session: AsyncSession, collaborator: Collaborator) -> Collaborator:
    session.add(collaborator)
    await session.flush()
    return collaborator


async def find_by_conversation_and_user(
    session: AsyncSession, conversation_id: str, user_id: str
) -> Collaborator | None:
    result = await session.execute(
        select(Collaborator).where(
            Collaborator.conversation_id == conversation_id, Collaborator.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def find_by_id(session: AsyncSession, collaborator_id: str) -> Collaborator | None:
    result = await session.execute(select(Collaborator).where(Collaborator.collaborator_id == collaborator_id))
    return result.scalar_one_or_none()


async def list_by_conversation(session: AsyncSession, conversation_id: str) -> list[Collaborator]:
    result = await session.execute(
        select(Collaborator).where(Collaborator.conversation_id == conversation_id).order_by(Collaborator.created_at)
    )
    return list(result.scalars().all())


async def list_conversations_for_user(session: AsyncSession, user_id: str) -> list[tuple[Conversation, Collaborator]]:
    result = await session.execute(
        select(Conversation, Collaborator)
        .join(Collaborator, Collaborator.conversation_id == Conversation.conversation_id)
        .where(Collaborator.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    return [(row[0], row[1]) for row in result.all()]


async def update_role(session: AsyncSession, collaborator: Collaborator, role: str) -> Collaborator:
    collaborator.role = role
    await session.flush()
    return collaborator


async def delete(session: AsyncSession, collaborator: Collaborator) -> None:
    await session.delete(collaborator)
    await session.flush()
