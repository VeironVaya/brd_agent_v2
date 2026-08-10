"""Conversation CRUD + the one-time template seeding that happens on
create. Seeding is application code, not a DB trigger — erd.md's
explicit decision."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ForbiddenError, NotFoundError, TitleRequiredError
from app.models.conversation import Conversation
from app.models.section import Section
from app.models.section_dependency import SectionDependency
from app.repositories import (
    answer_repository,
    bubble_repository,
    collaborator_repository,
    conversation_repository,
    section_dependency_repository,
    section_repository,
    user_repository,
)
from app.services import review_service, section_tree_service, template_service
from app.utils.ids import new_id

# Effective access levels, ranked low-to-high. "owner" is never a stored
# Collaborator row — it's implicit from Conversation.user_id, see erd.md.
ROLE_RANK = {"viewer": 0, "editor": 1, "owner": 2}


async def _seed_template_and_general(session: AsyncSession, conversation_id: str) -> None:
    sections: list[Section] = []
    id_by_template_key: dict[str, str] = {}

    # Ids generated explicitly here, not left to the model's default=new_id
    # column default — that default only fires at flush time, so reading
    # section.section_id immediately after construction (needed below, to
    # wire up parent_id/SECTION_DEPENDENCY before anything is flushed)
    # would just read None. Generating up front sidesteps that entirely.

    def walk(nodes: tuple, parent_id: str) -> None:
        for index, node in enumerate(nodes):
            section_id = new_id()
            section = Section(
                section_id=section_id,
                conversation_id=conversation_id,
                parent_id=parent_id,
                is_leaf=node.is_leaf,
                is_custom=False,
                is_general=False,
                template_key=node.id,
                title=node.title,
                sort_order=index,
            )
            sections.append(section)
            id_by_template_key[node.id] = section_id
            if not node.is_leaf:
                walk(node.children, section_id)

    for top_index, top in enumerate(template_service.SECTIONS):
        top_section_id = new_id()
        top_section = Section(
            section_id=top_section_id,
            conversation_id=conversation_id,
            parent_id=None,
            is_leaf=False,
            is_custom=False,
            is_general=False,
            template_key=top.id,
            title=top.title,
            sort_order=top_index,
        )
        sections.append(top_section)
        id_by_template_key[top.id] = top_section_id
        walk(top.children, top_section_id)

    general = Section(
        section_id=new_id(),
        conversation_id=conversation_id,
        parent_id=None,
        is_leaf=False,
        is_custom=False,
        is_general=True,
        template_key=None,
        title="General",
        sort_order=len(template_service.SECTIONS),
    )
    sections.append(general)

    await section_repository.bulk_insert(session, sections)

    deps: list[SectionDependency] = []
    for leaf in template_service.flatten_leaves():
        dependent_id = id_by_template_key[leaf.id]
        for dep_template_key in leaf.depends_on:
            deps.append(
                SectionDependency(
                    section_id=dependent_id,
                    depends_on_section_id=id_by_template_key[dep_template_key],
                )
            )
    if deps:
        await section_dependency_repository.bulk_insert(session, deps)


async def create(session: AsyncSession, *, user_id: str, title: str, context: str | None) -> Conversation:
    trimmed = title.strip()
    if not trimmed:
        raise TitleRequiredError("Title is required — give this BRD a name.")

    conversation = Conversation(user_id=user_id, title=trimmed, context=context)
    await conversation_repository.insert(session, conversation)
    await _seed_template_and_general(session, conversation.conversation_id)
    return conversation


async def list_for_user(session: AsyncSession, user_id: str) -> list[dict]:
    owned = await conversation_repository.list_by_user(session, user_id)
    shared = await collaborator_repository.list_conversations_for_user(session, user_id)

    items = []
    for c in owned:
        count = await conversation_repository.answered_count(session, c.conversation_id)
        items.append(
            {
                "id": c.conversation_id,
                "title": c.title,
                "updated_at": c.updated_at,
                "answered_count": count,
                "role": "owner",
                "owner_name": None,
                "owner_email": None,
            }
        )
    for c, collab in shared:
        count = await conversation_repository.answered_count(session, c.conversation_id)
        owner = await user_repository.find_by_id(session, c.user_id)
        items.append(
            {
                "id": c.conversation_id,
                "title": c.title,
                "updated_at": c.updated_at,
                "answered_count": count,
                "role": collab.role,
                "owner_name": owner.name if owner else None,
                "owner_email": owner.email if owner else None,
            }
        )
    items.sort(key=lambda i: i["updated_at"], reverse=True)
    return items


async def get_owned(session: AsyncSession, conversation_id: str, user_id: str) -> Conversation:
    """Strict owner-only gate — for conversation lifecycle (rename/delete)
    and collaborator management. Everything a collaborator should also be
    able to do goes through get_accessible instead."""
    conversation = await conversation_repository.find_by_id_for_user(session, conversation_id, user_id)
    if conversation is None:
        raise NotFoundError("Conversation not found.")
    return conversation


async def get_accessible(
    session: AsyncSession, conversation_id: str, user_id: str, *, min_role: str = "viewer"
) -> tuple[Conversation, str]:
    """Owner-or-collaborator gate, with a minimum required role. Returns the
    conversation plus the caller's effective role so callers (get_detail)
    can surface it on the wire."""
    conversation = await conversation_repository.find_by_id(session, conversation_id)
    if conversation is None:
        raise NotFoundError("Conversation not found.")

    if conversation.user_id == user_id:
        role = "owner"
    else:
        collaborator = await collaborator_repository.find_by_conversation_and_user(session, conversation_id, user_id)
        if collaborator is None:
            # 404, not 403 — a non-collaborator shouldn't learn this conversation exists.
            raise NotFoundError("Conversation not found.")
        role = collaborator.role

    if ROLE_RANK[role] < ROLE_RANK[min_role]:
        raise ForbiddenError("You don't have permission to do that.")

    return conversation, role


async def rename(session: AsyncSession, *, conversation_id: str, user_id: str, title: str) -> Conversation:
    trimmed = title.strip()
    if not trimmed:
        raise TitleRequiredError("Title is required — give this BRD a name.")
    conversation = await get_owned(session, conversation_id, user_id)
    return await conversation_repository.update_title(session, conversation, trimmed)


async def delete(session: AsyncSession, *, conversation_id: str, user_id: str) -> None:
    conversation = await get_owned(session, conversation_id, user_id)
    await conversation_repository.delete(session, conversation)


def _wire_key(section: Section) -> str:
    return section.template_key if not section.is_custom else section.section_id


async def get_detail(session: AsyncSession, *, conversation_id: str, user_id: str) -> dict:
    conversation, role = await get_accessible(session, conversation_id, user_id, min_role="viewer")

    sections = await section_repository.list_by_conversation(session, conversation_id)
    by_id = {s.section_id: s for s in sections}
    answers = await answer_repository.list_by_conversation(session, conversation_id)
    bubbles = await bubble_repository.list_by_conversation(session, conversation_id)
    flagged_ids = await review_service.find_flagged_section_ids(session, conversation_id)

    answers_dict: dict[str, dict] = {}
    for answer in answers:
        section = by_id.get(answer.section_id)
        if section is None:
            continue
        answers_dict[_wire_key(section)] = {
            "status": answer.status,
            "completeness": answer.completeness,
            "confidence": answer.confidence,
            "answer": answer.answer_text,
            "missing": answer.missing_items or [],
            "flagged": True if answer.section_id in flagged_ids else None,
        }

    messages_dict: dict[str, list[dict]] = {}
    for bubble in bubbles:
        section = by_id.get(bubble.section_id)
        if section is None:
            continue
        key = template_service.GENERAL_ROOM_ID if section.is_general else _wire_key(section)
        messages_dict.setdefault(key, []).append(
            {"id": bubble.bubble_id, "role": bubble.role, "text": bubble.text}
        )
    messages_dict.setdefault(template_service.GENERAL_ROOM_ID, [])

    custom_sections = section_tree_service.build_custom_tree(sections)
    flagged_items = await review_service.recompute(session, conversation_id)
    answered_count = await conversation_repository.answered_count(session, conversation_id)

    focused_section = by_id.get(conversation.focused_section_id) if conversation.focused_section_id else None
    focused_field_id = _wire_key(focused_section) if focused_section else None

    return {
        "id": conversation.conversation_id,
        "title": conversation.title,
        "updated_at": conversation.updated_at,
        "last_generated_at": conversation.last_generated_at,
        "last_generated_version": conversation.last_generated_version,
        "answered_count": answered_count,
        "focused_field_id": focused_field_id,
        "role": role,
        "answers": answers_dict,
        "custom_sections": custom_sections,
        "flagged_items": flagged_items,
        "messages": messages_dict,
    }
