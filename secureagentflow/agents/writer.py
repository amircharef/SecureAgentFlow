"""Structured summary writer agent."""

import json
from typing import Any

from secureagentflow.agents.base import Agent, AgentContext


class WriterAgent(Agent):
    """Write a compact JSON summary from facts and risk flags."""

    def write(
        self,
        facts: dict[str, Any],
        risk_flags: list[str],
        context: AgentContext,
    ) -> str:
        """Return a deterministic structured summary string."""
        self.call_llm(
            f"Write a structured summary from facts={facts} and flags={risk_flags}",
            context,
        )
        return json.dumps(
            {"key_facts": facts, "risk_flags": risk_flags},
            sort_keys=True,
        )
