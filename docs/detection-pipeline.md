# Detection Pipeline

## 1. Input

Each dataset provides requirement IDs and natural-language requirement text.

## 2. Preprocessing

The pipeline cleans text, creates all unordered pairs, calculates sentence-transformer cosine similarity, and identifies exact duplicate groups.

Duplicate groups use the smallest requirement ID as their representative. Non-representative members do not independently enter conflict detection; their relationships are resolved through the duplicate-group mapping. Duplicate detection remains separate from conflict detection.

Low-similarity pairs can be routed as `filtered_non_candidate`. Candidate representatives continue to Phase-1.

## 3. Phase-1

The four evidence views execute independently on one pair per model request. Each returns a verdict, confidence, concise reasoning, evidence, and assumptions.

## 4. Consensus and Adjudication

- Four `compatible` votes: finalize `compatible`.
- Four `incompatible` votes: finalize `incompatible`.
- Every other pattern: run DA, rebuttal, and arbiter.

The arbiter returns `compatible`, `incompatible`, or `uncertain`. In the published binary conflict metrics, only `incompatible` is positive.

## 5. Outputs

The finalizer writes per-pair verdicts and compatible, incompatible, and uncertain reports. The offline evaluator compares them with the included gold labels and generates TP, FP, FN, TN, Precision, Recall, F1, and Accuracy.
