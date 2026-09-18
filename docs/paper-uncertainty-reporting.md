# Paper-Ready Uncertainty Reporting

## Reporting Definition

A Phase-1 view abstains when it emits `uncertain` for a canonical candidate pair. A final abstention occurs when the disagreement handler and arbiter still return `uncertain`. Every final abstention is assigned to human review. Canonical aliases inherit the source pair's decision, so review workload is counted using unique source-pair units rather than duplicated alias rows.

## Results Paragraph

Across 6,911 stored final verdict rows, the framework abstained on 169 (2.45%). Collapsing inherited canonical aliases produced 121 unique human-review units. Dataset-level uncertainty was ETCS-GOLD 97/1599 (6.07%); OpenAPI Specification 3.0 4/870 (0.46%); promise-project2 18/913 (1.97%); Broker-All 9/654 (1.38%); Library-Gold 41/2875 (1.43%).

Phase-1 analysis covered 5,814 canonical candidates. At least one view abstained on 341 pairs (5.87%). The view-level abstention frequencies were semantic 152/5814 (2.61%); logic 203/5814 (3.49%); feasibility 35/5814 (0.60%); goal 71/5814 (1.22%). Because more than one view may abstain on the same pair, view-level counts are not additive. The artifact reports whether each abstention occurred alone or with other abstentions, whether DA selected that view for challenge, and whether the final decision became compatible, incompatible, or remained uncertain.

ETCS-GOLD used normalized final uncertainty labels: 55 unverifiable assumptions, 22 missing-domain-knowledge cases, 18 ambiguous requirements, and 2 verifiable assumptions. OpenAPI Specification 3.0 recorded four unverifiable-assumption cases. The older result schemas for promise-project2, Broker-All, and Library-Gold stored the uncertainty source as verbatim text rather than a controlled label. We therefore publish those reasons without post-hoc relabeling in `results/summary/uncertainty_reason_summary.csv` and the per-dataset JSONL evidence files.

## Interpretation

The uncertainty mechanism is an abstention mechanism, not a conflict-positive prediction. It prevents unresolved pairs from being forced into compatible or incompatible classes and exposes them as review cases. The primary quantitative result is therefore the final uncertainty rate; the unique review-unit count estimates manual workload after removing inherited aliases.
