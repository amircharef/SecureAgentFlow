"""Prompt-injection detection and input quarantine."""

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SanitizationResult:
    """Sanitized text and detected instruction-like indicators."""

    text: str
    quarantined: bool
    events: list[str]


class InputSanitizer:
    """Treat retrieved documents as data and quarantine instruction-like text."""

    _PATTERNS = (
        re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions?", re.IGNORECASE),
        re.compile(r"system\s+prompt", re.IGNORECASE),
        re.compile(r"mark\s+the\s+patient\s+as", re.IGNORECASE),
        re.compile(r"call\s+(?:the\s+)?(?:tool|function)", re.IGNORECASE),
    )

    def sanitize(self, document_text: str) -> SanitizationResult:
        """Replace suspicious instruction-like spans with a quarantine marker."""
        sanitized = document_text
        events: list[str] = []
        for pattern in self._PATTERNS:
            if pattern.search(sanitized):
                events.append(f"suspicious_pattern:{pattern.pattern}")
                sanitized = pattern.sub("[QUARANTINED_INSTRUCTION]", sanitized)
        return SanitizationResult(
            text=sanitized,
            quarantined=bool(events),
            events=events,
        )
