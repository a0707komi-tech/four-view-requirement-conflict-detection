from __future__ import annotations

import json
from pathlib import Path

from conflict_detection.runtime.artifacts.schemas import (
    ArbiterInputBundle,
    DaChallengeArtifact,
    Phase1SummaryArtifact,
    Phase1SummaryBundle,
    RebuttalSummaryArtifact,
)
from conflict_detection.runtime.output_layout import (
    load_dataset_name,
    phase1_artifact_path,
    stage_artifact_path,
)


class ArtifactBundleStore:
    def __init__(self, run_dir: str | Path, *, dataset_name: str | None = None) -> None:
        self.run_dir = Path(run_dir)
        self._dataset_name = dataset_name

    def write_phase1_summary(self, summary: Phase1SummaryArtifact) -> Path:
        destination = phase1_artifact_path(
            self.run_dir,
            agent_name=summary.agent,
            dataset_name=self.dataset_name,
            pair_id=summary.pair_id,
        )
        return self._write_json(destination, summary.to_dict())

    def read_phase1_summary(self, agent_name: str, pair_id: str) -> Phase1SummaryArtifact:
        source = phase1_artifact_path(
            self.run_dir,
            agent_name=agent_name,
            dataset_name=self.dataset_name,
            pair_id=pair_id,
        )
        return Phase1SummaryArtifact.from_dict(self._read_json(source))

    def load_phase1_bundle(self, pair_id: str, *, agent_names: tuple[str, ...]) -> Phase1SummaryBundle:
        return Phase1SummaryBundle(
            pair_id=pair_id,
            summaries={agent_name: self.read_phase1_summary(agent_name, pair_id) for agent_name in agent_names},
        )

    def write_da_challenge(self, artifact: DaChallengeArtifact) -> Path:
        destination = stage_artifact_path(
            self.run_dir,
            stage_name="da",
            dataset_name=self.dataset_name,
            pair_id=artifact.pair_id,
        )
        return self._write_json(destination, artifact.to_dict())

    def read_da_challenge(self, pair_id: str) -> DaChallengeArtifact:
        source = stage_artifact_path(
            self.run_dir,
            stage_name="da",
            dataset_name=self.dataset_name,
            pair_id=pair_id,
        )
        return DaChallengeArtifact.from_dict(self._read_json(source))

    def write_rebuttal_summary(self, artifact: RebuttalSummaryArtifact) -> Path:
        destination = stage_artifact_path(
            self.run_dir,
            stage_name="rebuttal",
            dataset_name=self.dataset_name,
            pair_id=artifact.pair_id,
        )
        return self._write_json(destination, artifact.to_dict())

    def read_rebuttal_summary(self, pair_id: str) -> RebuttalSummaryArtifact:
        source = stage_artifact_path(
            self.run_dir,
            stage_name="rebuttal",
            dataset_name=self.dataset_name,
            pair_id=pair_id,
        )
        return RebuttalSummaryArtifact.from_dict(self._read_json(source))

    def write_arbiter_bundle(self, bundle: ArbiterInputBundle) -> Path:
        destination = stage_artifact_path(
            self.run_dir,
            stage_name="arbiter",
            dataset_name=self.dataset_name,
            pair_id=bundle.pair_id,
        )
        return self._write_json(destination, bundle.to_dict())

    def read_arbiter_bundle(self, pair_id: str) -> ArbiterInputBundle:
        source = stage_artifact_path(
            self.run_dir,
            stage_name="arbiter",
            dataset_name=self.dataset_name,
            pair_id=pair_id,
        )
        return ArbiterInputBundle.from_dict(self._read_json(source))

    def _write_json(self, destination: Path, payload: dict[str, object]) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return destination

    def _read_json(self, source: Path) -> dict[str, object]:
        if not source.exists():
            raise FileNotFoundError(f"Missing artifact file: {source}")
        payload = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"Artifact payload must be an object: {source}")
        return payload

    @property
    def dataset_name(self) -> str:
        if self._dataset_name is None:
            self._dataset_name = load_dataset_name(self.run_dir)
        return self._dataset_name
