from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.section import Section


async def list_by_conversation(session: AsyncSession, conversation_id: str) -> list[Section]:
    result = await session.execute(
        select(Section).where(Section.conversation_id == conversation_id).order_by(Section.sort_order)
    )
    return list(result.scalars().all())


async def find_by_id(session: AsyncSession, section_id: str) -> Section | None:
    result = await session.execute(select(Section).where(Section.section_id == section_id))
    return result.scalar_one_or_none()


async def insert(session: AsyncSession, section: Section) -> Section:
    session.add(section)
    await session.flush()
    return section


async def bulk_insert(session: AsyncSession, sections: list[Section]) -> None:
    session.add_all(sections)
    await session.flush()


async def update_title(session: AsyncSession, section: Section, title: str) -> Section:
    section.title = title
    await session.flush()
    return section


async def delete(session: AsyncSession, section: Section) -> None:
    # ON DELETE CASCADE on sections.parent_id handles descendants at the DB level.
    await session.delete(section)
    await session.flush()


async def next_sort_order(session: AsyncSession, conversation_id: str, parent_id: str | None) -> int:
    result = await session.execute(
        select(Section).where(Section.conversation_id == conversation_id, Section.parent_id == parent_id)
    )
    siblings = list(result.scalars().all())
    return len(siblings)
