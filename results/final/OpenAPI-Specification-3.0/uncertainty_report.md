# Uncertainty and Abstention Report: OpenAPI Specification 3.0

This report is generated offline from the stored final verdicts and agent records. It does not call any model API.

## Scope and Denominators

- Final verdict rows: **870**.
- Canonical candidate rows with Phase-1 execution: **594**.
- Final uncertainty rate uses all final verdict rows, including canonical aliases and duplicate routes.
- Duplicate-group rows are shown as a separate route because the historical final artifact stores them as `incompatible` with `duplicate_conflict=true`; conflict metrics exclude them.
- View-level abstention rates use canonical candidate rows only; aliases inherit a result and are not counted as new view decisions.

## Final Outcomes

| Outcome | Count | Rate |
| --- | ---: | ---: |
| `compatible` | 834 | 95.86% |
| `incompatible` | 32 | 3.68% |
| `uncertain` | 4 | 0.46% |
| `duplicate_group_rule` route | 10 | 1.15% |

## Uncertainty and Human Review

| Measure | Count | Rate |
| --- | ---: | ---: |
| Final `uncertain` | 4 | 0.46% of final rows |
| `needs_human_review=true` among uncertain rows | 4 | 100.00% of uncertain rows |
| Uncertain rows without review flag | 0 | - |

Uncertainty is reported exactly as stored. The report does not infer a human-review flag from the verdict; the finalizer's stored `needs_human_review` value is shown separately.

## Final Uncertainty by Route and Stage

| Dimension | Count |
| --- | ---: |
| Route `canonical_candidate` | 3 |
| Route `canonical_alias` | 1 |
| Stage `canonical_candidate` | 3 |
| Stage `canonical_alias` | 1 |

## Phase-1 View Abstention

| View | Evaluated pairs | Compatible | Incompatible | Uncertain | Missing | Abstention rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| semantic | 594 | 569 | 14 | 11 | 0 | 1.85% |
| logic | 594 | 553 | 15 | 26 | 0 | 4.38% |
| feasibility | 594 | 542 | 52 | 0 | 0 | 0.00% |
| goal | 594 | 555 | 39 | 0 | 0 | 0.00% |

Canonical candidate pairs with at least one Phase-1 abstention: **34** (5.72%).

## Phase-1 Vote Patterns

| Vote pattern | Count |
| --- | ---: |
| `semantic=compatible; logic=compatible; feasibility=compatible; goal=compatible` | 515 |
| `semantic=compatible; logic=compatible; feasibility=incompatible; goal=compatible` | 19 |
| `semantic=compatible; logic=uncertain; feasibility=compatible; goal=compatible` | 14 |
| `semantic=incompatible; logic=incompatible; feasibility=incompatible; goal=incompatible` | 13 |
| `semantic=compatible; logic=compatible; feasibility=incompatible; goal=incompatible` | 7 |
| `semantic=compatible; logic=compatible; feasibility=compatible; goal=incompatible` | 4 |
| `semantic=compatible; logic=uncertain; feasibility=compatible; goal=incompatible` | 4 |
| `semantic=uncertain; logic=compatible; feasibility=incompatible; goal=incompatible` | 3 |
| `semantic=uncertain; logic=compatible; feasibility=compatible; goal=compatible` | 3 |
| `semantic=compatible; logic=uncertain; feasibility=incompatible; goal=incompatible` | 3 |
| `semantic=compatible; logic=incompatible; feasibility=incompatible; goal=incompatible` | 2 |
| `semantic=uncertain; logic=uncertain; feasibility=incompatible; goal=incompatible` | 2 |
| `semantic=uncertain; logic=compatible; feasibility=incompatible; goal=compatible` | 1 |
| `semantic=uncertain; logic=compatible; feasibility=compatible; goal=incompatible` | 1 |
| `semantic=compatible; logic=uncertain; feasibility=incompatible; goal=compatible` | 1 |
| `semantic=uncertain; logic=uncertain; feasibility=compatible; goal=compatible` | 1 |
| `semantic=incompatible; logic=uncertain; feasibility=incompatible; goal=compatible` | 1 |

## Stored Uncertainty Sources

| Source | Count |
| --- | ---: |
| unverifiable_assumption | 4 |

## Representative Final Uncertain Cases

### 5_20

- Route: `canonical_candidate`; confidence: `0.76`; human review flag: `True`.
- Stored uncertainty source: unverifiable_assumption.
- Phase-1 votes: `{"semantic": {"verdict": "compatible", "confidence": 0.95, "model": "deepseek-v4-flash"}, "logic": {"verdict": "incompatible", "confidence": 0.95, "model": "deepseek-v4-pro"}, "feasibility": {"verdict": "incompatible", "confidence": 0.85, "model": "kimi-k2.6"}, "goal": {"verdict": "incompatible", "confidence": 0.95, "model": "qwen3.7-plus"}}`.
- Cross-examination: {"target": "semantic", "challenge": "You assume the version field in Requirement B contains a semantic version number whose major.minor is the same as in Requirement A. Where in the text is that identity established?", "rebuttal_verdict_revised": true}.
- Arbiter reasoning: The pair does not textually establish that Requirement B’s `version` field is the same semantic version number referenced in Requirement A. A speaks about the major.minor portion of a semantic version number and assigns it the meaning of the OAS feature set. B speaks about the Info Object’s version field reflecting the deployed API implementation version and being updated on production release. If these are the same version identifier, there may be inconsistency; but that identity is a decisive unstated premise. Without it, no text-grounded interference, inconsistency, or impossible joint satisfaction is established from the pair alone..

### 5_21

- Route: `canonical_candidate`; confidence: `0.84`; human review flag: `True`.
- Stored uncertainty source: unverifiable_assumption.
- Phase-1 votes: `{"semantic": {"verdict": "uncertain", "confidence": 0.4, "model": "deepseek-v4-flash"}, "logic": {"verdict": "compatible", "confidence": 0.95, "model": "deepseek-v4-pro"}, "feasibility": {"verdict": "compatible", "confidence": 0.9, "model": "kimi-k2.6"}, "goal": {"verdict": "incompatible", "confidence": 0.95, "model": "qwen3.7-plus"}}`.
- Cross-examination: {"target": "goal", "challenge": "What text in the pair establishes that 'the semantic version number' in Requirement A and 'the Info Object version field' in Requirement B refer to the same field, rather than to distinct version fields in the specification?", "rebuttal_verdict_revised": true}.
- Arbiter reasoning: The pair does not textually establish a shared target strongly enough to ground conflict. Requirement A speaks of "the semantic version number" whose major.minor designates the OAS feature set, while Requirement B specifically constrains the "Info Object version field" to represent the OpenAPI document version, not the specification version. A conflict exists only if A’s semantic version number is the same field as B’s Info Object version field, but that identity is not stated in the pair. Without that decisive overlap premise, interference, inconsistency, and impossible joint satisfaction are not established from the text alone..

### 13_27

- Route: `canonical_candidate`; confidence: `0.77`; human review flag: `True`.
- Stored uncertainty source: unverifiable_assumption.
- Phase-1 votes: `{"semantic": {"verdict": "uncertain", "confidence": 0.3, "model": "deepseek-v4-flash"}, "logic": {"verdict": "uncertain", "confidence": 0.3, "model": "deepseek-v4-pro"}, "feasibility": {"verdict": "incompatible", "confidence": 0.95, "model": "kimi-k2.6"}, "goal": {"verdict": "incompatible", "confidence": 0.95, "model": "qwen3.7-plus"}}`.
- Cross-examination: {"target": "feasibility", "challenge": "You claim incompatibility because two parameters cannot share the same name and location, but Requirement B explicitly says both declarations MUST use the same name. How does that create a conflict rather than a single, shared placeholder?", "rebuttal_verdict_revised": false}.
- Arbiter reasoning: The pair is only weakly anchored to the same target. A constrains the syntax of OpenAPI path templates; B constrains how renamed parameters are declared during a transition, but does not clearly say the parameter is a path parameter or that two distinct placeholder names must coexist in one template. The incompatibility arguments rely on extra OpenAPI assumptions: that B applies to path parameters here, that template placeholder names must match declaration names, and that the two declarations correspond to different names despite B also saying they must use the same name at the same location. Without those decisive assumptions, no text-grounded interference, inconsistency, or impossible joint satisfaction between A and B is established from the pair alone..

### 24_27

- Route: `canonical_alias`; confidence: `0.77`; human review flag: `True`.
- Stored uncertainty source: unverifiable_assumption.
- Phase-1 votes: `{"semantic": {"verdict": "uncertain", "confidence": 0.3, "model": "deepseek-v4-flash"}, "logic": {"verdict": "uncertain", "confidence": 0.3, "model": "deepseek-v4-pro"}, "feasibility": {"verdict": "incompatible", "confidence": 0.95, "model": "kimi-k2.6"}, "goal": {"verdict": "incompatible", "confidence": 0.95, "model": "qwen3.7-plus"}}`.
- Cross-examination: {"target": "feasibility", "challenge": "You claim incompatibility because two parameters cannot share the same name and location, but Requirement B explicitly says both declarations MUST use the same name. How does that create a conflict rather than a single, shared placeholder?", "rebuttal_verdict_revised": false}.
- Arbiter reasoning: The pair is only weakly anchored to the same target. A constrains the syntax of OpenAPI path templates; B constrains how renamed parameters are declared during a transition, but does not clearly say the parameter is a path parameter or that two distinct placeholder names must coexist in one template. The incompatibility arguments rely on extra OpenAPI assumptions: that B applies to path parameters here, that template placeholder names must match declaration names, and that the two declarations correspond to different names despite B also saying they must use the same name at the same location. Without those decisive assumptions, no text-grounded interference, inconsistency, or impossible joint satisfaction between A and B is established from the pair alone..


## Phase-1 Abstention Evidence

- `semantic` on `1_6`: Failed to parse LLM output
  Evidence: []
- `semantic` on `1_52`: Failed to parse LLM output
  Evidence: []
- `logic` on `3_27`: Failed to parse LLM output
  Evidence: []
- `logic` on `5_7`: Failed to parse LLM output
  Evidence: []
- `semantic` on `5_21`: The two requirements refer to potentially different version fields: Requirement A describes a semantic version number designating the OAS feature set, while Requirement B specifies that the Info Object version field must represent the document version, not the spec version. If these refer to the same field, they conflict semantically. However, the text does not anchor them to the same artifact, so the overlap is ambiguous. Therefore, pair is uncertain without assuming identity.
  Evidence: ["the major.minor portion of the semantic version number", "the Info Object version field"]
- `logic` on `5_27`: Failed to parse LLM output
  Evidence: []
- `logic` on `6_7`: Failed to parse LLM output
  Evidence: []
- `logic` on `7_14`: Failed to parse LLM output
  Evidence: []
- `logic` on `7_19`: Failed to parse LLM output
  Evidence: []
- `logic` on `7_20`: Failed to parse LLM output
  Evidence: []
- `semantic` on `7_25`: Failed to parse LLM output
  Evidence: []
- `logic` on `7_25`: Failed to parse LLM output
  Evidence: []
- `logic` on `7_30`: Failed to parse LLM output
  Evidence: []
- `logic` on `7_45`: Failed to parse LLM output
  Evidence: []
- `logic` on `8_30`: Failed to parse LLM output
  Evidence: []
- `logic` on `9_52`: Failed to parse LLM output
  Evidence: []
- `logic` on `12_25`: Failed to parse LLM output
  Evidence: []
- `logic` on `12_49`: Failed to parse LLM output
  Evidence: []
- `semantic` on `12_52`: Failed to parse LLM output
  Evidence: []
- `semantic` on `13_27`: Failed to parse LLM output
  Evidence: []
- Additional abstention records: see `phase1_abstentions.jsonl` (37 total).
