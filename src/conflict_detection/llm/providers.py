from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from openai import OpenAI

from conflict_detection.llm.request_factory import extract_batch_chat_text
from conflict_detection.runtime.batch.contracts import BatchItemResult, BatchJob


class ProviderClient:
    def __init__(self, *, name: str, client: OpenAI, model: str) -> None:
        self.name = name
        self.client = client
        self.model = model

    def submit_chat_batch(
        self,
        *,
        request_file: Path,
        completion_window: str = "24h",
        metadata: dict[str, str] | None = None,
    ) -> BatchJob:
        upload = self.client.files.create(file=request_file.open("rb"), purpose="batch")
        batch = self.client.batches.create(
            input_file_id=upload.id,
            endpoint="/v1/chat/completions",
            completion_window=completion_window,
            metadata=metadata or {},
        )
        return BatchJob(
            job_id=str(batch.id),
            agent=str((metadata or {}).get("agent", "")),
            provider=self.name,
            batch_id=str(batch.id),
            input_file_id=str(upload.id),
            output_file_id=getattr(batch, "output_file_id", None),
            error_file_id=getattr(batch, "error_file_id", None),
            status=str(getattr(batch, "status", "submitted")),
            metadata=dict(metadata or {}),
        )

    def retrieve_batch(self, batch_id: str) -> BatchJob:
        batch = self.client.batches.retrieve(batch_id)
        metadata = getattr(batch, "metadata", {}) or {}
        return BatchJob(
            job_id=str(batch.id),
            agent=str(metadata.get("agent", "")),
            provider=self.name,
            batch_id=str(batch.id),
            input_file_id=str(getattr(batch, "input_file_id", "")),
            output_file_id=getattr(batch, "output_file_id", None),
            error_file_id=getattr(batch, "error_file_id", None),
            status=str(getattr(batch, "status", "submitted")),
            metadata=dict(metadata),
        )

    def fetch_batch_output(self, output_file_id: str) -> list[dict[str, Any]]:
        content = self.client.files.retrieve_content(output_file_id)
        items: list[dict[str, Any]] = []
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if isinstance(payload, dict):
                items.append(payload)
        return items

    def parse_batch_results(self, raw_items: list[dict[str, Any]]) -> list[BatchItemResult]:
        parsed: list[BatchItemResult] = []
        for item in raw_items:
            custom_id = str(item.get("custom_id", ""))
            metadata = _parse_custom_id(custom_id)
            response = item.get("response", {})
            status_code = 0
            error = None
            if isinstance(response, dict):
                status_code = int(response.get("status_code", 0) or 0)
                error = response.get("error")
            parsed.append(
                BatchItemResult(
                    custom_id=custom_id,
                    pair_id=metadata["pair_id"],
                    agent=metadata["agent"],
                    attempt=metadata["attempt"],
                    status_code=status_code,
                    raw_text=extract_batch_chat_text(item),
                    error=error if isinstance(error, dict) else None,
                )
            )
        return parsed


def _parse_custom_id(custom_id: str) -> dict[str, Any]:
    parts = {}
    for item in custom_id.split("|"):
        if ":" not in item:
            continue
        key, value = item.split(":", 1)
        parts[key] = value
    return {
        "run_id": str(parts.get("run", "")),
        "agent": str(parts.get("agent", "")),
        "pair_id": str(parts.get("pair", "")),
        "attempt": int(parts.get("attempt", "1")),
    }
