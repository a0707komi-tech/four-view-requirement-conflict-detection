from conflict_detection.orchestration.session_types import DetectionPair
from conflict_detection.runtime.artifacts.schemas import Phase1SummaryArtifact
from conflict_detection.runtime.consensus import evaluate_strict_consensus_from_summaries


PAIR = DetectionPair(
    pair_id="1_2",
    r1_id="1",
    r1_text="Requirement A",
    r2_id="2",
    r2_text="Requirement B",
    cosine_similarity=None,
)


def summary(agent: str, verdict: str, confidence: float) -> Phase1SummaryArtifact:
    return Phase1SummaryArtifact(
        pair_id="1_2",
        agent=agent,
        model="test-model",
        verdict=verdict,
        confidence=confidence,
        pairwise_conflict_grounded=True,
        reasoning_summary="test",
        key_evidence=(),
        assumptions=(),
    )


def test_unanimous_binary_vote_skips_adjudication() -> None:
    summaries = {
        agent: summary(agent, "incompatible", 0.8)
        for agent in ("semantic", "logic", "feasibility", "goal")
    }

    result = evaluate_strict_consensus_from_summaries(PAIR, summaries)

    assert result is not None
    assert result.verdict == "incompatible"
    assert result.confidence == 0.8


def test_disagreement_and_unanimous_uncertain_do_not_early_stop() -> None:
    disagreement = {
        "semantic": summary("semantic", "incompatible", 0.8),
        "logic": summary("logic", "compatible", 0.8),
        "feasibility": summary("feasibility", "incompatible", 0.8),
        "goal": summary("goal", "incompatible", 0.8),
    }
    uncertain = {
        agent: summary(agent, "uncertain", 0.5)
        for agent in ("semantic", "logic", "feasibility", "goal")
    }

    assert evaluate_strict_consensus_from_summaries(PAIR, disagreement) is None
    assert evaluate_strict_consensus_from_summaries(PAIR, uncertain) is None
