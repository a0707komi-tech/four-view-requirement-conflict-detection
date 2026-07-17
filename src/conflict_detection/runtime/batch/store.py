from __future__ import annotations

import json
from pathlib import Path

from conflict_detection.runtime.batch.contracts import BatchItem, BatchItemResult, BatchJob


class BatchStore:
    def __init__(self, run_dir: str | Path) -> None:
        self.run_dir = Path(run_dir)

    def write_request_items(self, agent: str, job_id: str, items: list[BatchItem]) -> Path:
        path = self.run_dir / "artifacts" / "batches" / agent / "requests" / f"{job_id}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for item in items:
                handle.write(
                    json.dumps(
                        {
                            "custom_id": item.custom_id,
                            "method": item.method,
                            "url": item.url,
                            "body": item.body,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        return path

    def write_submitted_job(self, job: BatchJob) -> Path:
        path = self.run_dir / "artifacts" / "batches" / job.agent / "submitted" / f"{job.job_id}.json"
        return self._write_json(path, job.to_dict())

    def write_job_status(self, job: BatchJob) -> Path:
        path = self.run_dir / "artifacts" / "batches" / job.agent / "status" / f"{job.job_id}.json"
        return self._write_json(path, job.to_dict())

    def write_response_items(self, agent: str, job_id: str, items: list[dict[str, object]]) -> Path:
        path = self.run_dir / "artifacts" / "batches" / agent / "responses" / f"{job_id}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for item in items:
                handle.write(json.dumps(item, ensure_ascii=False) + "\n")
        return path

    def write_parsed_results(self, agent: str, job_id: str, items: list[BatchItemResult]) -> Path:
        path = self.run_dir / "artifacts" / "batches" / agent / "parsed" / f"{job_id}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for item in items:
                handle.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")
        return path

    def list_submitted_jobs(self, agent: str) -> list[BatchJob]:
        root = self.run_dir / "artifacts" / "batches" / agent / "submitted"
        if not root.exists():
            return []
        jobs: list[BatchJob] = []
        for path in sorted(root.glob("*.json")):
            jobs.append(BatchJob.from_dict(json.loads(path.read_text(encoding="utf-8"))))
        return jobs

    def load_job_status(self, agent: str, job_id: str) -> BatchJob | None:
        path = self.run_dir / "artifacts" / "batches" / agent / "status" / f"{job_id}.json"
        if not path.exists():
            return None
        return BatchJob.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def _write_json(self, path: Path, payload: dict[str, object]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
