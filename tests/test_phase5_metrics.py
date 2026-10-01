"""Phase 5 metric aggregation tests."""

from pathlib import Path

import pandas as pd

from scripts.compute_metrics import compute_and_write, compute_metrics


def test_compute_metrics_uses_clean_c0_as_overhead_baseline() -> None:
    frame = pd.DataFrame(
        [
            {
                "configuration": "C0",
                "attack": "clean",
                "success": True,
                "detected": False,
                "attack_succeeded": False,
                "latency_ms": 10.0,
                "tokens_used": 20,
            },
            {
                "configuration": "C1",
                "attack": "clean",
                "success": True,
                "detected": True,
                "attack_succeeded": False,
                "latency_ms": 12.0,
                "tokens_used": 21,
            },
            {
                "configuration": "C0",
                "attack": "A1",
                "success": False,
                "detected": False,
                "attack_succeeded": True,
                "latency_ms": 0.0,
                "tokens_used": 0,
            },
            {
                "configuration": "C1",
                "attack": "A1",
                "success": True,
                "detected": True,
                "attack_succeeded": False,
                "latency_ms": 0.0,
                "tokens_used": 0,
            },
        ]
    )

    metrics = compute_metrics(frame)

    c1_latency = metrics.query(
        "configuration == 'C1' and metric == 'latency_overhead_ms_vs_C0'"
    )["value"].iloc[0]
    c1_fpr = metrics.query(
        "configuration == 'C1' and metric == 'false_positive_rate'"
    )["value"].iloc[0]
    c0_attack = metrics.query(
        "configuration == 'C0' and attack == 'A1' and metric == 'attack_success_rate'"
    )["value"].iloc[0]

    assert c1_latency == 2.0
    assert c1_fpr == 1.0
    assert c0_attack == 1.0


def test_compute_and_write_creates_phase5_artifacts(tmp_path: Path) -> None:
    raw = tmp_path / "attack_runs.jsonl"
    raw.write_text(
        '{"configuration":"C0","seed":7,"attack":"clean","success":true,"detected":false,"attack_succeeded":false,"latency_ms":1,"tokens_used":2}\n',
        encoding="utf-8",
    )

    compute_and_write(raw, tmp_path)

    assert (tmp_path / "metrics.csv").exists()
    assert (tmp_path / "summary_table.md").exists()
    assert (tmp_path / "plots" / "attack_success_detection.png").exists()
    assert (tmp_path / "plots" / "overhead_vs_baseline.png").exists()
