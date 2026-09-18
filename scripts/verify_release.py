from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ("semantic", "logic", "feasibility", "goal", "da", "rebuttal", "arbiter")
DATASET_SLUGS = (
    "ETCS-GOLD",
    "OpenAPI-Specification-3.0",
    "promise-project2",
    "Broker-All",
    "Library-Gold",
)
EXPECTED_AGENT_COUNTS = {
    "ETCS-GOLD": 778,
    "OpenAPI-Specification-3.0": 595,
    "promise-project2": 913,
    "Broker-All": 654,
    "Library-Gold": 2875,
}
FORBIDDEN_PATH_PARTS = {
    "__pycache__",
    "repair_backup",
    "repair_backups",
    "ablation",
    "baseline",
    "threshold_end_to_end",
    "prompt_versions",
    "prompts_batch",
    "all-minilm-l6-v2",
}
IGNORED_TOP_LEVEL = {".git", ".venv", "work"}
TEXT_SUFFIXES = {".py", ".json", ".jsonl", ".md", ".txt", ".toml", ".cff", ".csv", ".example"}
SENSITIVE_PATTERNS = {
    "secret-like API key": re.compile(r"(?i)\bsk-[a-z0-9_-]{20,}\b"),
    "private IPv4 address": re.compile(
        r"(?<!\d)(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?!\d)"
    ),
    "absolute Windows path": re.compile(r"(?i)(?<![a-z0-9])[a-z]:\\(?:users|home|multi-agent|projects)\\"),
    "absolute user home": re.compile(r"(?<![a-z0-9])/(?:home|users)/[a-z0-9._-]+", re.IGNORECASE),
    "SSH credential helper": re.compile(
        "SSH_" + "ASKPASS|CODEX_" + "SSH_PASSWORD|PreferredAuthentications=" + "password",
        re.IGNORECASE,
    ),
}


def is_ignored_runtime_path(relative: Path) -> bool:
    if relative.parts and relative.parts[0] in IGNORED_TOP_LEVEL:
        return True
    lowered_parts = {part.lower() for part in relative.parts}
    return bool(lowered_parts & {"__pycache__", ".pytest_cache"}) or relative.suffix.lower() == ".pyc"


def iter_release_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if is_ignored_runtime_path(relative):
            continue
        if path.name == "release_manifest.json":
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def record_count(path: Path) -> int | None:
    if path.suffix.lower() == ".jsonl":
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    if path.suffix.lower() == ".csv":
        raw = path.read_bytes()
        text = None
        for encoding in ("utf-8-sig", "utf-8", "gb18030", "latin-1"):
            try:
                text = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        if text is None:
            return None
        return sum(1 for _ in csv.DictReader(text.splitlines()))
    return None


def category_for(relative: Path) -> str:
    first = relative.parts[0]
    return {
        "src": "source",
        "config": "configuration",
        "scripts": "tooling",
        "tests": "tests",
        "datasets": "dataset",
        "results": "result",
        "docs": "documentation",
    }.get(first, "project_metadata")


def source_for(relative: Path) -> str:
    path = relative.as_posix()
    if path.startswith("src/") or path in {"config/execution_profiles.py", "config/__init__.py", "requirements.txt"}:
        return f"workspace://{path}"
    if path.startswith("datasets/requirements/"):
        return "workspace://dataset/requirement"
    if path.startswith("datasets/labels/"):
        return "workspace://dataset/conflict"
    if path.startswith("results/agents/"):
        return "workspace://results/final_datasets/canonical-run/output"
    if path.endswith("/verdicts.jsonl"):
        return "workspace://results/final_datasets/canonical-run/verdicts"
    if path.startswith("results/summary/metrics.") and relative.suffix in {".json", ".csv"}:
        return "workspace://results/final_datasets/Four-View-Multi-Agent-Framework-summary"
    return "generated"


def write_manifest(root: Path) -> Path:
    entries: list[dict[str, Any]] = []
    for path in iter_release_files(root):
        relative = path.relative_to(root)
        entries.append(
            {
                "path": relative.as_posix(),
                "category": category_for(relative),
                "source": source_for(relative),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "record_count": record_count(path),
            }
        )
    manifest = {
        "release": "four-view-requirement-conflict-detection",
        "version": "1.1.0",
        "date": date.today().isoformat(),
        "selection": {
            "datasets": list(DATASET_SLUGS),
            "etcs_result": "round4",
            "agent_record_rule": "latest successful record per pair",
            "duplicate_policy": "duplicate is not a conflict-positive class",
            "uncertainty_reporting": "offline report generated from stored final verdicts and agent records",
            "excluded_experiments": ["ablation", "baseline", "threshold/end-to-end"],
        },
        "files": entries,
    }
    path = root / "release_manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def verify_jsonl(path: Path) -> list[str]:
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSONL {path}:{line_number}: {exc}")
    return errors


def verify_scope(root: Path) -> list[str]:
    errors: list[str] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if is_ignored_runtime_path(relative):
            continue
        lowered = {part.lower() for part in relative.parts}
        forbidden = lowered & FORBIDDEN_PATH_PARTS
        if forbidden:
            errors.append(f"Forbidden path component {sorted(forbidden)}: {relative}")
        if path.name == ".env":
            errors.append(f"Tracked environment file: {relative}")
    return errors


def verify_sensitive_text(root: Path) -> list[str]:
    errors: list[str] = []
    for path in iter_release_files(root):
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != ".env.example":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label} found in {path.relative_to(root)}")
    return errors


def verify_results(root: Path) -> list[str]:
    errors: list[str] = []
    for agent in AGENTS:
        for dataset, expected in EXPECTED_AGENT_COUNTS.items():
            path = root / "results" / "agents" / agent / f"{dataset}.jsonl"
            if not path.is_file():
                errors.append(f"Missing agent result: {path.relative_to(root)}")
                continue
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
            pair_ids = [str(row.get("pair_id", "")) for row in rows]
            if len(rows) != expected:
                errors.append(f"Unexpected row count for {path.relative_to(root)}: {len(rows)} != {expected}")
            if len(pair_ids) != len(set(pair_ids)):
                errors.append(f"Duplicate pair IDs in {path.relative_to(root)}")
            if any(row.get("status") != "succeeded" for row in rows):
                errors.append(f"Non-success record in {path.relative_to(root)}")
    return errors


def verify_manifest(root: Path) -> list[str]:
    path = root / "release_manifest.json"
    if not path.is_file():
        return ["Missing release_manifest.json"]
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    manifest_paths = {entry["path"] for entry in payload.get("files", [])}
    actual_paths = {item.relative_to(root).as_posix() for item in iter_release_files(root)}
    if manifest_paths != actual_paths:
        errors.append("Manifest file set does not match release file set")
    for entry in payload.get("files", []):
        file_path = root / entry["path"]
        if file_path.is_file() and sha256_file(file_path) != entry["sha256"]:
            errors.append(f"Manifest hash mismatch: {entry['path']}")
    return errors


def verify_release(root: Path = ROOT) -> list[str]:
    errors = verify_scope(root)
    errors.extend(verify_sensitive_text(root))
    errors.extend(verify_results(root))
    for path in iter_release_files(root):
        if path.suffix.lower() == ".jsonl":
            errors.extend(verify_jsonl(path))
    errors.extend(verify_manifest(root))
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify the public release tree.")
    parser.add_argument("--write-manifest", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.write_manifest:
        write_manifest(ROOT)
    errors = verify_release(ROOT)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Release verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
