"""Run reproducible Phase 4 attack simulations and baseline workflows."""

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from attacks import (
    compromised_agent,
    impersonation,
    message_tampering,
    privilege_escalation,
    prompt_injection,
    replay,
)
from scripts.generate_dataset import generate_tasks
from secureagentflow.llm import MockLLM
from secureagentflow.security import CapabilityPolicy, SecurityConfig, SecurityLayer
from secureagentflow.workflow import BaselineOrchestrator, ClinicalTask


def build_security_layer(
    name: str, config_data: dict[str, Any], audit_dir: Path
) -> SecurityLayer:
    """Build one named experiment security configuration."""
    config = SecurityConfig(
        **config_data,
        audit_path=audit_dir / f"{name}.jsonl" if config_data.get("d6_audit") else None,
    )
    policy = (
        CapabilityPolicy.from_file(Path("configs/policy.yaml"))
        if config.d3_permissions
        else None
    )
    return SecurityLayer(config, policy=policy)


def run_experiments(
    config_path: Path = Path("configs/experiments.yaml"),
    output_path: Path = Path("results/attack_runs.jsonl"),
) -> None:
    """Run all configurations, seeds, clean tasks, and six attacks."""
    experiment_config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit_dir = output_path.parent / "audit"
    rows: list[dict[str, Any]] = []
    seeds = experiment_config["seeds"]
    for configuration, security_config in experiment_config["configurations"].items():
        for seed in seeds:
            tasks = generate_tasks(experiment_config["dataset_count"], seed)
            layer = build_security_layer(configuration, security_config, audit_dir)
            orchestrator = BaselineOrchestrator(
                MockLLM(), security=layer if configuration != "C0" else None
            )
            for raw_task in tasks:
                task = ClinicalTask.model_validate(raw_task)
                output = orchestrator.run(task)
                rows.append(
                    {
                        "configuration": configuration,
                        "seed": seed,
                        "attack": "clean",
                        "task_id": task.task_id,
                        "success": output.success,
                        "detected": any(
                            event["event"] == "input_quarantined"
                            for event in output.security_events
                        ),
                        "attack_succeeded": False,
                        "latency_ms": output.latency_ms,
                        "tokens_used": output.tokens_used,
                    }
                )
            attack_task = ClinicalTask.model_validate(tasks[0])
            attack_results = [
                message_tampering(layer),
                replay(layer),
                impersonation(layer),
                prompt_injection(layer, attack_task),
                compromised_agent(layer),
                privilege_escalation(layer),
            ]
            for result in attack_results:
                rows.append(
                    {
                        "configuration": configuration,
                        "seed": seed,
                        "attack": result.attack_id,
                        "task_id": attack_task.task_id,
                        "success": not result.attack_succeeded,
                        "detected": result.detected,
                        "attack_succeeded": result.attack_succeeded,
                        "latency_ms": 0.0,
                        "tokens_used": 0,
                        "events": result.events,
                    }
                )
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"Wrote {len(rows)} experiment rows to {output_path}")


def main() -> None:
    """Parse CLI arguments and run the experiment matrix."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/experiments.yaml"))
    parser.add_argument(
        "--output", type=Path, default=Path("results/attack_runs.jsonl")
    )
    args = parser.parse_args()
    run_experiments(args.config, args.output)


if __name__ == "__main__":
    main()
