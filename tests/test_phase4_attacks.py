"""Phase 4 attack simulation tests."""

import json
from pathlib import Path

from attacks import (
    compromised_agent,
    impersonation,
    message_tampering,
    privilege_escalation,
    prompt_injection,
    replay,
)
from scripts.run_experiments import run_experiments
from secureagentflow.security import CapabilityPolicy, SecurityConfig, SecurityLayer
from secureagentflow.workflow import ClinicalTask


def _layer(**overrides: bool) -> SecurityLayer:
    values = {
        "d1_identity": True,
        "d2_replay": True,
        "d3_permissions": True,
        "d4_sanitization": True,
        "d5_trust": True,
        "d6_audit": False,
    }
    values.update(overrides)
    policy = CapabilityPolicy.from_file(Path("configs/policy.yaml"))
    return SecurityLayer(SecurityConfig(**values), policy=policy)


def _task() -> ClinicalTask:
    return ClinicalTask(
        task_id="attack-task",
        document_text="age=42; sex=female; hemoglobin=12; glucose=90; creatinine=0.8",
        expected_facts={
            "age": 42,
            "sex": "female",
            "hemoglobin": 12,
            "glucose": 90,
            "creatinine": 0.8,
        },
        expected_flags=[],
    )


def test_all_attacks_are_detected_by_relevant_full_stack_defenses() -> None:
    layer = _layer()
    assert message_tampering(layer).detected
    assert replay(layer).detected
    assert impersonation(layer).detected
    assert prompt_injection(layer, _task()).detected
    assert compromised_agent(layer).detected
    assert privilege_escalation(layer).detected


def test_attack_controls_are_independently_toggleable() -> None:
    assert not message_tampering(_layer(d1_identity=False)).detected
    assert not replay(_layer(d2_replay=False)).detected
    assert not prompt_injection(
        _layer(d4_sanitization=False, d1_identity=False, d2_replay=False),
        _task(),
    ).detected
    assert not privilege_escalation(
        _layer(d3_permissions=False, d1_identity=False, d2_replay=False)
    ).detected


def test_experiment_runner_writes_reproducible_raw_rows(tmp_path: Path) -> None:
    output = tmp_path / "attack_runs.jsonl"
    run_experiments(output_path=output)
    rows = [
        json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()
    ]

    assert len(rows) == (5 * 5 * 40) + (5 * 5 * 6)
    assert {row["configuration"] for row in rows} == {"C0", "C1", "C2", "C3", "C4"}
    assert {row["attack"] for row in rows} == {
        "clean",
        "A1",
        "A2",
        "A3",
        "A4",
        "A5",
        "A6",
    }
