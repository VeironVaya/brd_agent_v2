"""
app/rag/llm_client.py
=====================
Thin LLM Invocation Layer for Standalone Evaluation & Testing.
"""

from __future__ import annotations

import json
import os
from typing import Callable, Protocol


class LLMClient(Protocol):
    """Protocol definition for thin LLM invocation layer."""

    def generate(self, prompt: str, system_instruction: str | None = None) -> str:
        ...


class FakeLLMClient:
    """
    Deterministic stub LLM client for testing and offline execution.
    Does NOT make live network API calls.
    """

    def __init__(
        self,
        canned_response: str | None = None,
        field_responses: dict[str, str] | None = None,
        generator_fn: Callable[[str, str | None], str] | None = None,
    ) -> None:
        self.canned_response = canned_response
        self.field_responses = field_responses or {}
        self.generator_fn = generator_fn
        self.calls: list[dict[str, str | None]] = []

    def generate(self, prompt: str, system_instruction: str | None = None) -> str:
        self.calls.append({"prompt": prompt, "system_instruction": system_instruction})

        if self.generator_fn:
            return self.generator_fn(prompt, system_instruction)

        for fid, resp in self.field_responses.items():
            if f"TARGET SECTION: [{fid}]" in prompt or f"Section {fid}" in prompt:
                return resp

        if self.canned_response is not None:
            return self.canned_response

        return json.dumps({
            "requirements": [
                {
                    "text": "The system shall support the specified project requirements.",
                    "evidence_ids": ["C1"],
                    "grounding_reference_ids": ["R1"]
                }
            ],
            "unresolved_gap_ids": []
        })


def get_default_llm_client(fallback_fake: bool = True) -> LLMClient:
    return FakeLLMClient()
