"""Reputation scores updated by verifier outcomes."""

from secureagentflow.security.exceptions import PermissionDenied


class TrustManager:
    """Track bounded agent reputation and enforce a trust threshold."""

    def __init__(self, threshold: float = 0.5) -> None:
        self.threshold = threshold
        self._scores: dict[str, float] = {}

    def score(self, agent: str) -> float:
        """Return an agent score, defaulting to neutral trust."""
        return self._scores.get(agent, 1.0)

    def update(self, agent: str, accepted: bool) -> float:
        """Reward accepted output and penalize rejected output."""
        current = self.score(agent)
        updated = current + (0.1 if accepted else -0.25)
        self._scores[agent] = max(0.0, min(1.0, updated))
        return self._scores[agent]

    def require_trusted(self, agent: str) -> None:
        """Reject agents whose score is below the configured threshold."""
        if self.score(agent) < self.threshold:
            raise PermissionDenied(f"Agent below trust threshold: {agent}")
