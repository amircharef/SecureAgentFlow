# SecureAgentFlow Evaluation Summary

All values below are computed from `results/attack_runs.jsonl`; no results are hard-coded.

## Clean-task and overhead metrics

| configuration | false_positive_rate | latency_overhead_ms_vs_C0 | mean_latency_ms | mean_tokens_used | task_success_rate | token_overhead_vs_C0 |
| --- | --- | --- | --- | --- | --- | --- |
| C0 | 0.0 | 0.0 | 0.170145 | 17.0 | 1.0 | 0.0 |
| C1 | 0.0 | 0.97286 | 1.143005 | 17.0 | 1.0 | 0.0 |
| C2 | 0.0 | 0.95914 | 1.129285 | 17.0 | 1.0 | 0.0 |
| C3 | 0.0 | 0.991685 | 1.16183 | 17.0 | 1.0 | 0.0 |
| C4 | 0.0 | 6.24167 | 6.411815 | 17.0 | 1.0 | 0.0 |

## Attack metrics

| configuration | attack_success_rate | detection_rate |
| --- | --- | --- |
| C0 | 1.0 | 0.0 |
| C1 | 0.5 | 0.5 |
| C2 | 0.333333 | 0.666667 |
| C3 | 0.166667 | 0.833333 |
| C4 | 0.0 | 1.0 |

## Interpretation

Attack success is the fraction of attack rows where the simulated attacker achieved its goal. Detection is the fraction of attack rows rejected or quarantined by the active defenses. False-positive rate is measured on clean rows using the raw `detected` field.
