from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from conflict_detection.orchestration.session_types import (
    DetectionPair,
    DuplicateRequirementGroup,
    PairRoute,
    PreprocessResult,
)
from conflict_detection.preprocessing.duplicate_groups import build_duplicate_routes
from conflict_detection.preprocessing.loader import load_requirements
from conflict_detection.preprocessing.pair_generator import generate_pairs
from conflict_detection.preprocessing.similarity_filter import (
    DUPLICATE_SIMILARITY_THRESHOLD,
    SimilarityFilter,
)


SUMMARY_KEYS = (
    "dataset",
    "total_requirements",
    "total_pairs",
    "candidate_count",
    "filtered_count",
    "threshold",
    "duplicate_group_count",
    "duplicate_conflict_pair_count",
    "canonical_candidate_count",
)

JSONL_KEYS = (
    "pair_id",
    "r1_id",
    "r1_text",
    "r2_id",
    "r2_text",
)


class PreprocessingPipeline:
    def __init__(
        self,
        model_path: str | Path | None = None,
        threshold: float = 0.24,
        similarity_filter: SimilarityFilter | Any | None = None,
    ) -> None:
        self.model_path = Path(model_path) if model_path else None
        self.threshold = float(threshold)
        self.similarity_filter = similarity_filter or SimilarityFilter(
            model_path=self.model_path
        )

    def run_file(self, input_path: str | Path) -> PreprocessResult:
        path = Path(input_path)
        requirements = load_requirements(path)
        pairs = generate_pairs(requirements)
        scored_pairs = self.similarity_filter.score_pairs(pairs)
        routed = build_duplicate_routes(
            scored_pairs,
            threshold=self.threshold,
            duplicate_threshold=DUPLICATE_SIMILARITY_THRESHOLD,
        )
        return PreprocessResult(
            dataset=path.stem,
            total_requirements=len(requirements),
            total_pairs=len(pairs),
            candidate_count=len(routed.candidate_pairs),
            filtered_count=len(routed.filtered_pairs),
            threshold=self.threshold,
            candidate_pairs=routed.candidate_pairs,
            filtered_pairs=routed.filtered_pairs,
            duplicate_groups=routed.duplicate_groups,
            canonical_requirement_map=routed.canonical_requirement_map,
            pair_routes=routed.pair_routes,
        )

    def write_candidates_jsonl(
        self,
        result: PreprocessResult,
        output_path: str | Path,
    ) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            for pair in result.candidate_pairs:
                payload = asdict(pair)
                ordered_payload = {key: payload[key] for key in JSONL_KEYS}
                handle.write(json.dumps(ordered_payload, ensure_ascii=False) + "\n")
        return path

    def write_summary_json(
        self,
        result: PreprocessResult,
        output_path: str | Path,
    ) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        summary_payload = {
            key: getattr(result, key)
            for key in SUMMARY_KEYS
            if hasattr(result, key)
        }
        summary_payload["duplicate_group_count"] = len(result.duplicate_groups)
        summary_payload["duplicate_conflict_pair_count"] = sum(
            1 for route in result.pair_routes if route.route_type == "duplicate_conflict"
        )
        summary_payload["canonical_candidate_count"] = len(result.candidate_pairs)
        path.write_text(
            json.dumps(summary_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def write_pair_routes_jsonl(
        self,
        result: PreprocessResult,
        output_path: str | Path,
    ) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            for route in result.pair_routes:
                handle.write(json.dumps(asdict(route), ensure_ascii=False) + "\n")
        return path

    def write_duplicate_groups_json(
        self,
        result: PreprocessResult,
        output_path: str | Path,
    ) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "duplicate_groups": [asdict(group) for group in result.duplicate_groups],
            "canonical_requirement_map": dict(result.canonical_requirement_map),
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    @staticmethod
    def to_legacy_dict(result: PreprocessResult) -> dict[str, Any]:
        payload = asdict(result)
        payload["candidate_pairs"] = [asdict(pair) for pair in result.candidate_pairs]
        payload["filtered_pairs"] = [asdict(pair) for pair in result.filtered_pairs]
        return payload
