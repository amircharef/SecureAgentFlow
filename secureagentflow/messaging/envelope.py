"""Signed message envelope shared by all agents."""

import base64
import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from pydantic import BaseModel, ConfigDict, Field


class MessageEnvelope(BaseModel):
    """Transport contract for messages exchanged between agents."""

    model_config = ConfigDict(extra="forbid")

    msg_id: str = Field(default_factory=lambda: str(uuid4()))
    trace_id: str
    sender: str
    receiver: str
    type: str
    payload: dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    nonce: str = Field(default_factory=lambda: str(uuid4()))
    signature: str | None = None

    def canonical_bytes(self) -> bytes:
        """Serialize all signed fields deterministically, excluding the signature."""
        data = self.model_dump(mode="json", exclude={"signature"})
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def sign(self, private_key: Ed25519PrivateKey) -> "MessageEnvelope":
        """Sign the envelope in place and return it for fluent use."""
        signature = private_key.sign(self.canonical_bytes())
        self.signature = base64.b64encode(signature).decode("ascii")
        return self

    def verify(self, public_key: Ed25519PublicKey) -> bool:
        """Return whether the attached signature validates this envelope."""
        if self.signature is None:
            return False
        try:
            public_key.verify(
                base64.b64decode(self.signature.encode("ascii"), validate=True),
                self.canonical_bytes(),
            )
        except (InvalidSignature, ValueError):
            return False
        return True
