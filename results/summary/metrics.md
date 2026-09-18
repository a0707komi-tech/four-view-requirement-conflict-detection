# Full Four-View Framework Results

Conflict detection metrics use `incompatible` as the positive prediction. Duplicate labels are excluded from the conflict-positive gold set.

| Dataset | TP | FP | FN | TN | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ETCS-GOLD | 36 | 26 | 13 | 1941 | 0.58 | 0.73 | 0.65 | 0.98 |
| OpenAPI Specification 3.0 | 20 | 2 | 0 | 1631 | 0.91 | 1.00 | 0.95 | 1.00 |
| promise-project2 | 7 | 1 | 4 | 2004 | 0.88 | 0.64 | 0.74 | 1.00 |
| Broker-All | 8 | 1 | 5 | 976 | 0.89 | 0.62 | 0.73 | 0.99 |
| Library-Gold | 17 | 0 | 3 | 5866 | 1.00 | 0.85 | 0.92 | 1.00 |

Mean F1 across datasets: **0.80**

Uncertainty and abstention analysis: [uncertainty_summary.md](uncertainty_summary.md)
