"""Timestamp-window and nonce replay protection."""

from datetime import datetime, timezone

from secureagentflow.messaging import MessageEnvelope
from secureagentflow.security.exceptions import ReplayError


class ReplayGuard:
    """Reject stale messages and nonces that have already been accepted."""

    def __init__(self, timestamp_window_seconds: float = 300.0) -> None:
        self.timestamp_window_seconds = timestamp_window_seconds
        self._seen_nonces: set[str] = set()

    def check(self, envelope: MessageEnvelope, now: datetime | None = None) -> None:
        """Validate and record an envelope nonce."""
        current_time = now or datetime.now(timezone.utc)
        timestamp = envelope.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        age = abs((current_time - timestamp).total_seconds())
        if age > self.timestamp_window_seconds:
            raise ReplayError(f"Message timestamp outside window: {age:.3f}s")
        if envelope.nonce in self._seen_nonces:
            raise ReplayError(f"Message nonce already seen: {envelope.nonce}")
        self._seen_nonces.add(envelope.nonce)
