"""YAML capability policy with deny-by-default authorization."""

from pathlib import Path
from typing import Any

import yaml

from secureagentflow.security.exceptions import PermissionDenied


class CapabilityPolicy:
    """Authorize message types and tools from a small YAML policy."""

    def __init__(self, rules: dict[str, Any]) -> None:
        self._rules = rules

    @classmethod
    def from_file(cls, path: Path) -> "CapabilityPolicy":
        """Load policy rules from YAML."""
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return cls(data)

    def allows_message(self, sender: str, message_type: str) -> bool:
        """Return whether ``sender`` may send ``message_type``."""
        agent_rules = self._rules.get("agents", {}).get(sender, {})
        return message_type in agent_rules.get("message_types", [])

    def allows_tool(self, sender: str, tool: str) -> bool:
        """Return whether ``sender`` may call ``tool``."""
        agent_rules = self._rules.get("agents", {}).get(sender, {})
        return tool in agent_rules.get("tools", [])

    def require_message(self, sender: str, message_type: str) -> None:
        """Raise when a message is not explicitly allowed."""
        if not self.allows_message(sender, message_type):
            raise PermissionDenied(f"{sender} cannot send message type {message_type}")

    def require_tool(self, sender: str, tool: str) -> None:
        """Raise when a tool is not explicitly allowed."""
        if not self.allows_tool(sender, tool):
            raise PermissionDenied(f"{sender} cannot call tool {tool}")
