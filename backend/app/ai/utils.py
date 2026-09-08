"""app/ai/utils.py
=================
Shared AI utilities for robust LLM response parsing and prompt sanitization.
"""

from __future__ import annotations

import json
import re
from typing import Any


def parse_llm_json(raw_text: str | None) -> Any:
    """Robustly extracts and parses JSON from LLM text responses.

    Handles:
    - Markdown code fences (```json ... ``` or ``` ... ```)
    - Conversational preambles or postscripts around the JSON payload
    - Leading/trailing whitespace
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Empty LLM response cannot be parsed as JSON.")

    text = raw_text.strip()

    # If wrapped in markdown fences, extract the block
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fence_match:
        text = fence_match.group(1).strip()

    # Direct JSON parse attempt
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find the outermost JSON object {...} or array [...]
    first_brace = text.find("{")
    last_brace = text.rfind("}")

    first_bracket = text.find("[")
    last_bracket = text.rfind("]")

    # Decide whether object or array appears first
    candidates: list[str] = []

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidates.append(text[first_brace : last_brace + 1])

    if first_bracket != -1 and last_bracket != -1 and last_bracket > first_bracket:
        candidates.append(text[first_bracket : last_bracket + 1])

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    # Clean non-printable control characters and try again
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Failed to parse LLM response as valid JSON: {exc}\nRaw preview: {raw_text[:200]}"
        ) from exc


def sanitize_prompt_input(text: str | None) -> str:
    """Sanitizes external / untrusted user input before injection into LLM prompts.

    Protects against:
    1. XML/HTML closing tag injection (e.g. </draft_content>, </confirmed_project_evidence>)
       that attempt to break out of data containment boundaries.
    2. Prompt directive hijacking tags (e.g. <system_instructions>, <admin_override>).
    3. Legacy delimiter hijacking patterns (e.g. --- END EVIDENCE ---, === END ===).
    4. Null bytes and unprintable control characters.
    """
    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

    if not text:
        return ""

    # Strip null bytes
    sanitized = text.replace("\x00", "")

    # Neutralize XML closing tags: </tag_name> -> [escaped-closing-tag: tag_name]
    sanitized = re.sub(
        r"</([a-zA-Z0-9_\-]+)>",
        r"[escaped-closing-tag: \1]",
        sanitized,
    )

    # Neutralize dangerous opening directive tags: <system_instructions>, <admin_override>, etc.
    dangerous_tags = (
        r"(?:system_instructions|system|instruction|admin_override|developer_mode|"
        r"prompt|directive|override|ignore_previous|root|jailbreak)"
    )
    sanitized = re.sub(
        rf"<({dangerous_tags}[^>]*)>",
        r"[escaped-tag: \1]",
        sanitized,
        flags=re.IGNORECASE,
    )

    # Neutralize legacy delimiter hijacking patterns
    # e.g., --- END EVIDENCE ---, --- END GENERATED CONTENT ---, === SECTION ===
    sanitized = re.sub(
        r"(-{3,}|={3,})\s*(END[_\s]+[A-Z0-9_\s]+)\s*(-{3,}|={3,})",
        r"[escaped-delimiter: \2]",
        sanitized,
        flags=re.IGNORECASE,
    )

    return sanitized

