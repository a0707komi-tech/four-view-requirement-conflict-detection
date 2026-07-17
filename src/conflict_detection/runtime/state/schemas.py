from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class NextAction(StrEnum):
    RUN_PHASE1 = "run_phase1"
    SKIP_TO_FINALIZE_CONSENSUS = "skip_to_finalize_consensus"
    RUN_DA = "run_da"
    RUN_REBUTTAL = "run_rebuttal"
    RUN_ARBITER = "run_arbiter"
    FINALIZE = "finalize"
    NEEDS_HUMAN_REVIEW = "needs_human_review"
    RETRY_CURRENT_STAGE = "retry_current_stage"
    HALT_ERROR = "halt_error"


@dataclass(frozen=True)
class Phase1State:
    verdicts: dict[str, str] = field(default_factory=dict)
    confidences: dict[str, float] = field(default_factory=dict)
    all_agents_completed: bool = False
    strict_consensus: bool = False
    strict_consensus_verdict: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Phase1State":
        return cls(
            verdicts={str(k): str(v) for k, v in dict(payload.get("verdicts", {})).items()},
            confidences={str(k): float(v) for k, v in dict(payload.get("confidences", {})).items()},
            all_agents_completed=bool(payload.get("all_agents_completed", False)),
            strict_consensus=bool(payload.get("strict_consensus", False)),
            strict_consensus_verdict=str(payload.get("strict_consensus_verdict", "")),
        )


@dataclass(frozen=True)
class EvidenceState:
    shared_scope_present: str = "unknown"
    conflict_window_detected: str = "unknown"
    coexistence_path_present: str = "unknown"
    bridge_assumptions_present: bool = False
    global_unsat_supported: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EvidenceState":
        return cls(
            shared_scope_present=str(payload.get("shared_scope_present", "unknown")),
            conflict_window_detected=str(payload.get("conflict_window_detected", "unknown")),
            coexistence_path_present=str(payload.get("coexistence_path_present", "unknown")),
            bridge_assumptions_present=bool(payload.get("bridge_assumptions_present", False)),
            global_unsat_supported=str(payload.get("global_unsat_supported", "unknown")),
        )


@dataclass(frozen=True)
class DebateState:
    da_needed: bool = False
    da_completed: bool = False
    target_agent: str = ""
    challenge_present: bool = False
    rebuttal_completed: bool = False
    verdict_revised: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "DebateState":
        return cls(
            da_needed=bool(payload.get("da_needed", False)),
            da_completed=bool(payload.get("da_completed", False)),
            target_agent=str(payload.get("target_agent", "")),
            challenge_present=bool(payload.get("challenge_present", False)),
            rebuttal_completed=bool(payload.get("rebuttal_completed", False)),
            verdict_revised=bool(payload.get("verdict_revised", False)),
        )


@dataclass(frozen=True)
class FinalState:
    arbiter_needed: bool = False
    human_review_recommended: bool = False
    final_verdict: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "FinalState":
        return cls(
            arbiter_needed=bool(payload.get("arbiter_needed", False)),
            human_review_recommended=bool(payload.get("human_review_recommended", False)),
            final_verdict=str(payload.get("final_verdict", "")),
        )


@dataclass(frozen=True)
class PairWorkingMemory:
    pair_id: str
    current_stage: str = ""
    phase1: Phase1State = field(default_factory=Phase1State)
    evidence_state: EvidenceState = field(default_factory=EvidenceState)
    debate_state: DebateState = field(default_factory=DebateState)
    final_state: FinalState = field(default_factory=FinalState)
    next_action: NextAction = NextAction.RUN_PHASE1

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair_id": self.pair_id,
            "current_stage": self.current_stage,
            "phase1": self.phase1.to_dict(),
            "evidence_state": self.evidence_state.to_dict(),
            "debate_state": self.debate_state.to_dict(),
            "final_state": self.final_state.to_dict(),
            "next_action": self.next_action.value,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PairWorkingMemory":
        return cls(
            pair_id=str(payload["pair_id"]),
            current_stage=str(payload.get("current_stage", "")),
            phase1=Phase1State.from_dict(dict(payload.get("phase1", {}))),
            evidence_state=EvidenceState.from_dict(dict(payload.get("evidence_state", {}))),
            debate_state=DebateState.from_dict(dict(payload.get("debate_state", {}))),
            final_state=FinalState.from_dict(dict(payload.get("final_state", {}))),
            next_action=NextAction(str(payload.get("next_action", NextAction.RUN_PHASE1.value))),
        )
