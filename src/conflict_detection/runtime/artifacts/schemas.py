from __future__ import annotations

from dataclasses import dataclass, field


def _tuple_of_strings(values: object) -> tuple[str, ...]:
    if not isinstance(values, list):
        return ()
    return tuple(str(item) for item in values)


@dataclass(frozen=True)
class Phase1AngleCard:
    summary: str = ""
    shared_state: str = ""
    decision_basis: tuple[str, ...] = ()
    coexistence_path: tuple[str, ...] = ()
    hidden_assumptions: tuple[str, ...] = ()
    global_test_note: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "summary": self.summary,
            "shared_state": self.shared_state,
            "decision_basis": list(self.decision_basis),
            "coexistence_path": list(self.coexistence_path),
            "hidden_assumptions": list(self.hidden_assumptions),
            "global_test_note": self.global_test_note,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "Phase1AngleCard":
        return cls(
            summary=str(payload.get("summary", "")),
            shared_state=str(payload.get("shared_state", "")),
            decision_basis=_tuple_of_strings(payload.get("decision_basis", [])),
            coexistence_path=_tuple_of_strings(payload.get("coexistence_path", [])),
            hidden_assumptions=_tuple_of_strings(payload.get("hidden_assumptions", [])),
            global_test_note=str(payload.get("global_test_note", "")),
        )


@dataclass(frozen=True)
class Phase1SummaryArtifact:
    pair_id: str
    agent: str
    model: str
    verdict: str
    confidence: float
    pairwise_conflict_grounded: bool
    reasoning_summary: str
    key_evidence: tuple[str, ...]
    assumptions: tuple[str, ...]
    angle_card: Phase1AngleCard = field(default_factory=Phase1AngleCard)

    def to_dict(self) -> dict[str, object]:
        return {
            "pair_id": self.pair_id,
            "agent": self.agent,
            "model": self.model,
            "verdict": self.verdict,
            "confidence": self.confidence,
            "pairwise_conflict_grounded": self.pairwise_conflict_grounded,
            "reasoning_summary": self.reasoning_summary,
            "key_evidence": list(self.key_evidence),
            "assumptions": list(self.assumptions),
            "angle_card": self.angle_card.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "Phase1SummaryArtifact":
        angle_payload = payload.get("angle_card")
        angle_card = (
            Phase1AngleCard.from_dict(angle_payload)
            if isinstance(angle_payload, dict)
            else _legacy_phase1_angle_card(payload)
        )
        return cls(
            pair_id=str(payload["pair_id"]),
            agent=str(payload["agent"]),
            model=str(payload.get("model", "")),
            verdict=str(payload.get("verdict", "uncertain")),
            confidence=float(payload.get("confidence", 0.5)),
            pairwise_conflict_grounded=bool(payload.get("pairwise_conflict_grounded", True)),
            reasoning_summary=str(payload.get("reasoning_summary", "")),
            key_evidence=_tuple_of_strings(payload.get("key_evidence", [])),
            assumptions=_tuple_of_strings(payload.get("assumptions", [])),
            angle_card=angle_card,
        )


@dataclass(frozen=True)
class Phase1SummaryBundle:
    pair_id: str
    summaries: dict[str, Phase1SummaryArtifact]

    def to_dict(self) -> dict[str, object]:
        return {
            "pair_id": self.pair_id,
            "summaries": {agent: summary.to_dict() for agent, summary in self.summaries.items()},
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "Phase1SummaryBundle":
        raw_summaries = payload.get("summaries", {})
        if not isinstance(raw_summaries, dict):
            raw_summaries = {}
        return cls(
            pair_id=str(payload["pair_id"]),
            summaries={
                str(agent): Phase1SummaryArtifact.from_dict(summary)
                for agent, summary in raw_summaries.items()
                if isinstance(summary, dict)
            },
        )


@dataclass(frozen=True)
class DaChallengeCard:
    focus: str = ""
    disagreement_points: tuple[str, ...] = ()
    weak_assumption_points: tuple[str, ...] = ()
    overlooked_factors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "focus": self.focus,
            "disagreement_points": list(self.disagreement_points),
            "weak_assumption_points": list(self.weak_assumption_points),
            "overlooked_factors": list(self.overlooked_factors),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "DaChallengeCard":
        return cls(
            focus=str(payload.get("focus", "")),
            disagreement_points=_tuple_of_strings(payload.get("disagreement_points", [])),
            weak_assumption_points=_tuple_of_strings(payload.get("weak_assumption_points", [])),
            overlooked_factors=_tuple_of_strings(payload.get("overlooked_factors", [])),
        )


@dataclass(frozen=True)
class DaChallengeArtifact:
    pair_id: str
    target_agent: str
    challenge: str
    challenge_type: str
    reason: str
    disagreements: tuple[str, ...]
    weak_assumptions: tuple[str, ...]
    overlooked_factors: tuple[str, ...]
    challenge_card: DaChallengeCard = field(default_factory=DaChallengeCard)

    def to_dict(self) -> dict[str, object]:
        return {
            "pair_id": self.pair_id,
            "target_agent": self.target_agent,
            "challenge": self.challenge,
            "challenge_type": self.challenge_type,
            "reason": self.reason,
            "disagreements": list(self.disagreements),
            "weak_assumptions": list(self.weak_assumptions),
            "overlooked_factors": list(self.overlooked_factors),
            "challenge_card": self.challenge_card.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "DaChallengeArtifact":
        card_payload = payload.get("challenge_card")
        challenge_card = (
            DaChallengeCard.from_dict(card_payload)
            if isinstance(card_payload, dict)
            else _legacy_da_challenge_card(payload)
        )
        return cls(
            pair_id=str(payload["pair_id"]),
            target_agent=str(payload.get("target_agent", "")),
            challenge=str(payload.get("challenge", "")),
            challenge_type=str(payload.get("challenge_type", "")),
            reason=str(payload.get("reason", "")),
            disagreements=_tuple_of_strings(payload.get("disagreements", [])),
            weak_assumptions=_tuple_of_strings(payload.get("weak_assumptions", [])),
            overlooked_factors=_tuple_of_strings(payload.get("overlooked_factors", [])),
            challenge_card=challenge_card,
        )


@dataclass(frozen=True)
class RebuttalDeltaCard:
    stance: str = ""
    response_core: str = ""
    response_points: tuple[str, ...] = ()
    remaining_gaps: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "stance": self.stance,
            "response_core": self.response_core,
            "response_points": list(self.response_points),
            "remaining_gaps": list(self.remaining_gaps),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "RebuttalDeltaCard":
        return cls(
            stance=str(payload.get("stance", "")),
            response_core=str(payload.get("response_core", "")),
            response_points=_tuple_of_strings(payload.get("response_points", [])),
            remaining_gaps=_tuple_of_strings(payload.get("remaining_gaps", [])),
        )


@dataclass(frozen=True)
class RebuttalSummaryArtifact:
    pair_id: str
    target_agent: str
    response_summary: str
    verdict_revised: bool
    revised_verdict: str
    revised_confidence: float | None
    unresolved_issues: tuple[str, ...]
    delta_card: RebuttalDeltaCard = field(default_factory=RebuttalDeltaCard)

    def to_dict(self) -> dict[str, object]:
        return {
            "pair_id": self.pair_id,
            "target_agent": self.target_agent,
            "response_summary": self.response_summary,
            "verdict_revised": self.verdict_revised,
            "revised_verdict": self.revised_verdict,
            "revised_confidence": self.revised_confidence,
            "unresolved_issues": list(self.unresolved_issues),
            "delta_card": self.delta_card.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "RebuttalSummaryArtifact":
        revised_confidence = payload.get("revised_confidence")
        card_payload = payload.get("delta_card")
        delta_card = (
            RebuttalDeltaCard.from_dict(card_payload)
            if isinstance(card_payload, dict)
            else _legacy_rebuttal_delta_card(payload)
        )
        return cls(
            pair_id=str(payload["pair_id"]),
            target_agent=str(payload.get("target_agent", "")),
            response_summary=str(payload.get("response_summary", "")),
            verdict_revised=bool(payload.get("verdict_revised", False)),
            revised_verdict=str(payload.get("revised_verdict", "")),
            revised_confidence=None if revised_confidence in (None, "") else float(revised_confidence),
            unresolved_issues=_tuple_of_strings(payload.get("unresolved_issues", [])),
            delta_card=delta_card,
        )


@dataclass(frozen=True)
class ArbiterInputBundle:
    pair_id: str
    phase1_summaries: dict[str, Phase1SummaryArtifact]
    da_challenge: DaChallengeArtifact
    rebuttal: RebuttalSummaryArtifact

    def to_dict(self) -> dict[str, object]:
        return {
            "pair_id": self.pair_id,
            "phase1_summaries": {agent: summary.to_dict() for agent, summary in self.phase1_summaries.items()},
            "da_challenge": self.da_challenge.to_dict(),
            "rebuttal": self.rebuttal.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "ArbiterInputBundle":
        raw_phase1 = payload.get("phase1_summaries", {})
        if not isinstance(raw_phase1, dict):
            raw_phase1 = {}
        da_payload = payload.get("da_challenge", {})
        rebuttal_payload = payload.get("rebuttal", {})
        return cls(
            pair_id=str(payload["pair_id"]),
            phase1_summaries={
                str(agent): Phase1SummaryArtifact.from_dict(summary)
                for agent, summary in raw_phase1.items()
                if isinstance(summary, dict)
            },
            da_challenge=DaChallengeArtifact.from_dict(da_payload if isinstance(da_payload, dict) else {"pair_id": str(payload["pair_id"])}),
            rebuttal=RebuttalSummaryArtifact.from_dict(
                rebuttal_payload if isinstance(rebuttal_payload, dict) else {"pair_id": str(payload["pair_id"])}
            ),
        )


def _legacy_phase1_angle_card(payload: dict[str, object]) -> Phase1AngleCard:
    verdict = str(payload.get("verdict", "uncertain"))
    pairwise_conflict_grounded = bool(payload.get("pairwise_conflict_grounded", True))
    reasoning_summary = str(payload.get("reasoning_summary", ""))
    key_evidence = _tuple_of_strings(payload.get("key_evidence", []))
    assumptions = _tuple_of_strings(payload.get("assumptions", []))
    return Phase1AngleCard(
        summary=reasoning_summary,
        shared_state="" if pairwise_conflict_grounded else "not explicitly captured in legacy artifact",
        decision_basis=key_evidence,
        coexistence_path=() if verdict == "incompatible" else ((reasoning_summary,) if reasoning_summary else ()),
        hidden_assumptions=assumptions,
        global_test_note=_default_global_test_note(
            verdict=verdict,
            pairwise_conflict_grounded=pairwise_conflict_grounded,
            hidden_assumptions=assumptions,
        ),
    )


def _legacy_da_challenge_card(payload: dict[str, object]) -> DaChallengeCard:
    reason = str(payload.get("reason", ""))
    challenge_type = str(payload.get("challenge_type", ""))
    focus = reason or challenge_type or str(payload.get("challenge", ""))
    return DaChallengeCard(
        focus=focus,
        disagreement_points=_tuple_of_strings(payload.get("disagreements", [])),
        weak_assumption_points=_tuple_of_strings(payload.get("weak_assumptions", [])),
        overlooked_factors=_tuple_of_strings(payload.get("overlooked_factors", [])),
    )


def _legacy_rebuttal_delta_card(payload: dict[str, object]) -> RebuttalDeltaCard:
    revised_verdict = str(payload.get("revised_verdict", ""))
    verdict_revised = bool(payload.get("verdict_revised", False))
    response_summary = str(payload.get("response_summary", ""))
    stance = "revised" if verdict_revised else "maintained"
    if revised_verdict:
        stance = f"{stance}:{revised_verdict}"
    return RebuttalDeltaCard(
        stance=stance,
        response_core=response_summary,
        response_points=(response_summary,) if response_summary else (),
        remaining_gaps=_tuple_of_strings(payload.get("unresolved_issues", [])),
    )


def _default_global_test_note(
    *,
    verdict: str,
    pairwise_conflict_grounded: bool,
    hidden_assumptions: tuple[str, ...],
) -> str:
    if not pairwise_conflict_grounded:
        return "No single forced shared conflict state was grounded from the pair alone."
    if verdict == "compatible":
        return "The analysis leaves at least one coexistence path open."
    if verdict == "incompatible":
        if hidden_assumptions:
            return "The incompatibility claim still depends on listed assumptions; no separate all-path failure proof is captured."
        return "The incompatibility claim is stated, but no separate all-path failure proof is captured."
    return "The analysis does not prove global incompatibility and does not settle a stable coexistence path."
