"""DUMMY AI — placeholder only, centralized on purpose.

Nothing in this file is real. It exists so `chat_service.py` and
`document_service.py` (once it needs live drafting help) have something
to call today, without the rest of the backend waiting on the AI team's
integration. When that's ready, replace `get_reply` below with a real
call and delete `DUMMY_AI_REPLY` — every dependency on the stub lives
in this one file, nothing else needs to change.

Search the codebase for "DUMMY_AI" to find every place this is used.
"""

DUMMY_AI_REPLY = "Got it — logged. What else can you tell me about this?"


async def get_reply(*, room_title: str, message_text: str) -> str:  # noqa: ARG001 — signature is the real interface, args unused only because this is a stub
    """DUMMY_AI: fixed placeholder reply, no actual model call.

    Real implementation (prompt assembly, model call, draft/answer
    merge) is the AI team's job — see backend/implementation_1.md's
    "AI integration boundary" section. This function's *signature* is
    the actual contract other services code against; only this body is
    throwaway.
    """
    return DUMMY_AI_REPLY
