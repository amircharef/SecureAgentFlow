"""Composable security gateway for agent messages and inputs."""

from typing import Any
from uuid import uuid4

from secureagentflow.messaging import MessageEnvelope
from secureagentflow.security.audit import AuditLog
from secureagentflow.security.config import SecurityConfig
from secureagentflow.security.exceptions import IdentityError
from secureagentflow.security.identity import AgentIdentity, IdentityRegistry
from secureagentflow.security.permissions import CapabilityPolicy
from secureagentflow.security.replay import ReplayGuard
from secureagentflow.security.sanitizer import InputSanitizer, SanitizationResult
from secureagentflow.security.trust import TrustManager


class SecurityLayer:
    """Apply independently enabled defenses at agent trust boundaries."""

    def __init__(
        self,
        config: SecurityConfig,
        registry: IdentityRegistry | None = None,
        policy: CapabilityPolicy | None = None,
    ) -> None:
        self.config = config
        self.registry = registry or IdentityRegistry()
        self.policy = policy
        self.replay_guard = ReplayGuard(config.timestamp_window_seconds)
        self.sanitizer = InputSanitizer()
        self.trust = TrustManager(config.trust_threshold)
        self.audit: AuditLog | None = None
        if config.d3_permissions and policy is None:
            raise ValueError("A capability policy is required when D3 is enabled")
        if config.d6_audit:
            if config.audit_path is None:
                raise ValueError("audit_path is required when D6 is enabled")
            self.audit = AuditLog(config.audit_path)

    def register_agents(self, names: list[str]) -> None:
        """Create identities for names not already registered."""
        for name in names:
            try:
                self.registry.identity(name)
            except IdentityError:
                self.registry.register(AgentIdentity(name))

    def send(
        self,
        sender: str,
        receiver: str,
        message_type: str,
        payload: dict[str, Any],
        trace_id: str | None = None,
    ) -> MessageEnvelope:
        """Create and validate a message as it crosses the local boundary."""
        envelope = MessageEnvelope(
            trace_id=trace_id or str(uuid4()),
            sender=sender,
            receiver=receiver,
            type=message_type,
            payload=payload,
        )
        if self.config.d1_identity:
            self.registry.sign(envelope)
        return self.receive(envelope)

    def receive(self, envelope: MessageEnvelope) -> MessageEnvelope:
        """Apply enabled message defenses and return an accepted envelope."""
        if self.config.d1_identity and not self.registry.verify(envelope):
            raise IdentityError(f"Invalid signature for sender: {envelope.sender}")
        if self.config.d2_replay:
            self.replay_guard.check(envelope)
        if self.config.d3_permissions:
            assert self.policy is not None
            self.policy.require_message(envelope.sender, envelope.type)
        if self.config.d5_trust:
            self.trust.require_trusted(envelope.sender)
        self._audit(
            "message_accepted",
            {
                "msg_id": envelope.msg_id,
                "trace_id": envelope.trace_id,
                "sender": envelope.sender,
                "receiver": envelope.receiver,
                "type": envelope.type,
            },
        )
        return envelope

    def sanitize_document(self, document_text: str) -> SanitizationResult:
        """Sanitize a document only when D4 is enabled."""
        if not self.config.d4_sanitization:
            return SanitizationResult(document_text, False, [])
        result = self.sanitizer.sanitize(document_text)
        self._audit(
            "input_sanitized",
            {"quarantined": result.quarantined, "events": result.events},
        )
        return result

    def authorize_tool(self, agent: str, tool: str) -> None:
        """Apply D3 to an attempted tool call."""
        if self.config.d3_permissions:
            assert self.policy is not None
            self.policy.require_tool(agent, tool)
        self._audit("tool_authorized", {"agent": agent, "tool": tool})

    def record_verifier_outcome(self, agent: str, accepted: bool) -> float:
        """Update D5 reputation after a verifier decision."""
        score = self.trust.update(agent, accepted) if self.config.d5_trust else 1.0
        self._audit(
            "trust_updated", {"agent": agent, "accepted": accepted, "score": score}
        )
        return score

    def _audit(self, event: str, details: dict[str, Any]) -> None:
        if self.audit is not None:
            self.audit.append(event, details)
