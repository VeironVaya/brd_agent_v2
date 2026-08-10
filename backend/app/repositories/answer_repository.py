from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.answer import Answer
from app.models.section import Section


async def find_by_section_id(session: AsyncSession, section_id: str) -> Answer | None:
    result = await session.execute(select(Answer).where(Answer.section_id == section_id))
    return result.scalar_one_or_none()


async def list_by_conversation(session: AsyncSession, conversation_id: str) -> list[Answer]:
    result = await session.execute(
        select(Answer).join(Section, Section.section_id == Answer.section_id).where(
            Section.conversation_id == conversation_id
        )
    )
    return list(result.scalars().all())


async def upsert(
    session: AsyncSession,
    section_id: str,
    *,
    status: str,
    completeness: int | None = None,
    confidence: int | None = None,
    answer_text: str | None = None,
    missing_items: list[str] | None = None,
    touch_answered_at: bool = True,
) -> Answer:
    answer = await find_by_section_id(session, section_id)
    if answer is None:
        answer = Answer(section_id=section_id, status=status, missing_items=missing_items or [])
        session.add(answer)

    answer.status = status
    if completeness is not None:
        answer.completeness = completeness
    if confidence is not None:
        answer.confidence = confidence
    if answer_text is not None:
        answer.answer_text = answer_text
    if missing_items is not None:
        answer.missing_items = missing_items
    if touch_answered_at:
        answer.answered_at = datetime.now(timezone.utc)

    await session.flush()
    return answer
