from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUBMITTED = "submitted"
    SUCCEEDED = "succeeded"
    FAILED_RETRYABLE = "failed_retryable"
    FAILED_TERMINAL = "failed_terminal"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class AgentTask:
    run_id: str
    pair_id: str
    agent: str
    attempt: int = 1


@dataclass(frozen=True)
class AgentError:
    type: str
    message: str
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentRecord:
    run_id: str
    pair_id: str
    agent: str
    status: TaskStatus
    attempt: int
    started_at: str
    finished_at: str
    input_ref: dict[str, str]
    model: str
    prompt_version: str
    result: dict[str, Any] | None
    error: AgentError | None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AgentRecord":
        error_payload = payload.get("error")
        error = AgentError(**error_payload) if error_payload else None
        return cls(
            run_id=str(payload["run_id"]),
            pair_id=str(payload["pair_id"]),
            agent=str(payload["agent"]),
            status=TaskStatus(str(payload["status"])),
            attempt=int(payload["attempt"]),
            started_at=str(payload["started_at"]),
            finished_at=str(payload["finished_at"]),
            input_ref=dict(payload.get("input_ref", {})),
            model=str(payload.get("model", "")),
            prompt_version=str(payload.get("prompt_version", "")),
            result=payload.get("result"),
            error=error,
        )


@dataclass(frozen=True)
class PairManifestRecord:
    run_id: str
    dataset_name: str
    pair_id: str
    r1_id: str
    r1_text: str
    r2_id: str
    r2_text: str
    cosine_similarity: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "PairManifestRecord":
        cosine_similarity = payload.get("cosine_similarity")
        return cls(
            run_id=str(payload["run_id"]),
            dataset_name=str(payload["dataset_name"]),
            pair_id=str(payload["pair_id"]),
            r1_id=str(payload["r1_id"]),
            r1_text=str(payload["r1_text"]),
            r2_id=str(payload["r2_id"]),
            r2_text=str(payload["r2_text"]),
            cosine_similarity=None if cosine_similarity is None else float(cosine_similarity),
        )


@dataclass(frozen=True)
class FinalRouteRecord:
    pair_id: str
    route_type: str
    canonical_pair_id: str | None
