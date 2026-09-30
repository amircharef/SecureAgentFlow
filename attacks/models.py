"""Models shared by simulated attack scenarios."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class AttackResult:
    """Outcome of one attack attempt at a configured trust boundary."""

    attack_id: str
    detected: bool
    attack_succeeded: bool
    events: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
