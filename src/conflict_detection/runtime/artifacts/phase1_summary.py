from __future__ import annotations

import json
import re

from conflict_detection.orchestration.session_types import AgentDecision
from conflict_detection.runtime.artifacts.schemas import (
    Phase1AngleCard,
    Phase1SummaryArtifact,
    Phase1SummaryBundle,
)

MAX_REASONING_CHARS = 320
MAX_TEXT_ITEM_CHARS = 160
MAX_LIST_ITEMS = 2


def build_phase1_summary(decision: AgentDecision, *, pair_id: str) -> Phase1SummaryArtifact:
    return Phase1SummaryArtifact(
        pair_id=pair_id,
        agent=decision.agent,
        model=decision.model,
        verdict=decision.verdict,
        confidence=round(float(decision.confidence), 4),
        pairwise_conflict_grounded=bool(decision.pairwise_conflict_grounded),
        reasoning_summary=_compact_text(decision.reasoning, limit=MAX_REASONING_CHARS),
        key_evidence=_compact_list(decision.key_evidence),
        assumptions=_compact_list(decision.assumptions),
        angle_card=_build_angle_card(decision),
    )


def build_phase1_summary_bundle(
    decisions: list[AgentDecision],
    *,
    pair_id: str,
) -> Phase1SummaryBundle:
    return Phase1SummaryBundle(
        pair_id=pair_id,
        summaries={decision.agent: build_phase1_summary(decision, pair_id=pair_id) for decision in decisions},
    )


def serialize_phase1_summary(summary: Phase1SummaryArtifact) -> str:
    payload = {
        "verdict": summary.verdict,
        "confidence": round(float(summary.confidence), 4),
        "pairwise_conflict_grounded": summary.pairwise_conflict_grounded,
        "angle_card": summary.angle_card.to_dict(),
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _compact_list(values: object) -> tuple[str, ...]:
    if not isinstance(values, list):
        return ()
    result: list[str] = []
    for item in values[:MAX_LIST_ITEMS]:
        result.append(_compact_text(str(item), limit=MAX_TEXT_ITEM_CHARS))
    return tuple(result)


def _compact_text(text: str, *, limit: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _build_angle_card(decision: AgentDecision) -> Phase1AngleCard:
    raw_json = decision.raw_json if isinstance(decision.raw_json, dict) else {}
    summary = _compact_text(
        str(raw_json.get("reasoning_summary") or raw_json.get("reasoning") or decision.reasoning),
        limit=MAX_REASONING_CHARS,
    )
    key_evidence = _compact_list(raw_json.get("key_evidence", decision.key_evidence))
    assumptions = _compact_list(raw_json.get("assumptions", decision.assumptions))
    shared_state = _extract_shared_state(raw_json, summary)
    coexistence_path = _extract_coexistence_path(raw_json, summary, decision.verdict)
    decision_basis = _extract_decision_basis(raw_json, key_evidence, summary)
    global_test_note = _extract_global_test_note(
        raw_json=raw_json,
        summary=summary,
        verdict=decision.verdict,
        pairwise_conflict_grounded=decision.pairwise_conflict_grounded,
        assumptions=assumptions,
    )
    return Phase1AngleCard(
        summary=summary,
        shared_state=shared_state,
        decision_basis=decision_basis,
        coexistence_path=coexistence_path,
        hidden_assumptions=assumptions,
        global_test_note=global_test_note,
    )


def _extract_shared_state(raw_json: dict[str, object], summary: str) -> str:
    candidates = (
        raw_json.get("shared_state"),
        raw_json.get("overlap_state"),
        raw_json.get("overlapping_state"),
        raw_json.get("contradiction_state"),
        raw_json.get("critical_condition"),
    )
    for candidate in candidates:
        compact = _compact_scalar(candidate, limit=MAX_TEXT_ITEM_CHARS)
        if compact:
            return compact
    extracted = _sentence_after_marker(summary, ("shared state", "overlapping state", "same state", "both apply"))
    return extracted


def _extract_coexistence_path(raw_json: dict[str, object], summary: str, verdict: str) -> tuple[str, ...]:
    for key in ("coexistence_state", "coexistence_path", "compatible_path", "satisfying_path"):
        values = _as_string_tuple(raw_json.get(key))
        if values:
            return _compact_strings(values)
    if verdict == "incompatible":
        return ()
    inferred = _sentence_after_marker(
        summary,
        ("coexist", "both can", "another plausible", "allow both", "can still satisfy"),
    )
    return (inferred,) if inferred else ()


def _extract_decision_basis(
    raw_json: dict[str, object],
    key_evidence: tuple[str, ...],
    summary: str,
) -> tuple[str, ...]:
    for key in ("conflict_basis", "decision_basis", "critical_facts", "basis"):
        values = _as_string_tuple(raw_json.get(key))
        if values:
            return _compact_strings(values)
    if key_evidence:
        return key_evidence
    inferred = _sentence_after_marker(summary, ("because", "due to", "since"))
    return (inferred,) if inferred else ()


def _extract_global_test_note(
    *,
    raw_json: dict[str, object],
    summary: str,
    verdict: str,
    pairwise_conflict_grounded: bool,
    assumptions: tuple[str, ...],
) -> str:
    for key in ("global_test_note", "why_not_global_unsat", "global_satisfiability_check"):
        compact = _compact_scalar(raw_json.get(key), limit=MAX_REASONING_CHARS)
        if compact:
            return compact
    if re.search(r"\bno implementation\b|\bcannot both be satisfied\b|\bmutually exclusive\b", summary, flags=re.I):
        return _compact_text(summary, limit=MAX_REASONING_CHARS)
    if not pairwise_conflict_grounded:
        return "No single forced shared conflict state was grounded from the pair alone."
    if verdict == "compatible":
        return "The analysis leaves at least one text-grounded coexistence path open."
    if verdict == "incompatible" and assumptions:
        return "The incompatibility claim still depends on listed assumptions; global unsatisfiability is not separately proven."
    if verdict == "incompatible":
        return "The incompatibility claim is asserted, but a separate all-path failure proof is not explicitly captured."
    return "The analysis does not establish a global no-solution proof."


def _compact_scalar(value: object, *, limit: int) -> str:
    if value is None:
        return ""
    return _compact_text(str(value), limit=limit)


def _as_string_tuple(value: object) -> tuple[str, ...]:
    if isinstance(value, list):
        return tuple(str(item) for item in value if str(item).strip())
    if isinstance(value, str) and value.strip():
        return (value,)
    return ()


def _compact_strings(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(_compact_text(value, limit=MAX_TEXT_ITEM_CHARS) for value in values[:MAX_LIST_ITEMS])


def _sentence_after_marker(text: str, markers: tuple[str, ...]) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
    for sentence in sentences:
        lowered = sentence.lower()
        if any(marker in lowered for marker in markers):
            return _compact_text(sentence, limit=MAX_TEXT_ITEM_CHARS)
    return ""
