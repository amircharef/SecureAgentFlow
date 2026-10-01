"""Generate reproducible synthetic clinical document tasks."""

import argparse
import json
import random
from pathlib import Path
from typing import Any


def _flags_for(facts: dict[str, Any]) -> list[str]:
    """Derive expected flags using the baseline clinical rules."""
    flags: list[str] = []
    if facts["hemoglobin"] < 10:
        flags.append("anemia")
    if facts["glucose"] >= 140:
        flags.append("hyperglycemia")
    if facts["creatinine"] > 1.3:
        flags.append("renal_impairment")
    return flags


def generate_tasks(count: int = 40, seed: int = 7) -> list[dict[str, Any]]:
    """Create ``count`` deterministic synthetic tasks."""
    generator = random.Random(seed)
    tasks: list[dict[str, Any]] = []
    for index in range(1, count + 1):
        facts = {
            "age": generator.randint(18, 90),
            "sex": generator.choice(["female", "male"]),
            "hemoglobin": round(generator.uniform(7.5, 15.5), 1),
            "glucose": generator.randint(70, 220),
            "creatinine": round(generator.uniform(0.6, 2.1), 1),
        }
        flags = _flags_for(facts)
        document = (
            f"Synthetic patient {index}: age={facts['age']}; sex={facts['sex']}; "
            f"hemoglobin={facts['hemoglobin']}; glucose={facts['glucose']}; "
            f"creatinine={facts['creatinine']}; note=scheduled follow-up."
        )
        tasks.append(
            {
                "task_id": f"task-{index:04d}",
                "document_text": document,
                "expected_facts": facts,
                "expected_flags": flags,
            }
        )
    return tasks


def main() -> None:
    """Write one JSON task file per generated synthetic patient."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data/tasks"))
    parser.add_argument("--count", type=int, default=40)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for task in generate_tasks(count=args.count, seed=args.seed):
        path = args.output_dir / f"{task['task_id']}.json"
        path.write_text(
            json.dumps(task, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(f"Generated {args.count} tasks in {args.output_dir}")


if __name__ == "__main__":
    main()
