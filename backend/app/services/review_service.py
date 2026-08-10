"""Flagged detection — erd.md's SECTION_DEPENDENCY + ANSWER.answered_at
join. `reason` text is regenerated on demand every call, never stored
(erd.md's explicit decision)."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import section_dependency_repository, section_repository


def _label(section) -> str:
    code = section.template_key or section.section_id
    return f"{code} {section.title}"


async def find_flagged_section_ids(session: AsyncSession, conversation_id: str) -> set[str]:
    pairs = await section_dependency_repository.find_flagged(session, conversation_id)
    return {dependent_id for dependent_id, _prereq_id in pairs}


async def recompute(session: AsyncSession, conversation_id: str) -> list[dict]:
    pairs = await section_dependency_repository.find_flagged(session, conversation_id)
    if not pairs:
        return []

    sections = await section_repository.list_by_conversation(session, conversation_id)
    by_id = {s.section_id: s for s in sections}

    items = []
    for dependent_id, prereq_id in pairs:
        dependent = by_id.get(dependent_id)
        prereq = by_id.get(prereq_id)
        if dependent is None or prereq is None:
            continue
        prereq_label = _label(prereq)
        items.append(
            {
                "field_id": dependent.template_key or dependent.section_id,
                "label": _label(dependent),
                "depends_on_label": prereq_label,
                "reason": (
                    f"{prereq_label} was updated — its answer no longer matches what this item assumed. "
                    "Re-verify this item against the new information."
                ),
            }
        )
    return items
