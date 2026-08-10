"""DUMMY AI — placeholder only, centralized on purpose.

Nothing in this file is real intelligence. It exists so `chat_service.py`
has something to call today, with a return shape rich enough that the
*rest* of the pipeline (Answer updates, status transitions, flagged
detection, the frontend's DonutBadge/missing-items/assumption-pill
rendering) can be built and verified for real right now, without waiting
on the AI team's integration. When that's ready, they replace this
file's internals (`get_reply`'s body — the deterministic placeholder
math below) with a real model call; the signature is the actual
contract other code is written against and is expected to stay stable
(or change deliberately, in coordination) — see
`../../../implementation_spin2.md` §1.2 for the fuller writeup of this
seam.

Search the codebase for "DUMMY_AI" to find every place this is used.
"""

from dataclasses import dataclass, field


@dataclass
class AgentReply:
    reply_text: str
    answer_text: str | None = None
    completeness: int | None = None
    confidence: int | None = None
    missing_items: list[str] = field(default_factory=list)
    is_assumption: bool = False


DUMMY_AI_REPLY = "Got it — logged. What else can you tell me about this?"
DUMMY_MISSING_ITEM = "More detail needed before this can be marked complete."


async def get_reply(
    *,
    room_title: str,  # noqa: ARG001 — unused by the dummy; real logic will want it
    room_purpose: str | None,  # noqa: ARG001
    message_text: str,
    history: list[dict],
    current_answer: dict | None,
) -> AgentReply:
    """DUMMY_AI: deterministic placeholder — no actual model call.

    `completeness` climbs a fixed amount per turn (based on how many
    prior messages already exist in this room) purely so the downstream
    pipeline has *something* real to react to: watch a leaf's status
    actually reach 'done', watch flagged detection actually trigger,
    watch the frontend's donut/missing-items panel actually change
    between messages. The exact numbers are meaningless — real
    completeness/confidence is the AI team's job, not this file's.

    `answer_text` is simply the running concatenation of every user
    message sent in this room — a placeholder for "the AI would
    normally synthesize this," not synthesis itself.
    """
    turns_so_far = len(history) // 2 + 1
    completeness = min(100, turns_so_far * 34)
    confidence = min(90, 55 + turns_so_far * 12)
    missing_items = [] if completeness >= 100 else [DUMMY_MISSING_ITEM]

    previous_answer_text = (current_answer or {}).get("answer_text") or ""
    answer_text = f"{previous_answer_text} {message_text}".strip()

    return AgentReply(
        reply_text=DUMMY_AI_REPLY,
        answer_text=answer_text,
        completeness=completeness,
        confidence=confidence,
        missing_items=missing_items,
        is_assumption=False,
    )
