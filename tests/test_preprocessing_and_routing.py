from conflict_detection.agents.semantic_agent import SemanticAgent
from conflict_detection.orchestration.session_types import DetectionPair
from conflict_detection.preprocessing.duplicate_groups import build_duplicate_routes


def test_duplicate_group_uses_minimum_id_and_one_canonical_pair() -> None:
    routed = build_duplicate_routes(
        [
            {
                "pair_id": "1_2",
                "r1_id": "1",
                "r1_text": "same requirement",
                "r2_id": "2",
                "r2_text": "same requirement",
                "cosine_similarity": 1.0,
            },
            {
                "pair_id": "1_3",
                "r1_id": "1",
                "r1_text": "same requirement",
                "r2_id": "3",
                "r2_text": "different requirement",
                "cosine_similarity": 0.8,
            },
            {
                "pair_id": "2_3",
                "r1_id": "2",
                "r1_text": "same requirement",
                "r2_id": "3",
                "r2_text": "different requirement",
                "cosine_similarity": 0.8,
            },
        ],
        threshold=0.24,
        duplicate_threshold=0.999999,
    )

    assert routed.canonical_requirement_map == {"1": "1", "2": "1", "3": "3"}
    assert [pair.pair_id for pair in routed.candidate_pairs] == ["1_3"]
    assert {route.pair_id: route.route_type for route in routed.pair_routes} == {
        "1_2": "duplicate_conflict",
        "1_3": "canonical_candidate",
        "2_3": "canonical_alias",
    }


def test_similarity_is_not_rendered_into_agent_prompt() -> None:
    pair = DetectionPair(
        pair_id="1_2",
        r1_id="1",
        r1_text="Requirement A",
        r2_id="2",
        r2_text="Requirement B",
        cosine_similarity=0.987654,
    )

    prompt = SemanticAgent(None, None).build_user_prompt(
        "Pair {{pair_id}}: {{requirement_a}} / {{requirement_b}}",
        pair,
    )

    assert "0.987654" not in prompt
    assert "cosine_similarity" not in prompt
