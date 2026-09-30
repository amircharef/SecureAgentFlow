"""Common agent contract for the baseline workflow."""

from dataclasses import dataclass
from typing import Any

from secureagentflow.llm import LLMClient


@dataclass(slots=True)
class AgentContext:
    """Execution context shared by agents during one task."""

    trace_id: str
    tokens_used: int = 0

    def record(self, tokens_used: int) -> None:
        """Accumulate provider-reported token usage."""
        self.tokens_used += tokens_used


class Agent:
    """Base class for an agent with an explicit identity and LLM client."""

    def __init__(self, name: str, llm: LLMClient) -> None:
        self.name = name
        self.llm = llm

    def call_llm(self, prompt: str, context: AgentContext) -> str:
        """Call the configured model and record its token usage."""
        response = self.llm.generate(prompt)
        context.record(response.tokens_used)
        return response.text

    def message(
        self,
        context: AgentContext,
        receiver: str,
        message_type: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Create the baseline message payload used by the orchestrator."""
        return {
            "trace_id": context.trace_id,
            "sender": self.name,
            "receiver": receiver,
            "type": message_type,
            "payload": payload,
        }
