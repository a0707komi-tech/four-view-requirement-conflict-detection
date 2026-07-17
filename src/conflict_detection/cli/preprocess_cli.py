from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from conflict_detection.io.dataset_paths import get_model_root
from conflict_detection.preprocessing.pipeline import PreprocessingPipeline


class EnvSimilarityFilter:
    def __init__(self, scores: dict[str, float]) -> None:
        self._scores = scores

    def score_pairs(self, pairs):
        scored = []
        for pair in pairs:
            key = f"{pair['r1_id']}|{pair['r2_id']}"
            reverse_key = f"{pair['r2_id']}|{pair['r1_id']}"
            score = self._scores.get(key, self._scores.get(reverse_key, 0.0))
            enriched = dict(pair)
            enriched["cosine_similarity"] = round(float(score), 6)
            scored.append(enriched)
        return scored


def _build_pipeline(args: argparse.Namespace) -> PreprocessingPipeline:
    stub_scores = os.environ.get("PREPROCESSING_STUB_SCORES")
    similarity_filter = None
    if stub_scores:
        similarity_filter = EnvSimilarityFilter(json.loads(stub_scores))
    return PreprocessingPipeline(
        model_path=args.model_path,
        threshold=args.threshold,
        similarity_filter=similarity_filter,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preprocess requirement datasets.")
    parser.add_argument("input", help="CSV file or directory")
    parser.add_argument(
        "--output-dir",
        default="preprocessed",
        help="Directory for summary and candidate outputs",
    )
    parser.add_argument(
        "--model-path",
        default=str(get_model_root()),
        help="Sentence transformer model",
    )
    parser.add_argument("--threshold", type=float, default=0.24, help="Similarity cutoff")
    args = parser.parse_args(argv)

    pipeline = _build_pipeline(args)
    input_path = Path(args.input)
    files = [input_path]
    if input_path.is_dir():
        files = sorted(
            candidate
            for candidate in input_path.iterdir()
            if candidate.suffix.lower() == ".csv"
        )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for file_path in files:
        result = pipeline.run_file(file_path)
        pipeline.write_summary_json(result, output_dir / f"{result.dataset}_summary.json")
        pipeline.write_candidates_jsonl(
            result,
            output_dir / f"{result.dataset}_candidates.jsonl",
        )
        pipeline.write_pair_routes_jsonl(
            result,
            output_dir / f"{result.dataset}_pair_routes.jsonl",
        )
        pipeline.write_duplicate_groups_json(
            result,
            output_dir / f"{result.dataset}_duplicate_groups.json",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
