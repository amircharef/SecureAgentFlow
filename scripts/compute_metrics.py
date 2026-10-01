"""Compute Phase 5 metrics and plots from raw experiment rows."""

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

ATTACKS = ["A1", "A2", "A3", "A4", "A5", "A6"]


def load_runs(path: Path) -> pd.DataFrame:
    """Load raw JSONL experiment rows into a validated dataframe."""
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    if not rows:
        raise ValueError(f"No experiment rows found in {path}")
    frame = pd.DataFrame(rows)
    required = {
        "configuration",
        "seed",
        "attack",
        "success",
        "detected",
        "attack_succeeded",
        "latency_ms",
        "tokens_used",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing raw result columns: {sorted(missing)}")
    return frame


def _mean(frame: pd.DataFrame, column: str) -> float:
    """Return a numeric mean, rounded only at output time."""
    return float(frame[column].mean()) if not frame.empty else 0.0


def compute_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """Compute observed task, attack, detection, and overhead metrics."""
    configurations = sorted(frame["configuration"].unique())
    clean = frame[frame["attack"] == "clean"]
    attacks = frame[frame["attack"].isin(ATTACKS)]
    baseline_clean = clean[clean["configuration"] == "C0"]
    baseline_latency = _mean(baseline_clean, "latency_ms")
    baseline_tokens = _mean(baseline_clean, "tokens_used")
    records: list[dict[str, Any]] = []

    for configuration in configurations:
        clean_config = clean[clean["configuration"] == configuration]
        attack_config = attacks[attacks["configuration"] == configuration]
        records.extend(
            [
                {
                    "configuration": configuration,
                    "attack": "clean",
                    "metric": "task_success_rate",
                    "value": _mean(clean_config, "success"),
                    "sample_count": len(clean_config),
                },
                {
                    "configuration": configuration,
                    "attack": "clean",
                    "metric": "false_positive_rate",
                    "value": _mean(clean_config, "detected"),
                    "sample_count": len(clean_config),
                },
                {
                    "configuration": configuration,
                    "attack": "clean",
                    "metric": "mean_latency_ms",
                    "value": _mean(clean_config, "latency_ms"),
                    "sample_count": len(clean_config),
                },
                {
                    "configuration": configuration,
                    "attack": "clean",
                    "metric": "latency_overhead_ms_vs_C0",
                    "value": _mean(clean_config, "latency_ms") - baseline_latency,
                    "sample_count": len(clean_config),
                },
                {
                    "configuration": configuration,
                    "attack": "clean",
                    "metric": "mean_tokens_used",
                    "value": _mean(clean_config, "tokens_used"),
                    "sample_count": len(clean_config),
                },
                {
                    "configuration": configuration,
                    "attack": "clean",
                    "metric": "token_overhead_vs_C0",
                    "value": _mean(clean_config, "tokens_used") - baseline_tokens,
                    "sample_count": len(clean_config),
                },
                {
                    "configuration": configuration,
                    "attack": "all_attacks",
                    "metric": "attack_success_rate",
                    "value": _mean(attack_config, "attack_succeeded"),
                    "sample_count": len(attack_config),
                },
                {
                    "configuration": configuration,
                    "attack": "all_attacks",
                    "metric": "detection_rate",
                    "value": _mean(attack_config, "detected"),
                    "sample_count": len(attack_config),
                },
            ]
        )
        for attack in ATTACKS:
            attack_rows = attack_config[attack_config["attack"] == attack]
            records.extend(
                [
                    {
                        "configuration": configuration,
                        "attack": attack,
                        "metric": "attack_success_rate",
                        "value": _mean(attack_rows, "attack_succeeded"),
                        "sample_count": len(attack_rows),
                    },
                    {
                        "configuration": configuration,
                        "attack": attack,
                        "metric": "detection_rate",
                        "value": _mean(attack_rows, "detected"),
                        "sample_count": len(attack_rows),
                    },
                ]
            )

    metrics = pd.DataFrame(records)
    metrics["value"] = metrics["value"].round(6)
    return metrics


def _write_summary(metrics: pd.DataFrame, path: Path) -> None:
    """Write human-readable tables derived from the metrics dataframe."""

    def markdown_table(frame: pd.DataFrame) -> str:
        """Render a dataframe as Markdown without an extra table dependency."""
        columns = [str(column) for column in frame.columns]
        lines = [
            "| " + " | ".join(columns) + " |",
            "| " + " | ".join("---" for _ in columns) + " |",
        ]
        for row in frame.itertuples(index=False, name=None):
            lines.append("| " + " | ".join(str(value) for value in row) + " |")
        return "\n".join(lines)

    clean = metrics[metrics["attack"] == "clean"]
    attacks = metrics[metrics["attack"] == "all_attacks"]
    table = clean.pivot(
        index="configuration", columns="metric", values="value"
    ).reset_index()
    attack_table = attacks.pivot(
        index="configuration", columns="metric", values="value"
    ).reset_index()
    sections = [
        "# SecureAgentFlow Evaluation Summary",
        "",
        "All values below are computed from `results/attack_runs.jsonl`; no results are hard-coded.",
        "",
        "## Clean-task and overhead metrics",
        "",
        markdown_table(table),
        "",
        "## Attack metrics",
        "",
        markdown_table(attack_table),
        "",
        "## Interpretation",
        "",
        "Attack success is the fraction of attack rows where the simulated attacker achieved its goal. Detection is the fraction of attack rows rejected or quarantined by the active defenses. False-positive rate is measured on clean rows using the raw `detected` field.",
        "",
    ]
    path.write_text("\n".join(sections), encoding="utf-8")


def _write_plots(metrics: pd.DataFrame, output_dir: Path) -> None:
    """Write plots for attack success and clean-task overhead."""
    output_dir.mkdir(parents=True, exist_ok=True)
    attack = metrics[
        (metrics["attack"] == "all_attacks")
        & (metrics["metric"].isin(["attack_success_rate", "detection_rate"]))
    ]
    attack_pivot = attack.pivot(index="configuration", columns="metric", values="value")
    axes = attack_pivot.plot(kind="bar", ylim=(0, 1), figsize=(8, 5), rot=0)
    axes.set_ylabel("Rate")
    axes.set_xlabel("Configuration")
    axes.set_title("Attack success and detection rates")
    axes.legend(title="Metric")
    axes.figure.tight_layout()
    axes.figure.savefig(output_dir / "attack_success_detection.png", dpi=160)
    plt.close(axes.figure)

    clean = metrics[metrics["attack"] == "clean"]
    overhead = clean.pivot(index="configuration", columns="metric", values="value")
    columns = ["latency_overhead_ms_vs_C0", "token_overhead_vs_C0"]
    axes = overhead[columns].plot(kind="bar", figsize=(8, 5), rot=0)
    axes.set_ylabel("Overhead")
    axes.set_xlabel("Configuration")
    axes.set_title("Latency and token overhead versus C0")
    axes.legend(title="Metric")
    axes.figure.tight_layout()
    axes.figure.savefig(output_dir / "overhead_vs_baseline.png", dpi=160)
    plt.close(axes.figure)


def compute_and_write(
    input_path: Path = Path("results/attack_runs.jsonl"),
    results_dir: Path = Path("results"),
) -> pd.DataFrame:
    """Compute metrics, tables, and plots from one raw run file."""
    metrics = compute_metrics(load_runs(input_path))
    results_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(results_dir / "metrics.csv", index=False)
    _write_summary(metrics, results_dir / "summary_table.md")
    _write_plots(metrics, results_dir / "plots")
    return metrics


def main() -> None:
    """Parse CLI arguments and write all Phase 5 artifacts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("results/attack_runs.jsonl"))
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    args = parser.parse_args()
    compute_and_write(args.input, args.results_dir)


if __name__ == "__main__":
    main()
