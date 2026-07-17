from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class BatchItem:
    custom_id: str
    pair_id: str
    agent: str
    attempt: int
    method: str
    url: str
    body: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BatchJob:
    job_id: str
    agent: str
    provider: str
    batch_id: str
    input_file_id: str
    output_file_id: str | None = None
    error_file_id: str | None = None
    status: str = "submitted"
    item_count: int = 0
    item_ids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "BatchJob":
        return cls(
            job_id=str(payload["job_id"]),
            agent=str(payload["agent"]),
            provider=str(payload["provider"]),
            batch_id=str(payload["batch_id"]),
            input_file_id=str(payload["input_file_id"]),
            output_file_id=None if payload.get("output_file_id") in (None, "") else str(payload["output_file_id"]),
            error_file_id=None if payload.get("error_file_id") in (None, "") else str(payload["error_file_id"]),
            status=str(payload.get("status", "submitted")),
            item_count=int(payload.get("item_count", 0)),
            item_ids=tuple(str(item) for item in payload.get("item_ids", [])),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass(frozen=True)
class BatchItemResult:
    custom_id: str
    pair_id: str
    agent: str
    attempt: int
    status_code: int
    raw_text: str
    error: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
