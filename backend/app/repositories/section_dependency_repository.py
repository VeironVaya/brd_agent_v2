from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.models.answer import Answer
from app.models.section import Section
from app.models.section_dependency import SectionDependency


async def bulk_insert(session: AsyncSession, deps: list[SectionDependency]) -> None:
    # Plain Core insert, not ORM add_all — SQLAlchemy 2.0's ORM bulk-insert
    # path for a composite-PK-only table (no non-key columns at all) was
    # observed dropping depends_on_section_id and inserting DEFAULT for
    # every row. Core insert() with explicit value dicts sidesteps that.
    if not deps:
        return
    rows = [{"section_id": d.section_id, "depends_on_section_id": d.depends_on_section_id} for d in deps]
    await session.execute(insert(SectionDependency), rows)
    await session.flush()


async def list_by_conversation(session: AsyncSession, conversation_id: str) -> list[SectionDependency]:
    result = await session.execute(
        select(SectionDependency)
        .join(Section, Section.section_id == SectionDependency.section_id)
        .where(Section.conversation_id == conversation_id)
    )
    return list(result.scalars().all())


async def find_flagged(session: AsyncSession, conversation_id: str) -> list[tuple[str, str]]:
    """erd.md's worked flagged-detection query: a leaf is flagged if it's
    done/review but a prerequisite's answer changed more recently than its own.
    Returns (dependent_section_id, prereq_section_id) pairs."""
    dependent = aliased(Answer)
    prereq = aliased(Answer)
    dependent_section = aliased(Section)

    result = await session.execute(
        select(SectionDependency.section_id, SectionDependency.depends_on_section_id)
        .join(dependent, dependent.section_id == SectionDependency.section_id)
        .join(prereq, prereq.section_id == SectionDependency.depends_on_section_id)
        .join(dependent_section, dependent_section.section_id == SectionDependency.section_id)
        .where(
            dependent_section.conversation_id == conversation_id,
            dependent.status.in_(["done", "review"]),
            prereq.answered_at.is_not(None),
            dependent.answered_at.is_not(None),
            prereq.answered_at > dependent.answered_at,
        )
    )
    return [(row[0], row[1]) for row in result.all()]
