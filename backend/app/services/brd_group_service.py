"""Business logic for BRD group management.

Groups work like Google Drive folders:
  - Owner can create, rename, delete, and share groups.
  - Collaborators (editor/viewer) can see the group and all BRDs inside it.
  - Assigning a BRD to a group is allowed for the group owner or any editor.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    AlreadySharedError,
    CannotShareWithSelfError,
    ForbiddenError,
    InvalidRoleError,
    NotFoundError,
    TitleRequiredError,
)
from app.models.brd_group import BrdGroup
from app.models.group_collaborator import GroupCollaborator
from app.repositories import brd_group_repository, group_collaborator_repository, user_repository
from app.utils.ids import new_id

ROLE_RANK = {"viewer": 0, "editor": 1, "owner": 2}
VALID_ROLES = {"editor", "viewer"}


# ── Access gates ──────────────────────────────────────────────────────────────

async def get_owned(
    session: AsyncSession, group_id: str, user_id: str
) -> BrdGroup:
    """Owner-only gate — for edit/delete/share operations."""
    group = await brd_group_repository.find_by_id_for_user(session, group_id, user_id)
    if group is None:
        raise NotFoundError("Group not found.")
    return group


async def get_accessible(
    session: AsyncSession, group_id: str, user_id: str, *, min_role: str = "viewer"
) -> tuple[BrdGroup, str]:
    """Owner-or-collaborator gate. Returns (group, effective_role)."""
    group = await brd_group_repository.find_by_id(session, group_id)
    if group is None:
        raise NotFoundError("Group not found.")

    if group.user_id == user_id:
        role = "owner"
    else:
        gc = await group_collaborator_repository.find_by_group_and_user(session, group_id, user_id)
        if gc is None:
            raise NotFoundError("Group not found.")
        role = gc.role

    if ROLE_RANK[role] < ROLE_RANK[min_role]:
        raise ForbiddenError("You don't have permission to do that.")

    return group, role


# ── Group CRUD ────────────────────────────────────────────────────────────────

async def create(
    session: AsyncSession,
    *,
    user_id: str,
    title: str,
    description: str | None,
) -> BrdGroup:
    trimmed = title.strip()
    if not trimmed:
        raise TitleRequiredError("Group title is required.")
    group = BrdGroup(
        group_id=new_id(),
        user_id=user_id,
        title=trimmed,
        description=description,
    )
    return await brd_group_repository.insert(session, group)


async def list_for_user(session: AsyncSession, user_id: str) -> list[dict]:
    """Returns owned groups + groups shared with this user, with role included."""
    owned = await brd_group_repository.list_by_user(session, user_id)
    shared_pairs = await group_collaborator_repository.list_groups_for_user(session, user_id)

    items: list[dict] = []
    for g in owned:
        items.append(_group_to_dict(g, role="owner"))
    for g, gc in shared_pairs:
        items.append(_group_to_dict(g, role=gc.role))
    return items


def _group_to_dict(group: BrdGroup, *, role: str) -> dict:
    return {
        "group_id": group.group_id,
        "user_id": group.user_id,
        "title": group.title,
        "description": group.description,
        "created_at": group.created_at,
        "role": role,
    }


async def update(
    session: AsyncSession,
    *,
    group_id: str,
    user_id: str,
    title: str,
    description: str | None,
) -> BrdGroup:
    group = await get_owned(session, group_id, user_id)
    trimmed = title.strip()
    if not trimmed:
        raise TitleRequiredError("Group title is required.")
    return await brd_group_repository.update(session, group, trimmed, description)


async def delete(session: AsyncSession, *, group_id: str, user_id: str) -> None:
    group = await get_owned(session, group_id, user_id)
    # DB FK (ondelete=SET NULL) nullifies group_id on all conversations in this group.
    await brd_group_repository.delete(session, group)


async def assign_group(
    session: AsyncSession,
    *,
    conversation_id: str,
    user_id: str,
    group_id: str | None,
) -> None:
    """Assign or unassign a BRD to/from a group.
    Caller must own the BRD. Target group must be accessible (owner or editor)."""
    from app.services import conversation_service
    conversation = await conversation_service.get_owned(session, conversation_id, user_id)

    if group_id is not None:
        # Editor-or-owner on the group is sufficient (like moving a file into a shared folder)
        await get_accessible(session, group_id, user_id, min_role="editor")

    conversation.group_id = group_id
    await session.flush()


# ── Group sharing ─────────────────────────────────────────────────────────────

async def add_collaborator(
    session: AsyncSession,
    *,
    group_id: str,
    owner_user_id: str,
    email: str,
    role: str,
) -> dict:
    """Owner-only: invite a user to a group by email."""
    if role not in VALID_ROLES:
        raise InvalidRoleError(f"Role must be one of: {', '.join(VALID_ROLES)}")

    group = await get_owned(session, group_id, owner_user_id)

    target = await user_repository.find_by_email(session, email)
    if target is None:
        raise NotFoundError("No account with that email exists.")
    if target.user_id == owner_user_id:
        raise CannotShareWithSelfError("You already own this group.")

    existing = await group_collaborator_repository.find_by_group_and_user(session, group_id, target.user_id)
    if existing is not None:
        raise AlreadySharedError("This person already has access — change their role below instead.")

    gc = GroupCollaborator(
        group_collaborator_id=new_id(),
        group_id=group.group_id,
        user_id=target.user_id,
        role=role,
    )
    gc = await group_collaborator_repository.insert(session, gc)
    return _collaborator_to_dict(gc, target)


async def list_collaborators(
    session: AsyncSession, *, group_id: str, owner_user_id: str
) -> list[dict]:
    await get_owned(session, group_id, owner_user_id)
    pairs = await group_collaborator_repository.list_with_user_details(session, group_id)
    return [_collaborator_to_dict(gc, user) for gc, user in pairs]


async def update_collaborator_role(
    session: AsyncSession,
    *,
    group_id: str,
    owner_user_id: str,
    collaborator_id: str,
    role: str,
) -> dict:
    if role not in VALID_ROLES:
        raise InvalidRoleError(f"Role must be one of: {', '.join(VALID_ROLES)}")
    await get_owned(session, group_id, owner_user_id)
    gc = await group_collaborator_repository.find_by_id(session, collaborator_id)
    if gc is None or gc.group_id != group_id:
        raise NotFoundError("Collaborator not found.")
    target = await user_repository.find_by_id(session, gc.user_id)
    gc = await group_collaborator_repository.update_role(session, gc, role)
    return _collaborator_to_dict(gc, target)


async def remove_collaborator(
    session: AsyncSession,
    *,
    group_id: str,
    owner_user_id: str,
    collaborator_id: str,
) -> None:
    await get_owned(session, group_id, owner_user_id)
    gc = await group_collaborator_repository.find_by_id(session, collaborator_id)
    if gc is None or gc.group_id != group_id:
        raise NotFoundError("Collaborator not found.")
    await group_collaborator_repository.delete(session, gc)


def _collaborator_to_dict(gc: GroupCollaborator, user) -> dict:
    return {
        "id": gc.group_collaborator_id,
        "user_id": gc.user_id,
        "email": user.email,
        "name": user.name,
        "role": gc.role,
    }
