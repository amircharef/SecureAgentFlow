"""Attack simulations for security evaluation."""

from attacks.models import AttackResult
from attacks.scenarios import (
    compromised_agent,
    impersonation,
    message_tampering,
    privilege_escalation,
    prompt_injection,
    replay,
)

__all__ = [
    "AttackResult",
    "compromised_agent",
    "impersonation",
    "message_tampering",
    "privilege_escalation",
    "prompt_injection",
    "replay",
]
