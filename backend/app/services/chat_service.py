"""postMessage — inserts Bubble rows, updates the conversation's
focused_section_id/updated_at, and persists whatever ANSWER update the
AI reply produced (still DUMMY_AI's placeholder numbers today — see
ai_integration.py — but the persistence pipeline itself is real: a leaf
can genuinely reach 'done', flagged detection downstream genuinely
fires). Never touches ANSWER for a non-leaf room (General chat, a
template header) — erd.md's ANSWER is strictly 1:1 with a leaf SECTION.
"""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.bubble import Bubble
from app.models.section import Section
from app.repositories import answer_repository, bubble_repository, conversation_repository, section_repository
from app.repositories import answer_repository, bubble_repository, conversation_repository, section_repository
from app.services import ai_integration, conversation_service, template_service


def _derive_status(completeness: int | None, previous_status: str | None) -> str:
    """completeness -> status is a backend rule, not something the AI
    dictates (implementation_spin2.md §1.2/§2.1) — 'locked'/'review' stay
    entirely driven by SECTION_DEPENDENCY/flagged logic elsewhere and are
    never set from here."""
    if completeness is None:
        return previous_status or "ready"
    return "done" if completeness >= 100 else "progress"


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
    conversation, _role = await conversation_service.get_accessible(
        session, conversation_id, user_id, min_role="editor"
    )
    section = await _resolve_room_section(session, conversation_id, room_id)

    # Gathered BEFORE inserting this turn's user bubble, so "history" is
    # unambiguously "everything before this message" — the new message
    # itself is passed separately as message_text, never duplicated into
    # history too.
    history = await bubble_repository.list_by_section(session, section.section_id)
    existing_answer = await answer_repository.find_by_section_id(session, section.section_id)
    current_answer = (
        {
            "answer_text": existing_answer.answer_text,
            "completeness": existing_answer.completeness,
            "confidence": existing_answer.confidence,
            "missing_items": existing_answer.missing_items,
        }
        if existing_answer
        else None
    )

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

    # Build context answers mapping for true context forwarding
    all_sections = await section_repository.list_by_conversation(session, conversation_id)
    all_answers = await answer_repository.list_by_conversation(session, conversation_id)
    context_answers = {}
    for ans in all_answers:
        ans_sec = next((s for s in all_sections if s.section_id == ans.section_id), None)
        if ans_sec and ans.answer_text:
            ans_room_id = ans_sec.template_key or ans_sec.section_id
            context_answers[ans_room_id] = ans.answer_text

    reply = await ai_integration.get_reply(
        room_id=section.template_key or section.section_id,
        room_title=section.title,
        room_purpose=section.purpose,
        message_text=text,
        history=[{"role": b.role, "text": b.text} for b in history],
        current_answer=current_answer,
        context_answers=context_answers,
    )

    agent_bubble = Bubble(
        section_id=section.section_id,
        role="assumption" if reply.is_assumption else "agent",
        text=reply.reply_text,
        created_at=datetime.now(timezone.utc),
    )
    await bubble_repository.insert(session, agent_bubble)

    # Only a leaf ever gets an ANSWER row (erd.md) — General chat and
    # template headers are never resolvable as is_leaf=True rooms in
    # practice, but this guard is the actual invariant, not an assumption
    # about which room ids happen to reach here.
    if section.is_leaf:
        status = _derive_status(reply.completeness, existing_answer.status if existing_answer else None)
        await answer_repository.upsert(
            session,
            section.section_id,
            status=status,
            completeness=reply.completeness,
            confidence=reply.confidence,
            answer_text=reply.answer_text,
            missing_items=reply.missing_items,
            confidence_breakdown=reply.confidence_breakdown,
        )

    if not section.is_general:
        conversation.focused_section_id = section.section_id
    await conversation_repository.touch_updated_at(session, conversation)

    return [
        {"id": user_bubble.bubble_id, "role": user_bubble.role, "text": user_bubble.text},
        {"id": agent_bubble.bubble_id, "role": agent_bubble.role, "text": agent_bubble.text},
    ]
