from __future__ import annotations

import csv
from pathlib import Path

from conflict_detection.preprocessing.cleaner import clean_text


def load_requirements(input_path: str | Path) -> list[dict[str, str]]:
    path = Path(input_path)
    requirements: list[dict[str, str]] = []
    seen_ids: set[str] = set()

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        for row in reader:
            if len(row) < 2:
                continue

            req_id = str(row[0]).strip()
            text = clean_text(row[1])
            if not req_id or req_id.lower() == "nan":
                continue
            if not text or text.lower() == "nan":
                continue
            if req_id in seen_ids:
                continue

            seen_ids.add(req_id)
            requirements.append({"req_id": req_id, "text": text})

    return requirements
