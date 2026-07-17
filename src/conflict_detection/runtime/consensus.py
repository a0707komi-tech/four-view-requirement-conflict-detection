from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from conflict_detection.orchestration.session_types import AgentDecision, DetectionPair
from conflict_detection.runtime.artifacts.schemas import Phase1SummaryArtifact

PHASE1_AGENT_NAMES = ("semantic", "logic", "feasibility", "goal")


@dataclass(frozen=True)
class StrictConsensusResult:
    verdict: str
    confidence: float


def evaluate_strict_consensus_from_decisions(
    pair: DetectionPair,
    decisions: Sequence[AgentDecision],
) -> StrictConsensusResult | None:
    del pair
    if len(decisions) != len(PHASE1_AGENT_NAMES):
        return None
    ordered = [decision for decision in decisions if decision.agent in PHASE1_AGENT_NAMES]
    if len(ordered) != len(PHASE1_AGENT_NAMES):
        return None
    return _evaluate_strict_consensus(ordered)


def evaluate_strict_consensus_from_summaries(
    pair: DetectionPair,
    summaries: dict[str, Phase1SummaryArtifact],
) -> StrictConsensusResult | None:
    del pair
    if len(summaries) != len(PHASE1_AGENT_NAMES):
        return None
    ordered = [summaries.get(agent_name) for agent_name in PHASE1_AGENT_NAMES]
    if any(summary is None for summary in ordered):
        return None
    return _evaluate_strict_consensus(ordered)


def _evaluate_strict_consensus(phase1_items) -> StrictConsensusResult | None:
    verdicts = [str(item.verdict) for item in phase1_items]
    if len(set(verdicts)) != 1:
        return None
    verdict = verdicts[0]
    if verdict not in {"compatible", "incompatible"}:
        return None
    confidences = [float(item.confidence) for item in phase1_items]
    return StrictConsensusResult(
        verdict=verdict,
        confidence=sum(confidences) / len(confidences),
    )
