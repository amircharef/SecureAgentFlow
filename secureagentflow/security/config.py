"""Independent security-defense configuration."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class SecurityConfig:
    """Toggle each defense independently for ablation experiments."""

    d1_identity: bool = False
    d2_replay: bool = False
    d3_permissions: bool = False
    d4_sanitization: bool = False
    d5_trust: bool = False
    d6_audit: bool = False
    timestamp_window_seconds: float = 300.0
    trust_threshold: float = 0.5
    audit_path: Path | None = None

    @classmethod
    def baseline(cls) -> "SecurityConfig":
        """Return C0 with every defense disabled."""
        return cls()

    @classmethod
    def full_stack(cls, audit_path: Path | None = None) -> "SecurityConfig":
        """Return C4 with every defense enabled."""
        return cls(
            d1_identity=True,
            d2_replay=True,
            d3_permissions=True,
            d4_sanitization=True,
            d5_trust=True,
            d6_audit=True,
            audit_path=audit_path,
        )
