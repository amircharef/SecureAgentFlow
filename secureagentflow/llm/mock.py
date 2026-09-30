"""Deterministic, rule-based LLM implementation for tests and experiments."""

from typing import Any

from secureagentflow.llm.base import LLMClient, LLMResponse


class MockLLM(LLMClient):
    """Return deterministic responses without requiring network access or a key."""

    def __init__(self, model: str = "mock-v1") -> None:
        self.model = model

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Generate a stable response based on the requested operation."""
        del kwargs
        normalized_prompt = prompt.strip().lower()
        if "extract" in normalized_prompt:
            text = '{"facts": [], "source": "mock"}'
        elif "risk" in normalized_prompt or "flag" in normalized_prompt:
            text = '{"risk_flags": [], "source": "mock"}'
        elif "verify" in normalized_prompt:
            text = '{"accepted": true, "reason": "mock verification"}'
        else:
            text = '{"summary": "Deterministic mock response"}'
        return LLMResponse(text=text, tokens_used=len(text.split()), model=self.model)
