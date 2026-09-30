"""Provider-backed LLM implementation."""

import os
from typing import Any

from secureagentflow.llm.base import LLMClient, LLMResponse


class APILLM(LLMClient):
    """Call an OpenAI-compatible provider using a key from the environment."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key_env: str = "OPENAI_API_KEY",
    ) -> None:
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"Missing API key environment variable: {api_key_env}")
        from openai import OpenAI

        self.model = model
        self._client = OpenAI(api_key=api_key)

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Generate a response through the configured provider."""
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        choice = response.choices[0]
        text = choice.message.content or ""
        usage = response.usage
        tokens_used = usage.total_tokens if usage is not None else 0
        return LLMResponse(text=text, tokens_used=tokens_used, model=self.model)
