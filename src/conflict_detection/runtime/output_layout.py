from __future__ import annotations

import json
from pathlib import Path


def load_dataset_name(run_dir: str | Path) -> str:
    run_path = Path(run_dir)
    scheduler_state_path = run_path / "manifests" / "scheduler_state.json"
    if scheduler_state_path.exists():
        payload = json.loads(scheduler_state_path.read_text(encoding="utf-8"))
        dataset_name = str(payload.get("dataset_name", "")).strip()
        if dataset_name:
            return dataset_name
    manifest_path = run_path / "manifests" / "pairs.jsonl"
    if manifest_path.exists():
        first_line = next((line.strip() for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()), "")
        if first_line:
            payload = json.loads(first_line)
            dataset_name = str(payload.get("dataset_name", "")).strip()
            if dataset_name:
                return dataset_name
    raise FileNotFoundError(f"Unable to determine dataset_name for run directory: {run_path}")


def agent_output_dir(run_dir: str | Path, *, agent_name: str, dataset_name: str) -> Path:
    return Path(run_dir) / "output" / agent_name / dataset_name


def agent_results_path(run_dir: str | Path, *, agent_name: str, dataset_name: str) -> Path:
    return agent_output_dir(run_dir, agent_name=agent_name, dataset_name=dataset_name) / "results.jsonl"


def phase1_artifact_path(run_dir: str | Path, *, agent_name: str, dataset_name: str, pair_id: str) -> Path:
    return agent_output_dir(run_dir, agent_name=agent_name, dataset_name=dataset_name) / "artifacts" / f"{pair_id}.json"


def stage_artifact_path(run_dir: str | Path, *, stage_name: str, dataset_name: str, pair_id: str) -> Path:
    return agent_output_dir(run_dir, agent_name=stage_name, dataset_name=dataset_name) / "artifacts" / f"{pair_id}.json"
