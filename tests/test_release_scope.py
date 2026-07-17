from pathlib import Path

from scripts.verify_release import verify_results, verify_scope


ROOT = Path(__file__).resolve().parents[1]


def test_release_paths_follow_public_scope() -> None:
    assert verify_scope(ROOT) == []


def test_published_agent_results_are_complete() -> None:
    assert verify_results(ROOT) == []
