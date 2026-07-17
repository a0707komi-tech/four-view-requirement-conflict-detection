from __future__ import annotations

import argparse
from pathlib import Path

from conflict_detection.runtime.finalizer import rebuild_final_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rebuild final outputs from agent-first artifacts.")
    parser.add_argument("--run-dir", required=True, help="Prepared run directory")
    parser.add_argument("--dataset-name", required=True, help="Dataset name")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rebuild_final_outputs(Path(args.run_dir), dataset_name=args.dataset_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
