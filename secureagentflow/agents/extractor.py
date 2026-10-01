"""Fact extraction agent for the synthetic clinical document format."""

import re
from typing import Any

from secureagentflow.agents.base import Agent, AgentContext


class ExtractorAgent(Agent):
    """Extract explicitly formatted facts from a synthetic document."""

    _FACT_PATTERN = re.compile(
        r"(?P<key>age|sex|hemoglobin|glucose|creatinine)\s*[:=]\s*"
        r"(?P<value>[A-Za-z]+|[-+]?\d+(?:\.\d+)?)",
        re.IGNORECASE,
    )

    def extract(self, document_text: str, context: AgentContext) -> dict[str, Any]:
        """Return normalized key-value facts found in ``document_text``."""
        self.call_llm(
            f"Extract key facts from this clinical document:\n{document_text}", context
        )
        facts: dict[str, Any] = {}
        for match in self._FACT_PATTERN.finditer(document_text):
            key = match.group("key").lower()
            value = match.group("value")
            if key in {"age", "hemoglobin", "glucose", "creatinine"}:
                facts[key] = float(value) if "." in value else int(value)
            else:
                facts[key] = value.lower()
        return facts
