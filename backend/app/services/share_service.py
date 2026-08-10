"""Collaborator management — strictly owner-only (add/list/update/remove),
matching custom_section_service's shape: every function starts with an
ownership gate via conversation_service.get_owned before touching
anything. Sharing targets an existing registered user found by email —
no invite-for-unregistered-email flow."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AlreadySharedError, CannotShareWithSelfError, InvalidRoleError, NotFoundError
from app.models.collaborator import Collaborator
from app.repositories import collaborator_repository, user_repository
from app.services import conversation_service

VALID_ROLES = {"editor", "viewer"}


def _dto(collaborator: Collaborator, email: str, name: str) -> dict:
    return {
        "id": collaborator.collaborator_id,
        "user_id": collaborator.user_id,
        "email": email,
        "name": name,
        "role": collaborator.role,
    }


async def add_collaborator(
    session: AsyncSession, *, conversation_id: str, owner_user_id: str, email: str, role: str
) -> dict:
    await conversation_service.get_owned(session, conversation_id, owner_user_id)

    if role not in VALID_ROLES:
        raise InvalidRoleError(f"Role must be one of {sorted(VALID_ROLES)}.")

    target = await user_repository.find_by_email(session, email)
    if target is None:
        raise NotFoundError("No account with that email exists.")

    if target.user_id == owner_user_id:
        raise CannotShareWithSelfError("You already own this conversation.")

    existing = await collaborator_repository.find_by_conversation_and_user(session, conversation_id, target.user_id)
    if existing is not None:
        raise AlreadySharedError("This person already has access — update their role instead.")

    collaborator = Collaborator(conversation_id=conversation_id, user_id=target.user_id, role=role)
    await collaborator_repository.insert(session, collaborator)
    return _dto(collaborator, target.email, target.name)


async def list_collaborators(session: AsyncSession, *, conversation_id: str, owner_user_id: str) -> list[dict]:
    await conversation_service.get_owned(session, conversation_id, owner_user_id)
    collaborators = await collaborator_repository.list_by_conversation(session, conversation_id)

    items = []
    for collaborator in collaborators:
        user = await user_repository.find_by_id(session, collaborator.user_id)
        if user is None:
            continue
        items.append(_dto(collaborator, user.email, user.name))
    return items


async def _find_owned_collaborator(
    session: AsyncSession, conversation_id: str, owner_user_id: str, collaborator_id: str
) -> Collaborator:
    await conversation_service.get_owned(session, conversation_id, owner_user_id)
    collaborator = await collaborator_repository.find_by_id(session, collaborator_id)
    if collaborator is None or collaborator.conversation_id != conversation_id:
        raise NotFoundError("Collaborator not found.")
    return collaborator


async def update_role(
    session: AsyncSession, *, conversation_id: str, owner_user_id: str, collaborator_id: str, role: str
) -> dict:
    if role not in VALID_ROLES:
        raise InvalidRoleError(f"Role must be one of {sorted(VALID_ROLES)}.")
    collaborator = await _find_owned_collaborator(session, conversation_id, owner_user_id, collaborator_id)
    await collaborator_repository.update_role(session, collaborator, role)
    user = await user_repository.find_by_id(session, collaborator.user_id)
    return _dto(collaborator, user.email, user.name)


async def remove_collaborator(
    session: AsyncSession, *, conversation_id: str, owner_user_id: str, collaborator_id: str
) -> None:
    collaborator = await _find_owned_collaborator(session, conversation_id, owner_user_id, collaborator_id)
    await collaborator_repository.delete(session, collaborator)
