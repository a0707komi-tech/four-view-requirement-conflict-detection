from __future__ import annotations

import json
import time
from pathlib import Path
from threading import Lock
from uuid import uuid4

from conflict_detection.runtime.state.schemas import PairWorkingMemory


class StateStore:
    _locks_by_path: dict[str, Lock] = {}
    _locks_guard = Lock()

    def __init__(self, run_dir: str | Path) -> None:
        self.run_dir = Path(run_dir)

    def read_memory(self, pair_id: str) -> PairWorkingMemory | None:
        source = self._path_for(pair_id)
        with self._lock_for(source):
            return self._read_unlocked(source)

    def write_memory(self, memory: PairWorkingMemory) -> Path:
        destination = self._path_for(memory.pair_id)
        with self._lock_for(destination):
            self._write_unlocked(destination, memory)
        return destination

    def update_memory(self, pair_id: str, updater) -> PairWorkingMemory:
        destination = self._path_for(pair_id)
        with self._lock_for(destination):
            current = self._read_unlocked(destination)
            updated = updater(current)
            self._write_unlocked(destination, updated)
            return updated

    def _path_for(self, pair_id: str) -> Path:
        return self.run_dir / "artifacts" / "state" / f"{pair_id}.json"

    def _read_unlocked(self, source: Path) -> PairWorkingMemory | None:
        for attempt in range(5):
            try:
                if not source.exists():
                    return None
                payload = json.loads(source.read_text(encoding="utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError(f"Working memory payload must be an object: {source}")
                return PairWorkingMemory.from_dict(payload)
            except (FileNotFoundError, PermissionError, json.JSONDecodeError):
                if attempt == 4:
                    raise
                time.sleep(0.01)
        return None

    def _write_unlocked(self, destination: Path, memory: PairWorkingMemory) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temp_path = destination.with_name(f"{destination.name}.{uuid4().hex}.tmp")
        temp_path.write_text(json.dumps(memory.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(destination)

    @classmethod
    def _lock_for(cls, path: Path) -> Lock:
        key = str(path.resolve())
        with cls._locks_guard:
            lock = cls._locks_by_path.get(key)
            if lock is None:
                lock = Lock()
                cls._locks_by_path[key] = lock
            return lock
