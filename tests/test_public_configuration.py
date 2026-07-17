from pathlib import Path

from config.execution_profiles import load_execution_profile


ROOT = Path(__file__).resolve().parents[1]


def test_default_profile_preserves_role_execution() -> None:
    profile = load_execution_profile("default", repo_root=ROOT)

    assert profile.role_execution["semantic"].mode == "sync"
    assert profile.role_execution["logic"].mode == "sync"
    assert profile.role_execution["feasibility"].mode == "batch"
    assert profile.role_execution["goal"].mode == "batch"
    assert profile.role_execution["da"].mode == "sync"
    assert profile.role_execution["rebuttal"].mode == "sync"
    assert profile.role_execution["arbiter"].mode == "sync"
    assert profile.role_execution["feasibility"].batch_max_items == 512
    assert profile.role_execution["goal"].batch_max_items == 512


def test_arbiter_endpoint_requires_public_environment_configuration() -> None:
    from conflict_detection.llm.model_config import ROLE_CONFIG

    assert ROLE_CONFIG["arbiter"]["default_base"] == ""
    assert ROLE_CONFIG["arbiter"]["base_url"] == "GPT_BASE_URL"
