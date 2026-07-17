from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from config.execution_profiles import load_execution_profile, profile_to_dict
from conflict_detection.io.pair_loader import load_duplicate_groups, load_pair_routes, load_pairs
from conflict_detection.orchestration.session_types import PairRoute
from conflict_detection.runtime.output_layout import agent_output_dir
from conflict_detection.runtime.route_manifest import (
    write_duplicate_groups_manifest,
    write_pair_routes_manifest,
)
from conflict_detection.runtime.run_manifest import write_pair_manifest

AGENT_NAMES = ("semantic", "logic", "feasibility", "goal", "da", "rebuttal", "arbiter")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare an agent-first conflict detection run.")
    parser.add_argument("--input", required=True, help="Path to candidate-pair JSONL file")
    parser.add_argument("--output-dir", default="./results", help="Directory for run artifacts")
    parser.add_argument("--run-id", help="Optional explicit run identifier")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit on candidate pairs")
    parser.add_argument("--profile", default="phase1_batch", help="Execution profile name")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    pairs = load_pairs(args.input, args.limit)
    input_path = Path(args.input)
    pair_routes_path = input_path.with_name(input_path.name.replace("_candidates.jsonl", "_pair_routes.jsonl"))
    duplicate_groups_path = input_path.with_name(input_path.name.replace("_candidates.jsonl", "_duplicate_groups.json"))
    output_dir = Path(args.output_dir)
    run_id = args.run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    profile = load_execution_profile(args.profile)
    dataset_name = input_path.stem.removesuffix("_candidates")
    write_pair_manifest(run_dir, run_id=run_id, dataset_name=dataset_name, pairs=pairs)
    pair_routes = load_pair_routes(pair_routes_path) if pair_routes_path.exists() else _build_default_pair_routes(pairs)
    duplicate_groups, canonical_requirement_map = (
        load_duplicate_groups(duplicate_groups_path)
        if duplicate_groups_path.exists()
        else ([], {})
    )
    write_pair_routes_manifest(run_dir, routes=pair_routes)
    write_duplicate_groups_manifest(
        run_dir,
        groups=duplicate_groups,
        canonical_requirement_map=canonical_requirement_map,
    )
    scheduler_state = run_dir / "manifests" / "scheduler_state.json"
    scheduler_state.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "dataset_name": dataset_name,
                "pair_count": len(pairs),
                "duplicate_group_count": len(duplicate_groups),
                "pair_route_count": len(pair_routes),
                "profile_name": profile.name,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (run_dir / "manifests" / "execution_profile.json").write_text(
        json.dumps(profile_to_dict(profile), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)
    for agent_name in AGENT_NAMES:
        agent_dir = agent_output_dir(run_dir, agent_name=agent_name, dataset_name=dataset_name)
        agent_dir.mkdir(parents=True, exist_ok=True)
        (agent_dir / "artifacts").mkdir(parents=True, exist_ok=True)
    return 0


def _build_default_pair_routes(pairs):
    return [
        PairRoute(
            pair_id=pair.pair_id,
            r1_id=pair.r1_id,
            r1_text=pair.r1_text,
            r2_id=pair.r2_id,
            r2_text=pair.r2_text,
            route_type="canonical_candidate",
            canonical_pair_id=pair.pair_id,
            canonical_r1_id=pair.r1_id,
            canonical_r1_text=pair.r1_text,
            canonical_r2_id=pair.r2_id,
            canonical_r2_text=pair.r2_text,
        )
        for pair in pairs
    ]


if __name__ == "__main__":
    raise SystemExit(main())
