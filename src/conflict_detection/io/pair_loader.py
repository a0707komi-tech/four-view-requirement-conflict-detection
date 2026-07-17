from __future__ import annotations

import json
from pathlib import Path

from conflict_detection.orchestration.session_types import DetectionPair, DuplicateRequirementGroup, PairRoute


def load_pairs(input_path: str | Path, limit: int = 0) -> list[DetectionPair]:
    pairs: list[DetectionPair] = []
    with Path(input_path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            pairs.append(
                DetectionPair(
                    pair_id=raw["pair_id"],
                    r1_id=raw["r1_id"],
                    r1_text=raw["r1_text"],
                    r2_id=raw["r2_id"],
                    r2_text=raw["r2_text"],
                    cosine_similarity=raw.get("cosine_similarity"),
                )
            )
    return pairs[:limit] if limit and limit < len(pairs) else pairs


def load_pair_routes(input_path: str | Path) -> list[PairRoute]:
    routes: list[PairRoute] = []
    with Path(input_path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            routes.append(PairRoute(**json.loads(line)))
    return routes


def load_duplicate_groups(input_path: str | Path) -> tuple[list[DuplicateRequirementGroup], dict[str, str]]:
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    groups = [DuplicateRequirementGroup(**item) for item in payload.get("duplicate_groups", [])]
    canonical_requirement_map = {
        str(key): str(value) for key, value in payload.get("canonical_requirement_map", {}).items()
    }
    return groups, canonical_requirement_map
