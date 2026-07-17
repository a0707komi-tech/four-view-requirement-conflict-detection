from __future__ import annotations

import json

from conflict_detection.orchestration.session_types import CrossExamResult
from conflict_detection.runtime.artifacts.phase1_summary import MAX_LIST_ITEMS, MAX_REASONING_CHARS, MAX_TEXT_ITEM_CHARS
from conflict_detection.runtime.artifacts.schemas import (
    ArbiterInputBundle,
    DaChallengeCard,
    DaChallengeArtifact,
    Phase1SummaryBundle,
    RebuttalDeltaCard,
    RebuttalSummaryArtifact,
)


def build_da_challenge_artifact(cross_exam: CrossExamResult, *, pair_id: str) -> DaChallengeArtifact:
    da_verdict = cross_exam.da_verdict
    disagreements = _compact_mapped_items(da_verdict.get("disagreements", []), _disagreement_to_text)
    weak_assumptions = _compact_mapped_items(da_verdict.get("weak_assumptions", []), _weak_assumption_to_text)
    overlooked_factors = _compact_list(da_verdict.get("overlooked_factors", []))
    return DaChallengeArtifact(
        pair_id=pair_id,
        target_agent=str(da_verdict.get("target_agent", cross_exam.target_agent)),
        challenge=_compact_text(str(da_verdict.get("challenge", cross_exam.challenge)), limit=MAX_REASONING_CHARS),
        challenge_type=str(da_verdict.get("challenge_type", "")),
        reason=_compact_text(str(da_verdict.get("reason", "")), limit=MAX_REASONING_CHARS),
        disagreements=disagreements,
        weak_assumptions=weak_assumptions,
        overlooked_factors=overlooked_factors,
        challenge_card=DaChallengeCard(
            focus=_compact_text(
                str(da_verdict.get("reason", "")) or str(da_verdict.get("challenge_type", "")) or str(da_verdict.get("challenge", cross_exam.challenge)),
                limit=MAX_REASONING_CHARS,
            ),
            disagreement_points=disagreements,
            weak_assumption_points=weak_assumptions,
            overlooked_factors=overlooked_factors,
        ),
    )


def build_rebuttal_summary_artifact(cross_exam: CrossExamResult, *, pair_id: str) -> RebuttalSummaryArtifact:
    rebuttal = cross_exam.rebuttal
    revised_confidence = rebuttal.get("revised_confidence")
    return RebuttalSummaryArtifact(
        pair_id=pair_id,
        target_agent=cross_exam.target_agent,
        response_summary=_compact_text(str(rebuttal.get("response", "")), limit=MAX_REASONING_CHARS),
        verdict_revised=bool(rebuttal.get("verdict_revised", False)),
        revised_verdict=str(rebuttal.get("revised_verdict", "")),
        revised_confidence=None if revised_confidence in (None, "") else round(float(revised_confidence), 4),
        unresolved_issues=_compact_list(rebuttal.get("unresolved_issues", [])),
        delta_card=_build_rebuttal_delta_card(rebuttal),
    )


def build_arbiter_input_bundle(
    phase1_bundle: Phase1SummaryBundle,
    da_challenge: DaChallengeArtifact,
    rebuttal: RebuttalSummaryArtifact,
) -> ArbiterInputBundle:
    return ArbiterInputBundle(
        pair_id=phase1_bundle.pair_id,
        phase1_summaries=dict(phase1_bundle.summaries),
        da_challenge=da_challenge,
        rebuttal=rebuttal,
    )


def serialize_da_challenge(artifact: DaChallengeArtifact) -> str:
    payload = {
        "target_agent": artifact.target_agent,
        "challenge": artifact.challenge,
        "challenge_type": artifact.challenge_type,
        "challenge_card": artifact.challenge_card.to_dict(),
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def serialize_rebuttal_summary(artifact: RebuttalSummaryArtifact) -> str:
    payload = {
        "verdict_revised": artifact.verdict_revised,
        "revised_verdict": artifact.revised_verdict,
        "revised_confidence": artifact.revised_confidence,
        "delta_card": artifact.delta_card.to_dict(),
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _compact_mapped_items(values: object, mapper) -> tuple[str, ...]:
    if not isinstance(values, list):
        return ()
    result: list[str] = []
    for item in values[:MAX_LIST_ITEMS]:
        result.append(_compact_text(mapper(item), limit=MAX_TEXT_ITEM_CHARS))
    return tuple(result)


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


def _disagreement_to_text(item: object) -> str:
    if not isinstance(item, dict):
        return str(item)
    agents = item.get("agents", [])
    issue = item.get("issue", "")
    if isinstance(agents, list):
        joined_agents = " vs ".join(str(agent) for agent in agents[:2])
    else:
        joined_agents = str(agents)
    return f"{joined_agents}: {issue}".strip(": ")


def _weak_assumption_to_text(item: object) -> str:
    if not isinstance(item, dict):
        return str(item)
    agent = str(item.get("agent", ""))
    assumption = str(item.get("assumption", ""))
    why_weak = str(item.get("why_weak", ""))
    return f"{agent}: {assumption} ({why_weak})".strip()


def _build_rebuttal_delta_card(rebuttal: dict[str, object]) -> RebuttalDeltaCard:
    response_summary = _compact_text(str(rebuttal.get("response", "")), limit=MAX_REASONING_CHARS)
    unresolved_issues = _compact_list(rebuttal.get("unresolved_issues", []))
    revised_verdict = str(rebuttal.get("revised_verdict", ""))
    verdict_revised = bool(rebuttal.get("verdict_revised", False))
    if verdict_revised and revised_verdict:
        stance = f"revised:{revised_verdict}"
    elif verdict_revised:
        stance = "revised"
    else:
        stance = "maintained"
    response_points = _compact_list(rebuttal.get("response_points", []))
    if not response_points and response_summary:
        response_points = (response_summary,)
    return RebuttalDeltaCard(
        stance=stance,
        response_core=response_summary,
        response_points=response_points,
        remaining_gaps=unresolved_issues,
    )
