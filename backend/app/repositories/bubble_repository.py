from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bubble import Bubble
from app.models.section import Section


async def list_by_section(session: AsyncSession, section_id: str) -> list[Bubble]:
    result = await session.execute(
        select(Bubble).where(Bubble.section_id == section_id).order_by(Bubble.created_at)
    )
    return list(result.scalars().all())


async def list_by_conversation(session: AsyncSession, conversation_id: str) -> list[Bubble]:
    result = await session.execute(
        select(Bubble)
        .join(Section, Section.section_id == Bubble.section_id)
        .where(Section.conversation_id == conversation_id)
        .order_by(Bubble.created_at)
    )
    return list(result.scalars().all())


async def insert(session: AsyncSession, bubble: Bubble) -> Bubble:
    session.add(bubble)
    await session.flush()
    return bubble
