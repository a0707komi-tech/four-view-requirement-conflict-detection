from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from conflict_detection.orchestration.session_types import DuplicateRequirementGroup, PairRoute


def write_pair_routes_manifest(run_dir: str | Path, *, routes: list[PairRoute]) -> Path:
    destination = Path(run_dir) / "manifests" / "pair_routes.jsonl"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for route in routes:
            handle.write(json.dumps(asdict(route), ensure_ascii=False) + "\n")
    return destination


def load_pair_routes_manifest(manifest_path: str | Path) -> list[PairRoute]:
    routes: list[PairRoute] = []
    with Path(manifest_path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            routes.append(PairRoute(**json.loads(line)))
    return routes


def write_duplicate_groups_manifest(
    run_dir: str | Path,
    *,
    groups: list[DuplicateRequirementGroup],
    canonical_requirement_map: dict[str, str],
) -> Path:
    destination = Path(run_dir) / "manifests" / "duplicate_groups.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "duplicate_groups": [asdict(group) for group in groups],
        "canonical_requirement_map": dict(canonical_requirement_map),
    }
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return destination


def load_duplicate_groups_manifest(
    manifest_path: str | Path,
) -> tuple[list[DuplicateRequirementGroup], dict[str, str]]:
    payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    groups = [DuplicateRequirementGroup(**item) for item in payload.get("duplicate_groups", [])]
    canonical_requirement_map = {
        str(key): str(value) for key, value in payload.get("canonical_requirement_map", {}).items()
    }
    return groups, canonical_requirement_map
