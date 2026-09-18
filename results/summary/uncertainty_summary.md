# Uncertainty and Abstention Summary

This summary is generated offline from the published final verdicts and effective agent records. No model API is called.

Final uncertainty uses all final verdict rows. Phase-1 view abstention rates use canonical candidate rows only, because canonical aliases inherit a result and do not represent a new view decision.

## Final Uncertainty

| Dataset | Final pairs | Compatible | Incompatible | Uncertain | Duplicate route (subset) | Uncertainty rate | Unique review units | Legacy review flag true |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ETCS-GOLD | 1599 | 1420 | 82 | 97 | 20 | 6.07% | 50 | 95 |
| OpenAPI Specification 3.0 | 870 | 834 | 32 | 4 | 10 | 0.46% | 3 | 4 |
| promise-project2 | 913 | 887 | 8 | 18 | 0 | 1.97% | 18 | 0 |
| Broker-All | 654 | 636 | 9 | 9 | 0 | 1.38% | 9 | 0 |
| Library-Gold | 2875 | 2817 | 17 | 41 | 0 | 1.43% | 41 | 0 |

## Phase-1 View Abstention

| Dataset | View | Uncertain | Rate | Single-view | Multi-view | DA target | Final C | Final I | Final U |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ETCS-GOLD | semantic | 59 | 7.58% | 36 | 23 | 2 | 27 | 7 | 25 |
| ETCS-GOLD | logic | 94 | 12.08% | 70 | 24 | 25 | 57 | 5 | 32 |
| ETCS-GOLD | feasibility | 12 | 1.54% | 7 | 5 | 6 | 7 | 2 | 3 |
| ETCS-GOLD | goal | 2 | 0.26% | 1 | 1 | 1 | 2 | 0 | 0 |
| OpenAPI Specification 3.0 | semantic | 11 | 1.85% | 8 | 3 | 2 | 8 | 1 | 2 |
| OpenAPI Specification 3.0 | logic | 26 | 4.38% | 23 | 3 | 12 | 24 | 1 | 1 |
| OpenAPI Specification 3.0 | feasibility | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 0 |
| OpenAPI Specification 3.0 | goal | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 0 |
| promise-project2 | semantic | 11 | 1.20% | 6 | 5 | 4 | 5 | 0 | 6 |
| promise-project2 | logic | 22 | 2.41% | 16 | 6 | 12 | 14 | 1 | 7 |
| promise-project2 | feasibility | 4 | 0.44% | 2 | 2 | 2 | 2 | 1 | 1 |
| promise-project2 | goal | 18 | 1.97% | 11 | 7 | 11 | 15 | 0 | 3 |
| Broker-All | semantic | 8 | 1.22% | 6 | 2 | 2 | 4 | 0 | 4 |
| Broker-All | logic | 13 | 1.99% | 11 | 2 | 8 | 8 | 1 | 4 |
| Broker-All | feasibility | 0 | 0.00% | 0 | 0 | 0 | 0 | 0 | 0 |
| Broker-All | goal | 2 | 0.31% | 0 | 2 | 0 | 0 | 0 | 2 |
| Library-Gold | semantic | 63 | 2.19% | 26 | 37 | 11 | 28 | 0 | 35 |
| Library-Gold | logic | 48 | 1.67% | 17 | 31 | 14 | 15 | 4 | 29 |
| Library-Gold | feasibility | 19 | 0.66% | 2 | 17 | 6 | 2 | 0 | 17 |
| Library-Gold | goal | 49 | 1.70% | 19 | 30 | 21 | 20 | 0 | 29 |

The per-dataset reports contain vote patterns, route/stage breakdowns, raw stored uncertainty sources, representative arbiter reasoning, and complete JSONL evidence files.
