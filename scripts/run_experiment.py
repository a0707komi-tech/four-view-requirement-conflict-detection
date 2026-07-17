from __future__ import annotations

import argparse
from pathlib import Path

from conflict_detection.cli.prepare_run_cli import main as prepare_run
from conflict_detection.cli.run_scheduler_cli import main as run_scheduler


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare and execute one conflict-detection run.")
    parser.add_argument("--input", required=True, help="Candidate-pair JSONL produced by preprocessing")
    parser.add_argument("--output-dir", default="work/runs", help="Run output root")
    parser.add_argument("--run-id", required=True, help="Stable run identifier")
    parser.add_argument("--profile", default="default", help="Execution profile")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    prepare_status = prepare_run(
        [
            "--input",
            args.input,
            "--output-dir",
            args.output_dir,
            "--run-id",
            args.run_id,
            "--profile",
            args.profile,
        ]
    )
    if prepare_status != 0:
        return prepare_status
    run_dir = Path(args.output_dir) / args.run_id
    return run_scheduler(["--run-dir", str(run_dir), "--profile", args.profile])


if __name__ == "__main__":
    raise SystemExit(main())
