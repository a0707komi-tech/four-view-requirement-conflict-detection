# Agent Interfaces

## Shared Pair Input

Every agent reasons about one pair containing `pair_id`, `r1_id`, `r1_text`, `r2_id`, and `r2_text`. Similarity scores are not sent to agents.

## Phase-1 Output

Phase-1 records contain:

- `verdict`: `compatible`, `incompatible`, or `uncertain`.
- `confidence`: numeric confidence.
- `reasoning`: concise view-specific justification.
- `key_evidence`: textual evidence supporting the verdict.
- `assumptions`: assumptions required by the analysis.
- `pairwise_conflict_grounded`: whether the conclusion is grounded in the relation between both requirements.

## View Responsibilities

- **Semantic:** interprets meaning, modality, scope, actors, objects, and conditions.
- **Logic:** checks propositions, negation, quantification, numeric constraints, and consistency.
- **Feasibility:** checks engineering, implementation, operational, resource, and platform constraints.
- **Goal:** examines stakeholder goals and goal-level interference as a supplementary view.

## DA and Rebuttal

DA selects a target view and states one grounded challenge. Rebuttal returns whether the target revises its verdict, its revised verdict when applicable, and remaining unresolved issues.

## Arbiter

The arbiter receives both original requirement texts and compact evidence from Phase-1, DA, and rebuttal. It returns the final verdict, confidence, reasoning, uncertainty source, and human-review flag.

Prompt templates and metadata are available under `src/conflict_detection/prompts`.
