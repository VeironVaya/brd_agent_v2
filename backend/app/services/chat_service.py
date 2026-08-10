"""postMessage — inserts Bubble rows, updates the conversation's
focused_section_id/updated_at. The agent reply is DUMMY_AI (see
ai_integration.py) until the AI team's integration lands; this service
does NOT touch ANSWER content/answered_at on a dummy reply — bumping
those on fabricated content would mark real progress that never
happened. Wire that up once real replies produce real answer updates.
"""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.bubble import Bubble
from app.models.section import Section
from app.repositories import bubble_repository, conversation_repository, section_repository
from app.services import ai_integration, conversation_service, template_service


async def _resolve_room_section(session: AsyncSession, conversation_id: str, room_id: str) -> Section:
    sections = await section_repository.list_by_conversation(session, conversation_id)
    if room_id == template_service.GENERAL_ROOM_ID:
        match = next((s for s in sections if s.is_general), None)
    else:
        match = next(
            (s for s in sections if (s.template_key == room_id) or (s.is_custom and s.section_id == room_id)),
            None,
        )
    if match is None:
        raise NotFoundError(f"Room {room_id!r} not found.")
    return match


async def post_message(
    session: AsyncSession, *, conversation_id: str, user_id: str, room_id: str, text: str
) -> list[dict]:
    conversation = await conversation_service.get_owned(session, conversation_id, user_id)
    section = await _resolve_room_section(session, conversation_id, room_id)

    # created_at set explicitly here, not left to the column's
    # server_default=func.now() — both inserts happen in the same DB
    # transaction, and Postgres's now() is transaction-scoped, so the
    # user and agent bubble would otherwise get an *identical* timestamp.
    # With no tiebreaker, ORDER BY created_at can then return a pair in
    # either order — observed in practice as a reply appearing to sort
    # before its own message. datetime.now() per statement guarantees
    # real, monotonically increasing wall-clock values instead.
    user_bubble = Bubble(section_id=section.section_id, role="user", text=text, created_at=datetime.now(timezone.utc))
    await bubble_repository.insert(session, user_bubble)

    reply_text = await ai_integration.get_reply(room_title=section.title, message_text=text)
    agent_bubble = Bubble(
        section_id=section.section_id, role="agent", text=reply_text, created_at=datetime.now(timezone.utc)
    )
    await bubble_repository.insert(session, agent_bubble)

    if not section.is_general:
        conversation.focused_section_id = section.section_id
    await conversation_repository.touch_updated_at(session, conversation)

    return [
        {"id": user_bubble.bubble_id, "role": user_bubble.role, "text": user_bubble.text},
        {"id": agent_bubble.bubble_id, "role": agent_bubble.role, "text": agent_bubble.text},
    ]
