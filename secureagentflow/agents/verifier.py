"""Verifier agent for consistency checks."""

import json
from typing import Any

from secureagentflow.agents.base import Agent, AgentContext


class VerifierAgent(Agent):
    """Check that output facts, flags, and summary match the source document."""

    def verify(
        self,
        document_text: str,
        expected_facts: dict[str, Any],
        expected_flags: list[str],
        extracted_facts: dict[str, Any],
        risk_flags: list[str],
        summary: str,
        context: AgentContext,
    ) -> bool:
        """Return true only when all structured workflow outputs are consistent."""
        self.call_llm(
            f"Verify this summary against the source:\n{document_text}", context
        )
        try:
            summary_data = json.loads(summary)
        except json.JSONDecodeError:
            return False
        return (
            extracted_facts == expected_facts
            and sorted(risk_flags) == sorted(expected_flags)
            and summary_data
            == {"key_facts": expected_facts, "risk_flags": expected_flags}
        )
