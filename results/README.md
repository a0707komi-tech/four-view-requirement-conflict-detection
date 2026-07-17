# Experiment Results

This directory contains only the complete four-view framework results. Ablation, baseline-comparison, and threshold/end-to-end experiments are excluded.

## Layout

- `summary/`: metrics across all five datasets.
- `final/<dataset>/`: final verdicts, verdict partitions, metrics, false positives, missed conflicts, and correctly detected conflicts.
- `agents/<agent>/<dataset>.jsonl`: latest successful effective record for every processed pair.

The seven exported agents are semantic, logic, feasibility, goal, DA, rebuttal, and arbiter. Failed retry records, superseded attempts, Batch provider IDs, raw request archives, scheduler state, and run logs are excluded.

Final conflict metrics treat `incompatible` as the positive prediction. `uncertain` is non-positive. Duplicate labels are not conflict-positive.

ETCS-GOLD uses the fourth-round result. The other four datasets use their repaired and completed formal runs listed in `release_manifest.json`.

## License

Unless a third-party right applies to quoted dataset text, the project-generated result structure, metrics, and reports are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
