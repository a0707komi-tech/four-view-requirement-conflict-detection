from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RoleExecutionConfig:
    mode: str
    provider: str
    batch_max_items: int = 1


@dataclass(frozen=True)
class SchedulerConfig:
    global_max_workers: int
    per_agent_max_workers: dict[str, int]
    max_attempts: dict[str, int]


@dataclass(frozen=True)
class ExecutionProfile:
    name: str
    phase1_prompt_root: Path
    debate_prompt_root: Path
    scheduler: SchedulerConfig
    role_execution: dict[str, RoleExecutionConfig]


def load_execution_profile(profile_name: str, *, repo_root: Path | None = None) -> ExecutionProfile:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[1]
    source = root / "config" / "run_profiles" / f"{profile_name}.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    return ExecutionProfile(
        name=str(payload["name"]),
        phase1_prompt_root=root / str(payload["phase1_prompt_root"]),
        debate_prompt_root=root / str(payload["debate_prompt_root"]),
        scheduler=SchedulerConfig(
            global_max_workers=int(payload["scheduler"]["global_max_workers"]),
            per_agent_max_workers={k: int(v) for k, v in payload["scheduler"]["per_agent_max_workers"].items()},
            max_attempts={k: int(v) for k, v in payload["scheduler"]["max_attempts"].items()},
        ),
        role_execution={
            role: RoleExecutionConfig(
                mode=str(config["mode"]),
                provider=str(config["provider"]),
                batch_max_items=int(config.get("batch_max_items", 1)),
            )
            for role, config in payload.get("role_execution", {}).items()
        },
    )


def profile_to_dict(profile: ExecutionProfile) -> dict[str, Any]:
    return {
        "name": profile.name,
        "phase1_prompt_root": str(profile.phase1_prompt_root),
        "debate_prompt_root": str(profile.debate_prompt_root),
        "scheduler": {
            "global_max_workers": profile.scheduler.global_max_workers,
            "per_agent_max_workers": dict(profile.scheduler.per_agent_max_workers),
            "max_attempts": dict(profile.scheduler.max_attempts),
        },
        "role_execution": {
            role: {
                "mode": config.mode,
                "provider": config.provider,
                "batch_max_items": config.batch_max_items,
            }
            for role, config in profile.role_execution.items()
        },
    }
