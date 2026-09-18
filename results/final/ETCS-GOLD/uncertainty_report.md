# Uncertainty and Abstention Report: ETCS-GOLD

This report is generated offline from the stored final verdicts and agent records. It does not call any model API.

## Scope and Denominators

- Final verdict rows: **1599**.
- Canonical candidate rows with Phase-1 execution: **778**.
- Final uncertainty rate uses all final verdict rows, including canonical aliases and duplicate routes.
- Duplicate-group rows are shown as a separate route because the historical final artifact stores them as `incompatible` with `duplicate_conflict=true`; conflict metrics exclude them.
- View-level abstention rates use canonical candidate rows only; aliases inherit a result and are not counted as new view decisions.

## Final Outcomes

| Outcome | Count | Rate |
| --- | ---: | ---: |
| `compatible` | 1420 | 88.81% |
| `incompatible` | 82 | 5.13% |
| `uncertain` | 97 | 6.07% |
| `duplicate_group_rule` route (subset of incompatible) | 20 | subset |

## Uncertainty and Human Review

| Measure | Count | Rate |
| --- | ---: | ---: |
| Final `uncertain` | 97 | 6.07% of final rows |
| `needs_human_review=true` among uncertain rows | 95 | 97.94% of uncertain rows |
| Uncertain rows without review flag | 2 | - |
| Recommended review queue | 97 rows / 50 unique units | all final uncertain rows |

Uncertainty is reported exactly as stored. The legacy `needs_human_review` value is retained for provenance, but the reporting policy sends every final uncertain verdict to review. Canonical aliases share their source pair's review unit.

## Final Uncertainty by Route and Stage

| Dimension | Count |
| --- | ---: |
| Route `canonical_candidate` | 50 |
| Route `canonical_alias` | 47 |
| Stage `canonical_candidate` | 50 |
| Stage `canonical_alias` | 47 |

## Phase-1 View Abstention

| View | Evaluated | Uncertain | Rate | Single-view | Multi-view | DA target | Final C | Final I | Final U |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| semantic | 778 | 59 | 7.58% | 36 | 23 | 2 | 27 | 7 | 25 |
| logic | 778 | 94 | 12.08% | 70 | 24 | 25 | 57 | 5 | 32 |
| feasibility | 778 | 12 | 1.54% | 7 | 5 | 6 | 7 | 2 | 3 |
| goal | 778 | 2 | 0.26% | 1 | 1 | 1 | 2 | 0 | 0 |

`Single-view` means that this was the only Phase-1 view to abstain; `multi-view` means at least one other view also abstained. `Final C/I/U` reports the final compatible, incompatible, or uncertain outcome after disagreement handling for the pairs on which that view abstained.

Canonical candidate pairs with at least one Phase-1 abstention: **139** (17.87%).

## Phase-1 Vote Patterns

| Vote pattern | Count |
| --- | ---: |
| `semantic=compatible; logic=compatible; feasibility=compatible; goal=compatible` | 572 |
| `semantic=compatible; logic=uncertain; feasibility=compatible; goal=compatible` | 47 |
| `semantic=incompatible; logic=incompatible; feasibility=incompatible; goal=incompatible` | 20 |
| `semantic=uncertain; logic=compatible; feasibility=compatible; goal=compatible` | 15 |
| `semantic=compatible; logic=compatible; feasibility=compatible; goal=incompatible` | 10 |
| `semantic=compatible; logic=compatible; feasibility=incompatible; goal=incompatible` | 8 |
| `semantic=compatible; logic=uncertain; feasibility=incompatible; goal=incompatible` | 8 |
| `semantic=uncertain; logic=compatible; feasibility=compatible; goal=incompatible` | 8 |
| `semantic=uncertain; logic=uncertain; feasibility=incompatible; goal=incompatible` | 7 |
| `semantic=uncertain; logic=uncertain; feasibility=compatible; goal=compatible` | 7 |
| `semantic=compatible; logic=compatible; feasibility=uncertain; goal=compatible` | 6 |
| `semantic=incompatible; logic=uncertain; feasibility=incompatible; goal=incompatible` | 6 |
| `semantic=incompatible; logic=incompatible; feasibility=compatible; goal=incompatible` | 6 |
| `semantic=compatible; logic=uncertain; feasibility=incompatible; goal=compatible` | 5 |
| `semantic=incompatible; logic=compatible; feasibility=incompatible; goal=incompatible` | 5 |
| `semantic=compatible; logic=compatible; feasibility=incompatible; goal=compatible` | 4 |
| `semantic=compatible; logic=uncertain; feasibility=compatible; goal=incompatible` | 4 |
| `semantic=uncertain; logic=incompatible; feasibility=incompatible; goal=incompatible` | 4 |
| `semantic=uncertain; logic=uncertain; feasibility=compatible; goal=incompatible` | 4 |
| `semantic=uncertain; logic=incompatible; feasibility=compatible; goal=incompatible` | 3 |
| `semantic=incompatible; logic=incompatible; feasibility=compatible; goal=compatible` | 3 |
| `semantic=incompatible; logic=compatible; feasibility=compatible; goal=compatible` | 3 |
| `semantic=compatible; logic=incompatible; feasibility=compatible; goal=compatible` | 3 |
| `semantic=uncertain; logic=compatible; feasibility=incompatible; goal=incompatible` | 3 |
| `semantic=uncertain; logic=incompatible; feasibility=compatible; goal=compatible` | 3 |
| `semantic=uncertain; logic=uncertain; feasibility=incompatible; goal=compatible` | 2 |
| `semantic=compatible; logic=incompatible; feasibility=incompatible; goal=incompatible` | 2 |
| `semantic=incompatible; logic=incompatible; feasibility=uncertain; goal=incompatible` | 1 |
| `semantic=compatible; logic=compatible; feasibility=compatible; goal=uncertain` | 1 |
| `semantic=uncertain; logic=incompatible; feasibility=uncertain; goal=compatible` | 1 |
| `semantic=incompatible; logic=compatible; feasibility=incompatible; goal=compatible` | 1 |
| `semantic=uncertain; logic=uncertain; feasibility=uncertain; goal=compatible` | 1 |
| `semantic=compatible; logic=incompatible; feasibility=compatible; goal=incompatible` | 1 |
| `semantic=compatible; logic=uncertain; feasibility=uncertain; goal=uncertain` | 1 |
| `semantic=uncertain; logic=uncertain; feasibility=uncertain; goal=incompatible` | 1 |
| `semantic=incompatible; logic=compatible; feasibility=compatible; goal=incompatible` | 1 |
| `semantic=compatible; logic=uncertain; feasibility=uncertain; goal=incompatible` | 1 |

## Stored Uncertainty Sources

| Source | Count |
| --- | ---: |
| unverifiable_assumption | 55 |
| missing_domain_knowledge | 22 |
| ambiguous_requirement | 18 |
| verifiable_assumption | 2 |

## Representative Final Uncertain Cases

### 1_61

- Route: `canonical_candidate`; confidence: `0.78`; human review flag: `True`.
- Stored uncertainty source: unverifiable_assumption.
- Phase-1 votes: `{"semantic": {"verdict": "uncertain", "confidence": 0.3, "model": "deepseek-v4-flash"}, "logic": {"verdict": "incompatible", "confidence": 0.95, "model": "deepseek-v4-pro"}, "feasibility": {"verdict": "compatible", "confidence": 0.95, "model": "kimi-k2.6"}, "goal": {"verdict": "incompatible", "confidence": 0.95, "model": "qwen3.7-plus"}}`.
- Cross-examination: {"target": "logic", "challenge": "You assume operational status is 'information to allow him to drive the train safely.' What in the requirement text grounds that equivalence, and how do you rule out non-safety-related status displays?", "rebuttal_verdict_revised": true}.
- Arbiter reasoning: The pair is textually anchored to driver-facing information, but no conflict is established from the text alone. A requires the current operational status to be shown on the DMI. B restricts ETCS from providing information that allows safe driving unless speed is below 400 km/h. The decisive missing premise is whether A’s “current operational status” is, in this pair, ETCS-provided safe-driving information covered by B. The strongest incompatibility arguments depended on that assumption and were later withdrawn. The strongest compatibility story also depends on assuming operational status is outside B’s restricted class. Because that classification is unresolved by the pair text, interference/inconsistency is not proven..

### 3_10

- Route: `canonical_candidate`; confidence: `0.86`; human review flag: `True`.
- Stored uncertainty source: unverifiable_assumption.
- Phase-1 votes: `{"semantic": {"verdict": "uncertain", "confidence": 0.3, "model": "deepseek-v4-flash"}, "logic": {"verdict": "uncertain", "confidence": 0.3, "model": "deepseek-v4-pro"}, "feasibility": {"verdict": "incompatible", "confidence": 0.95, "model": "kimi-k2.6"}, "goal": {"verdict": "incompatible", "confidence": 1.0, "model": "qwen3.7-plus"}}`.
- Cross-examination: {"target": "feasibility", "challenge": "You assume Requirement A mandates ETCS to use radio, but the text only says 'Basic track to train... via radio' without specifying ETCS as the provider. What text grounds your assumption that both requirements target the same system?", "rebuttal_verdict_revised": true}.
- Arbiter reasoning: The pair is textually anchored to the same capability: track-to-train and train-to-track information via continuous radio. If both applied to ETCS, they would be inconsistent, because A affirms that radio-based exchange is a basic function while B says ETCS shall not be required to provide that function. But the decisive scope premise is missing: A never names ETCS, while B does. A may describe a broader or different system, so the conflict cannot be conclusively grounded from the pair text alone..

### 4_61

- Route: `canonical_candidate`; confidence: `0.83`; human review flag: `True`.
- Stored uncertainty source: unverifiable_assumption.
- Phase-1 votes: `{"semantic": {"verdict": "compatible", "confidence": 0.95, "model": "deepseek-v4-flash"}, "logic": {"verdict": "incompatible", "confidence": 0.95, "model": "deepseek-v4-pro"}, "feasibility": {"verdict": "compatible", "confidence": 0.95, "model": "kimi-k2.6"}, "goal": {"verdict": "compatible", "confidence": 0.95, "model": "qwen3.7-plus"}}`.
- Cross-examination: {"target": "logic", "challenge": "You assume an acknowledgment request is 'information to allow him to drive the train safely.' Where in the text is that equivalence grounded, and why isn't it equally plausible that the request is a procedural command outside that safety-information scope?", "rebuttal_verdict_revised": true}.
- Arbiter reasoning: The pair is only weakly anchored through possible driver-facing information. Requirement A governs acknowledgement/brake behavior for level transitions requested from trackside; Requirement B limits what ETCS may provide to the driver above 400 km/h. A conflict is not textually established because A never says ETCS provides the acknowledgement request, nor that the request is the kind of 'information to allow him to drive the train safely' covered by B. But compatibility is also not decisively grounded, because that same linkage is plausible. Since whether interference exists depends on those unresolved assumptions, the strongest surviving synthesis is uncertain..

### 5_7

- Route: `canonical_candidate`; confidence: `0.77`; human review flag: `True`.
- Stored uncertainty source: unverifiable_assumption.
- Phase-1 votes: `{"semantic": {"verdict": "incompatible", "confidence": 0.95, "model": "deepseek-v4-flash"}, "logic": {"verdict": "compatible", "confidence": 0.9, "model": "deepseek-v4-pro"}, "feasibility": {"verdict": "incompatible", "confidence": 0.85, "model": "kimi-k2.6"}, "goal": {"verdict": "incompatible", "confidence": 0.95, "model": "qwen3.7-plus"}}`.
- Cross-examination: {"target": "logic", "challenge": "You treat 'in principle' as a general exception mechanism, but what text in Requirement B explicitly permits an exception for STM transitions that require driver acknowledgement?", "rebuttal_verdict_revised": false}.
- Arbiter reasoning: The pair is anchored to the same subject—transition behavior—but only overlaps if transitions to/from STM can occur while the train is moving. Requirement A requires driver acknowledgement for STM transitions; Requirement B says moving transitions shall in principle occur automatically. That suggests potential interference on the same mechanism, but the conflict is not fully established from the text alone because A does not say those STM transitions happen while moving, and B applies only in that operating condition. Also, B’s qualifier “in principle” weakens an absolute inconsistency claim. So a conflict is plausible, but a decisive text-grounded overlap premise is missing..

### 5_8

- Route: `canonical_candidate`; confidence: `0.84`; human review flag: `True`.
- Stored uncertainty source: missing_domain_knowledge.
- Phase-1 votes: `{"semantic": {"verdict": "uncertain", "confidence": 0.6, "model": "deepseek-v4-flash"}, "logic": {"verdict": "uncertain", "confidence": 0.3, "model": "deepseek-v4-pro"}, "feasibility": {"verdict": "incompatible", "confidence": 0.95, "model": "kimi-k2.6"}, "goal": {"verdict": "incompatible", "confidence": 0.95, "model": "qwen3.7-plus"}}`.
- Cross-examination: {"target": "goal", "challenge": "You assume STM transitions are a subset of level transitions. Where in the requirement pair text is that subset relation explicitly stated or necessarily implied?", "rebuttal_verdict_revised": true}.
- Arbiter reasoning: The apparent clash is strong only if transitions to/from national Operation (STM) are also “level transitions.” If they are, A requires driver acknowledgement while B forbids any driver input, creating a direct inconsistency over the same transition event. But that overlap is not established by the pair text itself. A is anchored to STM transitions; B is anchored to level transitions. Since the decisive premise that these are the same operational class is missing, neither incompatibility nor compatibility is fully grounded from the text alone..

### 5_13

- Route: `canonical_candidate`; confidence: `0.77`; human review flag: `True`.
- Stored uncertainty source: unverifiable_assumption.
- Phase-1 votes: `{"semantic": {"verdict": "uncertain", "confidence": 0.3, "model": "deepseek-v4-flash"}, "logic": {"verdict": "uncertain", "confidence": 0.3, "model": "deepseek-v4-pro"}, "feasibility": {"verdict": "incompatible", "confidence": 0.95, "model": "kimi-k2.6"}, "goal": {"verdict": "compatible", "confidence": 0.95, "model": "qwen3.7-plus"}}`.
- Cross-examination: {"target": "feasibility", "challenge": "You equate 'transitions to and from national Operation (STM)' with 'compatibility with national systems.' What text in Requirement A proves the ETCS must be compatible with, rather than merely interface during a transition from, those national systems?", "rebuttal_verdict_revised": true}.
- Arbiter reasoning: The pair overlaps on ETCS and a national-operation context, but no conflict is textually established. A requires a driver acknowledgement request during transitions to and from national Operation (STM). B forbids ETCS compatibility with national systems listed in the CCS TSI. The strongest incompatibility claim depends on an unstated premise that handling STM transitions necessarily requires compatibility with those listed national systems. The surviving compatible reading is also not fully decisive because the text does not clarify whether STM in A is one of the national systems covered by B. Without that missing premise, interference, inconsistency, or impossible joint satisfaction is not proven from the pair alone..

### 5_14

- Route: `canonical_alias`; confidence: `0.77`; human review flag: `True`.
- Stored uncertainty source: unverifiable_assumption.
- Phase-1 votes: `{"semantic": {"verdict": "incompatible", "confidence": 0.95, "model": "deepseek-v4-flash"}, "logic": {"verdict": "compatible", "confidence": 0.9, "model": "deepseek-v4-pro"}, "feasibility": {"verdict": "incompatible", "confidence": 0.85, "model": "kimi-k2.6"}, "goal": {"verdict": "incompatible", "confidence": 0.95, "model": "qwen3.7-plus"}}`.
- Cross-examination: {"target": "logic", "challenge": "You treat 'in principle' as a general exception mechanism, but what text in Requirement B explicitly permits an exception for STM transitions that require driver acknowledgement?", "rebuttal_verdict_revised": false}.
- Arbiter reasoning: The pair is anchored to the same subject—transition behavior—but only overlaps if transitions to/from STM can occur while the train is moving. Requirement A requires driver acknowledgement for STM transitions; Requirement B says moving transitions shall in principle occur automatically. That suggests potential interference on the same mechanism, but the conflict is not fully established from the text alone because A does not say those STM transitions happen while moving, and B applies only in that operating condition. Also, B’s qualifier “in principle” weakens an absolute inconsistency claim. So a conflict is plausible, but a decisive text-grounded overlap premise is missing..

### 5_34

- Route: `canonical_candidate`; confidence: `0.77`; human review flag: `True`.
- Stored uncertainty source: ambiguous_requirement.
- Phase-1 votes: `{"semantic": {"verdict": "uncertain", "confidence": 0.3, "model": "deepseek-v4-flash"}, "logic": {"verdict": "compatible", "confidence": 0.9, "model": "deepseek-v4-pro"}, "feasibility": {"verdict": "compatible", "confidence": 0.85, "model": "kimi-k2.6"}, "goal": {"verdict": "compatible", "confidence": 0.95, "model": "qwen3.7-plus"}}`.
- Cross-examination: {"target": "goal", "challenge": "You assume acknowledgement is a post-initiation action that does not preclude automatic initiation. Where in the requirement texts is this temporal separation grounded, and how do you rule out that acknowledgement is part of the initiation itself?", "rebuttal_verdict_revised": true}.
- Arbiter reasoning: The pair is textually anchored to an overlapping case: STM transitions that occur while the train is stationary. A requires ETCS to request driver acknowledgement for STM transitions; B requires stationary transitions to be initiated automatically or manually as appropriate. No direct conflict is stated unless 'driver acknowledgement' is treated as part of initiation or 'automatic initiation' is read to exclude any required driver action. The text itself does not define that relationship. The compatible reading relies on a stage split (automatic initiation, later acknowledgement), but that split is not clearly grounded in the pair. Because the conflict turns on an unresolved assumption about initiation versus acknowledgement, the safest judgment is uncertain..

### 5_37

- Route: `canonical_candidate`; confidence: `0.73`; human review flag: `True`.
- Stored uncertainty source: unverifiable_assumption.
- Phase-1 votes: `{"semantic": {"verdict": "compatible", "confidence": 1.0, "model": "deepseek-v4-flash"}, "logic": {"verdict": "uncertain", "confidence": 0.3, "model": "deepseek-v4-pro"}, "feasibility": {"verdict": "compatible", "confidence": 0.95, "model": "kimi-k2.6"}, "goal": {"verdict": "compatible", "confidence": 0.95, "model": "qwen3.7-plus"}}`.
- Cross-examination: {"target": "logic", "challenge": "You assume transitions may occur above 100 km/h, but the text does not state that. Why is this unsupported assumption decisive for 'uncertain' rather than concluding no conflict is grounded?", "rebuttal_verdict_revised": false}.
- Arbiter reasoning: The pair is anchored to the same system (ETCS), but not to a clearly shared operating condition. A appears to require ETCS to request driver acknowledgement for STM transitions in general, while B limits ETCS functionality to speeds at or below 100 km/h. A text-grounded conflict would arise only if STM transitions must or may occur above 100 km/h, because ETCS then could not perform A. The pair itself does not state transition speeds or whether A is implicitly limited to ETCS’s functional envelope. Since both compatibility and incompatibility hinge on that unresolved premise, no conflict relation is decisively grounded from the pair alone..

### 5_48

- Route: `canonical_alias`; confidence: `0.77`; human review flag: `True`.
- Stored uncertainty source: ambiguous_requirement.
- Phase-1 votes: `{"semantic": {"verdict": "uncertain", "confidence": 0.3, "model": "deepseek-v4-flash"}, "logic": {"verdict": "compatible", "confidence": 0.9, "model": "deepseek-v4-pro"}, "feasibility": {"verdict": "compatible", "confidence": 0.85, "model": "kimi-k2.6"}, "goal": {"verdict": "compatible", "confidence": 0.95, "model": "qwen3.7-plus"}}`.
- Cross-examination: {"target": "goal", "challenge": "You assume acknowledgement is a post-initiation action that does not preclude automatic initiation. Where in the requirement texts is this temporal separation grounded, and how do you rule out that acknowledgement is part of the initiation itself?", "rebuttal_verdict_revised": true}.
- Arbiter reasoning: The pair is textually anchored to an overlapping case: STM transitions that occur while the train is stationary. A requires ETCS to request driver acknowledgement for STM transitions; B requires stationary transitions to be initiated automatically or manually as appropriate. No direct conflict is stated unless 'driver acknowledgement' is treated as part of initiation or 'automatic initiation' is read to exclude any required driver action. The text itself does not define that relationship. The compatible reading relies on a stage split (automatic initiation, later acknowledgement), but that split is not clearly grounded in the pair. Because the conflict turns on an unresolved assumption about initiation versus acknowledgement, the safest judgment is uncertain..


## Phase-1 Abstention Evidence

- `semantic` on `1_61`: Failed to parse LLM output
  Evidence: []
- `semantic` on `2_42`: Failed to parse LLM output
  Evidence: []
- `logic` on `3_7`: Failed to parse LLM output
  Evidence: []
- `semantic` on `3_10`: Failed to parse LLM output
  Evidence: []
- `logic` on `3_10`: Failed to parse LLM output
  Evidence: []
- `logic` on `3_26`: Failed to parse LLM output
  Evidence: []
- `semantic` on `4_5`: The two requirements address different transition types: 'level transitions' (Req A) versus 'transitions to/from national Operation (STM)' (Req B). They are not textually anchored to the same target, so no direct semantic interference or inconsistency can be established. However, without clarifying the relationship between these transition types, partial overlap remains possible, making the conflict status uncertain.
  Evidence: ["level transitions", "transitions to and from national Operation (STM)"]
- `logic` on `4_9`: Failed to parse LLM output
  Evidence: []
- `logic` on `4_28`: Failed to parse LLM output
  Evidence: []
- `semantic` on `5_8`: Both requirements concern ETCS transitions and driver actions, but the anchors differ: A explicitly targets transitions to/from STM, while B targets level transitions. Without text ensuring these sets overlap, the apparent conflict between requiring driver acknowledgement (A) and forbidding driver input (B) depends on an unstated overlap assumption. Thus, a decisive conflict relation cannot be confirmed from the pair text alone.
  Evidence: ["transitions to and from national Operation (STM)", "level transitions"]
- `logic` on `5_8`: Failed to parse LLM output
  Evidence: []
- `logic` on `5_10`: Failed to parse LLM output
  Evidence: []
- `semantic` on `5_13`: Failed to parse LLM output
  Evidence: []
- `logic` on `5_13`: Failed to parse LLM output
  Evidence: []
- `semantic` on `5_25`: Both requirements address ETCS but target different functions. A mandates driver acknowledgement requests during transitions to/from national Operation (STM). B prohibits ETCS from supervising train or shunting movements. Without explicit textual link, it is unclear whether requesting acknowledgement constitutes supervision. A plausible reading separates these actions, removing conflict. Thus, semantic interference or inconsistency cannot be definitively established from the pair text alone.
  Evidence: ["shall request, an acknowledgement by the driver", "shall not be able to supervise train or shunting movements"]
- `semantic` on `5_34`: Failed to parse LLM output
  Evidence: []
- `logic` on `5_35`: Failed to parse LLM output
  Evidence: []
- `logic` on `5_37`: The pair does not share an explicit speed condition for transitions. A requires driver acknowledgement during STM transitions; B limits ETCS functionality to ≤100 km/h. A conflict exists only if transitions can occur above 100 km/h, but nothing in the text requires or prohibits that. Without that condition, the requirements may be reconcilable (e.g., transitions always happen below 100 km/h). Thus, the conflict is not text-grounded.
  Evidence: ["For transitions to and from national Operation (STM) the ETCS shall request, an acknowledgement by the driver.", "ETCS shall only be functional up to a maximum train speed of 100 km/h."]
- `semantic` on `5_52`: Failed to parse LLM output
  Evidence: []
- `logic` on `5_58`: Failed to parse LLM output
  Evidence: []
- Additional abstention records: see `phase1_abstentions.jsonl` (167 total).
