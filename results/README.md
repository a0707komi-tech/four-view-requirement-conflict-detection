# Experiment Results

This directory contains only the complete four-view framework results. Ablation, baseline-comparison, and threshold/end-to-end experiments are excluded.

## Layout

- `summary/`: metrics across all five datasets.
- `summary/uncertainty_summary.md`: final uncertainty rates, explicit human-review flags, and Phase-1 view abstention rates.
- `summary/uncertainty_summary.csv`: machine-readable uncertainty summary.
- `summary/phase1_abstention_summary.csv`: one row per dataset and Phase-1 view.
- `summary/phase1_abstention_reasons.csv`: every Phase-1 abstention with its stored reasoning, evidence, context, DA targeting, and downstream final verdict.
- `summary/uncertainty_reason_summary.csv`: exact stored uncertainty sources and counts, without post-hoc relabeling.
- `final/<dataset>/`: final verdicts, verdict partitions, metrics, conflict reports, uncertainty reports, and JSONL evidence.
- `agents/<agent>/<dataset>.jsonl`: latest successful effective record for every processed pair.

The seven exported agents are semantic, logic, feasibility, goal, DA, rebuttal, and arbiter. Failed retry records, superseded attempts, Batch provider IDs, raw request archives, scheduler state, and run logs are excluded.

Final conflict metrics treat `incompatible` as the positive prediction. `uncertain` is non-positive. Duplicate labels are not conflict-positive.

The uncertainty reports are generated offline from the stored final verdicts and agent records. Final uncertainty rates use all final verdict rows. Phase-1 abstention rates use `canonical_candidate` rows only because `canonical_alias` rows inherit a canonical result rather than invoking the Phase-1 views again. Every final `uncertain` row enters the recommended human-review queue; aliases share their canonical source pair's review unit. Each dataset also contains `uncertainty_reasons.jsonl` and `phase1_abstentions.jsonl` for row-level traceability.

ETCS-GOLD uses the fourth-round result. The other four datasets use their repaired and completed formal runs listed in `release_manifest.json`.

## License

Unless a third-party right applies to quoted dataset text, the project-generated result structure, metrics, and reports are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
