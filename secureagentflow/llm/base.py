"""Abstract language-model client contract."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class LLMResponse:
    """The normalized result returned by an LLM client."""

    text: str
    tokens_used: int
    model: str


class LLMClient(ABC):
    """Interface used by agents without coupling them to an LLM provider."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Generate a response for ``prompt``."""
        raise NotImplementedError
