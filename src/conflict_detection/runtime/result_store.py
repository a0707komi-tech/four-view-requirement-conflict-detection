from __future__ import annotations

import json
from pathlib import Path

from conflict_detection.runtime.contracts import AgentRecord
from conflict_detection.runtime.output_layout import agent_results_path, load_dataset_name


class AgentResultStore:
    def __init__(self, run_dir: str | Path, *, dataset_name: str | None = None) -> None:
        self.run_dir = Path(run_dir)
        self._dataset_name = dataset_name

    def append_record(self, agent_name: str, record: AgentRecord) -> Path:
        destination = agent_results_path(self.run_dir, agent_name=agent_name, dataset_name=self.dataset_name)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
        return destination

    def load_latest_records(self, agent_name: str) -> dict[str, AgentRecord]:
        source = agent_results_path(self.run_dir, agent_name=agent_name, dataset_name=self.dataset_name)
        if not source.exists():
            return {}

        latest: dict[str, AgentRecord] = {}
        with source.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                record = AgentRecord.from_dict(json.loads(line))
                latest[record.pair_id] = record
        return latest

    @property
    def dataset_name(self) -> str:
        if self._dataset_name is None:
            self._dataset_name = load_dataset_name(self.run_dir)
        return self._dataset_name
