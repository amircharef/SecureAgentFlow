"""Tamper-evident hash-chained JSONL audit log."""

import hashlib
import json
from pathlib import Path
from typing import Any


class AuditLog:
    """Append audit records whose hashes chain to the previous record."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._last_hash = self._read_last_hash()

    def append(self, event: str, details: dict[str, Any]) -> str:
        """Append one canonical record and return its entry hash."""
        record = {"event": event, "details": details, "prev_hash": self._last_hash}
        encoded = json.dumps(record, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
        entry_hash = hashlib.sha256(encoded).hexdigest()
        record["entry_hash"] = entry_hash
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        self._last_hash = entry_hash
        return entry_hash

    def verify_chain(self) -> bool:
        """Return whether every stored record links to its predecessor."""
        previous = ""
        if not self.path.exists():
            return True
        for line in self.path.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            expected_hash = record.pop("entry_hash")
            if record.get("prev_hash") != previous:
                return False
            encoded = json.dumps(record, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
            if hashlib.sha256(encoded).hexdigest() != expected_hash:
                return False
            previous = expected_hash
        return True

    def _read_last_hash(self) -> str:
        if not self.path.exists():
            return ""
        lines = self.path.read_text(encoding="utf-8").splitlines()
        return json.loads(lines[-1])["entry_hash"] if lines else ""
