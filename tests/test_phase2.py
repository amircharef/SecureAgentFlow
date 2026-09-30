"""Phase 2 baseline workflow tests."""

from secureagentflow.llm import MockLLM
from secureagentflow.workflow import BaselineOrchestrator, ClinicalTask


def test_baseline_orchestrator_completes_clean_task() -> None:
    task = ClinicalTask(
        task_id="task-0001",
        document_text=(
            "Synthetic patient 1: age=42; sex=female; hemoglobin=11.2; "
            "glucose=155; creatinine=0.9; note=scheduled follow-up."
        ),
        expected_facts={
            "age": 42,
            "sex": "female",
            "hemoglobin": 11.2,
            "glucose": 155,
            "creatinine": 0.9,
        },
        expected_flags=["hyperglycemia"],
    )

    output = BaselineOrchestrator(MockLLM()).run(task)

    assert output.success
    assert output.extracted_facts == task.expected_facts
    assert output.risk_flags == task.expected_flags
    assert output.security_events == []
    assert output.tokens_used > 0
    assert output.trace_id


def test_baseline_plan_is_a_linear_dag() -> None:
    orchestrator = BaselineOrchestrator(MockLLM())
    task = ClinicalTask(
        task_id="task-0002",
        document_text="age=30; sex=male; hemoglobin=14; glucose=90; creatinine=0.8",
        expected_facts={
            "age": 30,
            "sex": "male",
            "hemoglobin": 14,
            "glucose": 90,
            "creatinine": 0.8,
        },
        expected_flags=[],
    )

    plan = orchestrator.build_plan(task)

    assert plan.steps == ["extract_facts", "assess_risk", "write_summary", "verify_summary"]
    assert len(plan.edges) == len(plan.steps) - 1
