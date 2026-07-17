from __future__ import annotations

import os
from pathlib import Path


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_prompt_root() -> Path:
    return get_repo_root() / "src" / "conflict_detection" / "prompts"


def get_model_root() -> Path:
    override = os.environ.get("CONFLICT_DETECTION_MODEL_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return get_repo_root() / "all-MiniLM-L6-v2"
