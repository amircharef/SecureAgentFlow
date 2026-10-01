"""Agent identities and Ed25519 public-key registry."""

from dataclasses import dataclass, field

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from secureagentflow.messaging import MessageEnvelope
from secureagentflow.security.exceptions import IdentityError


@dataclass(slots=True)
class AgentIdentity:
    """An agent name paired with its private signing key."""

    name: str
    private_key: Ed25519PrivateKey = field(default_factory=Ed25519PrivateKey.generate)

    @property
    def public_key(self) -> Ed25519PublicKey:
        """Return the public key safe to publish in a registry."""
        return self.private_key.public_key()


class IdentityRegistry:
    """Map registered agent names to public keys and signing identities."""

    def __init__(self) -> None:
        self._identities: dict[str, AgentIdentity] = {}

    def register(self, identity: AgentIdentity) -> None:
        """Register an identity, rejecting accidental duplicate names."""
        if identity.name in self._identities:
            raise IdentityError(f"Identity already registered: {identity.name}")
        self._identities[identity.name] = identity

    def identity(self, name: str) -> AgentIdentity:
        """Return a registered identity."""
        try:
            return self._identities[name]
        except KeyError as error:
            raise IdentityError(f"Unknown agent identity: {name}") from error

    def sign(self, envelope: MessageEnvelope) -> MessageEnvelope:
        """Sign an envelope using the registered sender identity."""
        return envelope.sign(self.identity(envelope.sender).private_key)

    def verify(self, envelope: MessageEnvelope) -> bool:
        """Verify an envelope against the sender's registered public key."""
        try:
            identity = self.identity(envelope.sender)
        except IdentityError:
            return False
        return envelope.verify(identity.public_key)
