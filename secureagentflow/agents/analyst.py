"""Risk analysis agent for extracted synthetic clinical facts."""

from typing import Any

from secureagentflow.agents.base import Agent, AgentContext


class AnalystAgent(Agent):
    """Derive transparent risk flags from extracted measurements."""

    def analyze(self, facts: dict[str, Any], context: AgentContext) -> list[str]:
        """Return stable risk flags using the synthetic task rules."""
        self.call_llm(f"Assess risk flags from these extracted facts: {facts}", context)
        flags: list[str] = []
        if float(facts.get("hemoglobin", 99)) < 10:
            flags.append("anemia")
        if float(facts.get("glucose", 0)) >= 140:
            flags.append("hyperglycemia")
        if float(facts.get("creatinine", 0)) > 1.3:
            flags.append("renal_impairment")
        return flags
