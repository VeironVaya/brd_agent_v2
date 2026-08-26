"""Conversation CRUD + the one-time template seeding that happens on
create. Seeding is application code, not a DB trigger — erd.md's
explicit decision."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ForbiddenError, InvalidChoiceDataError, NotFoundError, TitleRequiredError
from app.models.conversation import Conversation
from app.models.section import Section
from app.models.section_dependency import SectionDependency
from app.repositories import (
    answer_repository,
    bubble_repository,
    collaborator_repository,
    conversation_repository,
    group_collaborator_repository,
    section_dependency_repository,
    section_repository,
    user_repository,
)
from app.services import review_service, section_tree_service, template_service
from app.utils.ids import new_id

# Effective access levels, ranked low-to-high. "owner" is never a stored
# Collaborator row — it's implicit from Conversation.user_id, see erd.md.
ROLE_RANK = {"viewer": 0, "editor": 1, "owner": 2}

DIRECTORATE_OPTIONS = {
    "CEO Office",
    "Marketing",
    "Sales",
    "Planning & Transformation (P&T)",
    "Finance & Risk Management",
    "Network",
    "Information Technology (IT)",
    "Human Capital Management (HCM)",
}


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


async def create(
    session: AsyncSession,
    *,
    user_id: str,
    title: str,
    context: str | None,
    requestor_directorate: str | None = None,
    impacted_stakeholders: list[str] | None = None,
    group_id: str | None = None,
) -> Conversation:
    trimmed = title.strip()
    if not trimmed:
        raise TitleRequiredError("Title is required — give this BRD a name.")
    if requestor_directorate is not None and requestor_directorate not in DIRECTORATE_OPTIONS:
        raise InvalidChoiceDataError("Invalid requestor directorate.")
    if any(stakeholder not in DIRECTORATE_OPTIONS for stakeholder in (impacted_stakeholders or [])):
        raise InvalidChoiceDataError("Invalid impacted stakeholder.")

    conversation = Conversation(
        user_id=user_id,
        title=trimmed,
        context=context,
        requestor_directorate=requestor_directorate,
        impacted_stakeholders=impacted_stakeholders or [],
        group_id=group_id,
    )
    await conversation_repository.insert(session, conversation)
    await _seed_template_and_general(session, conversation.conversation_id)
    return conversation


async def list_for_user(session: AsyncSession, user_id: str) -> list[dict]:
    owned = await conversation_repository.list_by_user(session, user_id)
    # BRDs shared directly with this user (existing per-BRD collaborators)
    shared = await collaborator_repository.list_conversations_for_user(session, user_id)
    # BRDs accessible via group membership
    group_pairs = await group_collaborator_repository.list_groups_for_user(session, user_id)
    group_ids_with_role = {gc.group_id: gc.role for _, gc in group_pairs}

    from app.repositories import conversation_repository as _cr
    group_shared_convs: list[Conversation] = []
    if group_ids_with_role:
        group_shared_convs = await _cr.list_by_group_ids(session, list(group_ids_with_role.keys()))
    # Exclude BRDs the user owns (already in `owned`) from group-shared list
    owned_ids = {c.conversation_id for c in owned}
    # Also exclude BRDs already covered by direct sharing
    direct_shared_ids = {c.conversation_id for c, _ in shared}
    group_shared_convs = [
        c for c in group_shared_convs
        if c.conversation_id not in owned_ids and c.conversation_id not in direct_shared_ids
    ]

    # Batch-fetch answered counts
    all_ids = (
        [c.conversation_id for c in owned]
        + [c.conversation_id for c, _ in shared]
        + [c.conversation_id for c in group_shared_convs]
    )
    counts = await conversation_repository.answered_counts_for_conversations(session, all_ids)

    # Batch-fetch owner users for shared + group-shared conversations
    owner_ids = list(
        {c.user_id for c, _ in shared} | {c.user_id for c in group_shared_convs}
    )
    owners_by_id: dict[str, object] = {}
    if owner_ids:
        for owner in await user_repository.find_many_by_ids(session, owner_ids):
            owners_by_id[owner.user_id] = owner

    items = []
    for c in owned:
        items.append(
            {
                "id": c.conversation_id,
                "title": c.title,
                "updated_at": c.updated_at,
                "answered_count": counts.get(c.conversation_id, 0),
                "role": "owner",
                "owner_name": None,
                "owner_email": None,
                "group_id": c.group_id,
            }
        )
    for c, collab in shared:
        owner = owners_by_id.get(c.user_id)
        items.append(
            {
                "id": c.conversation_id,
                "title": c.title,
                "updated_at": c.updated_at,
                "answered_count": counts.get(c.conversation_id, 0),
                "role": collab.role,
                "owner_name": owner.name if owner else None,
                "owner_email": owner.email if owner else None,
                "group_id": c.group_id,
            }
        )
    for c in group_shared_convs:
        owner = owners_by_id.get(c.user_id)
        # The user's effective role on the BRD is the group's role
        role = group_ids_with_role.get(c.group_id, "viewer")
        items.append(
            {
                "id": c.conversation_id,
                "title": c.title,
                "updated_at": c.updated_at,
                "answered_count": counts.get(c.conversation_id, 0),
                "role": role,
                "owner_name": owner.name if owner else None,
                "owner_email": owner.email if owner else None,
                "group_id": c.group_id,
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
    """Owner-or-collaborator gate, with a minimum required role. Also checks
    group-level access (Google Drive folder sharing semantics)."""
    conversation = await conversation_repository.find_by_id(session, conversation_id)
    if conversation is None:
        raise NotFoundError("Conversation not found.")

    if conversation.user_id == user_id:
        role = "owner"
    else:
        # Check direct BRD collaborator first
        collaborator = await collaborator_repository.find_by_conversation_and_user(session, conversation_id, user_id)
        if collaborator is not None:
            role = collaborator.role
        elif conversation.group_id is not None:
            # Fall back to group-level access
            gc = await group_collaborator_repository.find_by_group_and_user(
                session, conversation.group_id, user_id
            )
            if gc is not None:
                role = gc.role
            else:
                raise NotFoundError("Conversation not found.")
        else:
            raise NotFoundError("Conversation not found.")

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
    # recompute() runs the flagged detection query once — reuse its result.
    # flagged_ids maps section_id (not wire key) for the answers_dict lookup below.
    # We derive it by re-running find_flagged_section_ids... but that would be two
    # queries again. Instead, build section_id→wire_key mapping and invert.
    flagged_items = await review_service.recompute(session, conversation_id)
    # Build flagged_section_ids from flagged_items by reverse-mapping field_id → section_id
    wire_key_to_section_id = {_wire_key(s): s.section_id for s in sections}
    flagged_ids = {wire_key_to_section_id[item["field_id"]] for item in flagged_items if item["field_id"] in wire_key_to_section_id}

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
            "choice_data": answer.choice_data,
            "confidence_breakdown": answer.confidence_breakdown,
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
    # flagged_items already computed above — no second query needed
    answered_count = await conversation_repository.answered_count(session, conversation_id)

    focused_section = by_id.get(conversation.focused_section_id) if conversation.focused_section_id else None
    focused_field_id = _wire_key(focused_section) if focused_section else None

    return {
        "id": conversation.conversation_id,
        "title": conversation.title,
        "requestor_directorate": conversation.requestor_directorate,
        "impacted_stakeholders": conversation.impacted_stakeholders or [],
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
