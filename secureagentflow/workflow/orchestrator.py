"""Baseline multi-agent orchestrator for the clinical workflow."""

from time import perf_counter
from uuid import uuid4

from secureagentflow.agents import AnalystAgent, ExtractorAgent, VerifierAgent, WriterAgent
from secureagentflow.agents.base import AgentContext
from secureagentflow.llm import LLMClient
from secureagentflow.messaging import MessageEnvelope
from secureagentflow.workflow.models import ClinicalTask, TaskOutput, WorkflowPlan


class BaselineOrchestrator:
    """Run C0 with explicit routing and no active security defenses."""

    def __init__(self, llm: LLMClient) -> None:
        self.extractor = ExtractorAgent("extractor", llm)
        self.analyst = AnalystAgent("analyst", llm)
        self.writer = WriterAgent("writer", llm)
        self.verifier = VerifierAgent("verifier", llm)

    def build_plan(self, task: ClinicalTask) -> WorkflowPlan:
        """Build the fixed DAG used for a clinical document task."""
        del task
        return WorkflowPlan()

    def run(self, task: ClinicalTask) -> TaskOutput:
        """Execute the baseline workflow and return its measured output."""
        started = perf_counter()
        trace_id = str(uuid4())
        context = AgentContext(trace_id=trace_id)
        self.build_plan(task)

        extracted_facts = self.extractor.extract(task.document_text, context)
        self._transport(context, "extractor", "analyst", "facts", {"facts": extracted_facts})
        risk_flags = self.analyst.analyze(extracted_facts, context)
        self._transport(context, "analyst", "writer", "risk_flags", {"risk_flags": risk_flags})
        summary = self.writer.write(extracted_facts, risk_flags, context)
        self._transport(context, "writer", "verifier", "summary", {"summary": summary})
        success = self.verifier.verify(
            task.document_text,
            task.expected_facts,
            task.expected_flags,
            extracted_facts,
            risk_flags,
            summary,
            context,
        )
        latency_ms = (perf_counter() - started) * 1000
        return TaskOutput(
            task_id=task.task_id,
            summary=summary,
            extracted_facts=extracted_facts,
            risk_flags=risk_flags,
            trace_id=trace_id,
            security_events=[],
            success=success,
            latency_ms=round(latency_ms, 3),
            tokens_used=context.tokens_used,
        )

    @staticmethod
    def _transport(
        context: AgentContext,
        sender: str,
        receiver: str,
        message_type: str,
        payload: dict[str, object],
    ) -> None:
        """Construct a baseline unsigned envelope for observability."""
        MessageEnvelope(
            trace_id=context.trace_id,
            sender=sender,
            receiver=receiver,
            type=message_type,
            payload=payload,
        )
