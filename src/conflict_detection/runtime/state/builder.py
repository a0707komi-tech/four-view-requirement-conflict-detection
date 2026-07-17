from __future__ import annotations

from conflict_detection.orchestration.session_types import DetectionPair
from conflict_detection.runtime.consensus import evaluate_strict_consensus_from_summaries
from conflict_detection.runtime.artifacts.schemas import (
    DaChallengeArtifact,
    Phase1SummaryArtifact,
    RebuttalSummaryArtifact,
)
from conflict_detection.runtime.state.schemas import (
    DebateState,
    EvidenceState,
    FinalState,
    NextAction,
    PairWorkingMemory,
    Phase1State,
)

PHASE1_AGENT_NAMES = ("semantic", "logic", "feasibility", "goal")


def update_memory_after_phase1(
    memory: PairWorkingMemory | None,
    *,
    pair: DetectionPair,
    summary: Phase1SummaryArtifact,
    all_phase1_summaries: dict[str, Phase1SummaryArtifact] | None = None,
) -> PairWorkingMemory:
    existing = memory or PairWorkingMemory(pair_id=summary.pair_id)
    source_summaries = all_phase1_summaries or {summary.agent: summary}
    verdicts = {agent: item.verdict for agent, item in source_summaries.items()}
    confidences = {agent: float(item.confidence) for agent, item in source_summaries.items()}
    if not all_phase1_summaries:
        verdicts = dict(existing.phase1.verdicts) | verdicts
        confidences = dict(existing.phase1.confidences) | confidences
    bridge_assumptions_present = existing.evidence_state.bridge_assumptions_present or bool(summary.assumptions)
    all_agents_completed = all(agent in source_summaries for agent in PHASE1_AGENT_NAMES)
    consensus_verdict = ""
    strict_consensus = False
    consensus_result = None
    if all_agents_completed:
        consensus_result = evaluate_strict_consensus_from_summaries(pair, source_summaries)
        if consensus_result is not None:
            strict_consensus = True
            consensus_verdict = consensus_result.verdict

    evidence_state = EvidenceState(
        shared_scope_present="unknown",
        conflict_window_detected="unknown",
        coexistence_path_present="possible" if not strict_consensus else (
            "absent" if consensus_verdict == "incompatible" else "present"
        ),
        bridge_assumptions_present=bridge_assumptions_present,
        global_unsat_supported="strong" if consensus_verdict == "incompatible" else (
            "not_supported" if strict_consensus and consensus_verdict == "compatible" else "unknown"
        ),
    )
    phase1_state = Phase1State(
        verdicts=verdicts,
        confidences=confidences,
        all_agents_completed=all_agents_completed,
        strict_consensus=strict_consensus,
        strict_consensus_verdict=consensus_verdict,
    )
    debate_state = DebateState(
        da_needed=all_agents_completed and not strict_consensus,
        da_completed=False,
        target_agent=existing.debate_state.target_agent,
        challenge_present=existing.debate_state.challenge_present,
        rebuttal_completed=existing.debate_state.rebuttal_completed,
        verdict_revised=existing.debate_state.verdict_revised,
    )
    final_state = FinalState(
        arbiter_needed=all_agents_completed and not strict_consensus,
        human_review_recommended=False,
        final_verdict=consensus_verdict if strict_consensus else "",
    )
    return PairWorkingMemory(
        pair_id=summary.pair_id,
        current_stage="phase1",
        phase1=phase1_state,
        evidence_state=evidence_state,
        debate_state=debate_state,
        final_state=final_state,
        next_action=compute_next_action(
            current_stage="phase1",
            phase1=phase1_state,
            debate_state=debate_state,
            final_state=final_state,
        ),
    )


def update_memory_after_da(
    memory: PairWorkingMemory | None,
    *,
    challenge: DaChallengeArtifact,
) -> PairWorkingMemory:
    existing = memory or PairWorkingMemory(pair_id=challenge.pair_id)
    debate_state = DebateState(
        da_needed=existing.debate_state.da_needed,
        da_completed=True,
        target_agent=challenge.target_agent,
        challenge_present=bool(challenge.challenge.strip()),
        rebuttal_completed=False,
        verdict_revised=False,
    )
    final_state = FinalState(
        arbiter_needed=not existing.phase1.strict_consensus,
        human_review_recommended=False,
        final_verdict=existing.final_state.final_verdict,
    )
    return PairWorkingMemory(
        pair_id=challenge.pair_id,
        current_stage="da",
        phase1=existing.phase1,
        evidence_state=existing.evidence_state,
        debate_state=debate_state,
        final_state=final_state,
        next_action=compute_next_action(
            current_stage="da",
            phase1=existing.phase1,
            debate_state=debate_state,
            final_state=final_state,
        ),
    )


def update_memory_after_rebuttal(
    memory: PairWorkingMemory | None,
    *,
    rebuttal: RebuttalSummaryArtifact,
) -> PairWorkingMemory:
    existing = memory or PairWorkingMemory(pair_id=rebuttal.pair_id)
    debate_state = DebateState(
        da_needed=existing.debate_state.da_needed,
        da_completed=existing.debate_state.da_completed,
        target_agent=rebuttal.target_agent or existing.debate_state.target_agent,
        challenge_present=existing.debate_state.challenge_present,
        rebuttal_completed=True,
        verdict_revised=bool(rebuttal.verdict_revised),
    )
    final_state = FinalState(
        arbiter_needed=not existing.phase1.strict_consensus,
        human_review_recommended=bool(rebuttal.unresolved_issues),
        final_verdict=existing.final_state.final_verdict,
    )
    return PairWorkingMemory(
        pair_id=rebuttal.pair_id,
        current_stage="rebuttal",
        phase1=existing.phase1,
        evidence_state=existing.evidence_state,
        debate_state=debate_state,
        final_state=final_state,
        next_action=compute_next_action(
            current_stage="rebuttal",
            phase1=existing.phase1,
            debate_state=debate_state,
            final_state=final_state,
        ),
    )


def update_memory_after_arbiter(
    memory: PairWorkingMemory | None,
    *,
    pair_id: str,
    arbiter_output: dict[str, object],
) -> PairWorkingMemory:
    existing = memory or PairWorkingMemory(pair_id=pair_id)
    final_state = FinalState(
        arbiter_needed=False,
        human_review_recommended=bool(arbiter_output.get("needs_human_review", False)),
        final_verdict=str(arbiter_output.get("verdict", "")),
    )
    return PairWorkingMemory(
        pair_id=pair_id,
        current_stage="arbiter",
        phase1=existing.phase1,
        evidence_state=existing.evidence_state,
        debate_state=existing.debate_state,
        final_state=final_state,
        next_action=compute_next_action(
            current_stage="arbiter",
            phase1=existing.phase1,
            debate_state=existing.debate_state,
            final_state=final_state,
        ),
    )


def compute_next_action(
    *,
    current_stage: str,
    phase1: Phase1State,
    debate_state: DebateState,
    final_state: FinalState,
) -> NextAction:
    if current_stage == "phase1":
        if not phase1.all_agents_completed:
            return NextAction.RUN_PHASE1
        if phase1.strict_consensus:
            return NextAction.SKIP_TO_FINALIZE_CONSENSUS
        return NextAction.RUN_DA
    if current_stage == "da":
        if debate_state.da_completed and debate_state.challenge_present:
            return NextAction.RUN_REBUTTAL
        return NextAction.HALT_ERROR
    if current_stage == "rebuttal":
        if debate_state.rebuttal_completed:
            return NextAction.RUN_ARBITER
        return NextAction.HALT_ERROR
    if current_stage == "arbiter":
        if final_state.human_review_recommended:
            return NextAction.NEEDS_HUMAN_REVIEW
        return NextAction.FINALIZE
    return NextAction.RUN_PHASE1
