# Uncertainty and Abstention Summary

This summary is generated offline from the published final verdicts and effective agent records. No model API is called.

Final uncertainty uses all final verdict rows. Phase-1 view abstention rates use canonical candidate rows only, because canonical aliases inherit a result and do not represent a new view decision.

## Final Uncertainty

| Dataset | Final pairs | Compatible | Incompatible | Uncertain | Duplicate route | Uncertainty rate | Review flag true | Uncertain without flag |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ETCS-GOLD | 1599 | 1420 | 82 | 97 | 20 | 6.07% | 95 | 2 |
| OpenAPI Specification 3.0 | 870 | 834 | 32 | 4 | 10 | 0.46% | 4 | 0 |
| promise-project2 | 913 | 887 | 8 | 18 | 0 | 1.97% | 0 | 18 |
| Broker-All | 654 | 636 | 9 | 9 | 0 | 1.38% | 0 | 9 |
| Library-Gold | 2875 | 2817 | 17 | 41 | 0 | 1.43% | 0 | 41 |

## Phase-1 View Abstention

| Dataset | View | Uncertain | Abstention rate |
| --- | --- | ---: | ---: |
| ETCS-GOLD | semantic | 59 | 7.58% |
| ETCS-GOLD | logic | 94 | 12.08% |
| ETCS-GOLD | feasibility | 12 | 1.54% |
| ETCS-GOLD | goal | 2 | 0.26% |
| OpenAPI Specification 3.0 | semantic | 11 | 1.85% |
| OpenAPI Specification 3.0 | logic | 26 | 4.38% |
| OpenAPI Specification 3.0 | feasibility | 0 | 0.00% |
| OpenAPI Specification 3.0 | goal | 0 | 0.00% |
| promise-project2 | semantic | 11 | 1.20% |
| promise-project2 | logic | 22 | 2.41% |
| promise-project2 | feasibility | 4 | 0.44% |
| promise-project2 | goal | 18 | 1.97% |
| Broker-All | semantic | 8 | 1.22% |
| Broker-All | logic | 13 | 1.99% |
| Broker-All | feasibility | 0 | 0.00% |
| Broker-All | goal | 2 | 0.31% |
| Library-Gold | semantic | 63 | 2.19% |
| Library-Gold | logic | 48 | 1.67% |
| Library-Gold | feasibility | 19 | 0.66% |
| Library-Gold | goal | 49 | 1.70% |

The per-dataset reports contain vote patterns, route/stage breakdowns, raw stored uncertainty sources, representative arbiter reasoning, and complete JSONL evidence files.
