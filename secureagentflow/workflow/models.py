"""Typed task and workflow output models."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class ClinicalTask(BaseModel):
    """One synthetic clinical document task."""

    model_config = ConfigDict(extra="forbid")

    task_id: str
    document_text: str
    expected_facts: dict[str, Any]
    expected_flags: list[str]


class WorkflowPlan(BaseModel):
    """A small explicit DAG for the baseline workflow."""

    steps: list[str] = [
        "extract_facts",
        "assess_risk",
        "write_summary",
        "verify_summary",
    ]
    edges: list[tuple[str, str]] = [
        ("extract_facts", "assess_risk"),
        ("assess_risk", "write_summary"),
        ("write_summary", "verify_summary"),
    ]


class TaskOutput(BaseModel):
    """Serialized output produced for one clinical task."""

    task_id: str
    summary: str
    extracted_facts: dict[str, Any]
    risk_flags: list[str]
    trace_id: str
    security_events: list[dict[str, Any]]
    success: bool
    latency_ms: float
    tokens_used: int
