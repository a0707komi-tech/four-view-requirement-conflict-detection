from __future__ import annotations

import json
from pathlib import Path

from conflict_detection.orchestration.session_types import PromptBundle, PromptMetadata


class PromptLoader:
    def __init__(self, prompt_root: Path):
        self.prompt_root = Path(prompt_root)
        self.shared_core_path = self.prompt_root / "_shared_core.txt"

    def load(self, agent_name: str) -> PromptBundle:
        agent_dir = self.prompt_root / agent_name
        meta_path = agent_dir / "meta.json"
        user_path = agent_dir / "user.txt"
        system_path = agent_dir / "system.txt"

        if not meta_path.exists():
            raise FileNotFoundError(f"Missing prompt metadata: {meta_path}")
        if not user_path.exists():
            raise FileNotFoundError(f"Missing user prompt: {user_path}")

        meta_raw = json.loads(meta_path.read_text(encoding="utf-8"))
        metadata = PromptMetadata(
            role_name=meta_raw["role_name"],
            supports_system_role=bool(meta_raw["supports_system_role"]),
            temperature_policy=dict(meta_raw["temperature_policy"]),
            max_tokens_policy=dict(meta_raw["max_tokens_policy"]),
            paper_patterns=tuple(meta_raw["paper_patterns"]),
        )

        system_prompt = None
        if system_path.exists():
            system_prompt = system_path.read_text(encoding="utf-8").strip()
        else:
            shared_core = self._load_shared_core()
            if shared_core and metadata.supports_system_role:
                system_prompt = shared_core

        return PromptBundle(
            metadata=metadata,
            system_prompt=system_prompt,
            user_prompt=user_path.read_text(encoding="utf-8").strip(),
        )

    def _load_shared_core(self) -> str:
        if not self.shared_core_path.exists():
            return ""
        return self.shared_core_path.read_text(encoding="utf-8").strip()
