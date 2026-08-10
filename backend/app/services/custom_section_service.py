"""Add/rename/remove CustomSection nodes, arbitrary depth. `target`
resolution mirrors api_contract.md §4 exactly: kind='template' resolves
by template_key (within this conversation), kind='custom' resolves by
real section_id, target=None means standalone top-level."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError, TitleRequiredError
from app.models.section import Section
from app.repositories import section_repository
from app.services import conversation_service


async def _resolve_target(
    session: AsyncSession, conversation_id: str, target: dict | None
) -> str | None:
    """Returns the real parent section_id (or None for standalone)."""
    if target is None:
        return None

    if target["kind"] == "template":
        sections = await section_repository.list_by_conversation(session, conversation_id)
        match = next((s for s in sections if s.template_key == target["id"]), None)
        if match is None:
            raise NotFoundError(f"Template section {target['id']!r} not found.")
        return match.section_id

    if target["kind"] == "custom":
        section = await section_repository.find_by_id(session, target["id"])
        if section is None or section.conversation_id != conversation_id:
            raise NotFoundError("Custom section not found.")
        return section.section_id

    raise NotFoundError(f"Unknown target kind {target['kind']!r}.")


async def add_node(
    session: AsyncSession,
    *,
    conversation_id: str,
    user_id: str,
    target: dict | None,
    title: str,
    has_children: bool,
    purpose: str | None,
) -> Section:
    await conversation_service.get_owned(session, conversation_id, user_id)

    trimmed = title.strip()
    if not trimmed:
        raise TitleRequiredError("Section title is required.")

    parent_id = await _resolve_target(session, conversation_id, target)
    sort_order = await section_repository.next_sort_order(session, conversation_id, parent_id)

    section = Section(
        conversation_id=conversation_id,
        parent_id=parent_id,
        is_leaf=not has_children,
        is_custom=True,
        is_general=False,
        template_key=None,
        title=trimmed,
        purpose=purpose,
        sort_order=sort_order,
    )
    return await section_repository.insert(session, section)


async def _find_owned_custom_section(
    session: AsyncSession, conversation_id: str, user_id: str, section_id: str
) -> Section:
    await conversation_service.get_owned(session, conversation_id, user_id)
    section = await section_repository.find_by_id(session, section_id)
    if section is None or section.conversation_id != conversation_id or not section.is_custom:
        raise NotFoundError("Custom section not found.")
    return section


async def rename_node(
    session: AsyncSession, *, conversation_id: str, user_id: str, section_id: str, title: str
) -> Section:
    trimmed = title.strip()
    if not trimmed:
        raise TitleRequiredError("Section title is required.")
    section = await _find_owned_custom_section(session, conversation_id, user_id, section_id)
    return await section_repository.update_title(session, section, trimmed)


async def remove_node(session: AsyncSession, *, conversation_id: str, user_id: str, section_id: str) -> None:
    section = await _find_owned_custom_section(session, conversation_id, user_id, section_id)
    # ON DELETE CASCADE on sections.parent_id handles descendants at the DB level.
    await section_repository.delete(session, section)
