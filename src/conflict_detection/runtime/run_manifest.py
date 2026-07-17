from __future__ import annotations

import json
from pathlib import Path

from conflict_detection.orchestration.session_types import DetectionPair
from conflict_detection.runtime.contracts import PairManifestRecord


def write_pair_manifest(
    run_dir: str | Path,
    *,
    run_id: str,
    dataset_name: str,
    pairs: list[DetectionPair],
) -> Path:
    destination = Path(run_dir) / "manifests" / "pairs.jsonl"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for pair in pairs:
            record = PairManifestRecord(
                run_id=run_id,
                dataset_name=dataset_name,
                pair_id=pair.pair_id,
                r1_id=pair.r1_id,
                r1_text=pair.r1_text,
                r2_id=pair.r2_id,
                r2_text=pair.r2_text,
                cosine_similarity=pair.cosine_similarity,
            )
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
    return destination


def load_pair_manifest(manifest_path: str | Path) -> list[PairManifestRecord]:
    records: list[PairManifestRecord] = []
    with Path(manifest_path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(PairManifestRecord.from_dict(json.loads(line)))
    return records
