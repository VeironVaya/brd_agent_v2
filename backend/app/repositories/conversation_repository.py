from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.answer import Answer
from app.models.conversation import Conversation
from app.models.section import Section


async def list_by_user(session: AsyncSession, user_id: str) -> list[Conversation]:
    result = await session.execute(
        select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc())
    )
    return list(result.scalars().all())


async def find_by_id_for_user(session: AsyncSession, conversation_id: str, user_id: str) -> Conversation | None:
    result = await session.execute(
        select(Conversation).where(
            Conversation.conversation_id == conversation_id, Conversation.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def find_by_id(session: AsyncSession, conversation_id: str) -> Conversation | None:
    """Unscoped lookup by PK — used by permission checks that still need to
    distinguish owner vs. collaborator vs. no-access themselves, unlike
    find_by_id_for_user's hard owner-only filter."""
    result = await session.execute(select(Conversation).where(Conversation.conversation_id == conversation_id))
    return result.scalar_one_or_none()


async def insert(session: AsyncSession, conversation: Conversation) -> Conversation:
    session.add(conversation)
    await session.flush()
    return conversation


async def update_title(session: AsyncSession, conversation: Conversation, title: str) -> Conversation:
    conversation.title = title
    conversation.updated_at = datetime.now(timezone.utc)
    await session.flush()
    return conversation


async def touch_updated_at(session: AsyncSession, conversation: Conversation) -> None:
    conversation.updated_at = datetime.now(timezone.utc)
    await session.flush()


async def update_generation_metadata(session: AsyncSession, conversation: Conversation, version: str) -> None:
    conversation.last_generated_at = datetime.now(timezone.utc)
    conversation.last_generated_version = version
    await session.flush()


async def delete(session: AsyncSession, conversation: Conversation) -> None:
    await session.delete(conversation)
    await session.flush()


async def answered_count(session: AsyncSession, conversation_id: str) -> int:
    """Computed, not stored — erd.md's explicit decision. Counts standard-template
    leaves (is_custom=False, is_leaf=True) with status='done' for this conversation."""
    result = await session.execute(
        select(func.count())
        .select_from(Section)
        .join(Answer, Answer.section_id == Section.section_id)
        .where(
            Section.conversation_id == conversation_id,
            Section.is_custom.is_(False),
            Section.is_leaf.is_(True),
            Answer.status == "done",
        )
    )
    return result.scalar_one()
