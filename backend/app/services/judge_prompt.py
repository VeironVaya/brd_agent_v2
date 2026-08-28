"""Backward-compatibility re-export for app.ai.judge.prompt.

Agent 2 prompts now live in `app.ai.judge.prompt`.
This module is retained for backward compatibility.
"""

from app.ai.judge.prompt import (
    JUDGE_STAGE_A_PROMPT,
    JUDGE_STAGE_B_PROMPT,
    build_stage_a_context,
    build_stage_b_context,
)

__all__ = [
    "JUDGE_STAGE_A_PROMPT",
    "JUDGE_STAGE_B_PROMPT",
    "build_stage_a_context",
    "build_stage_b_context",
]
