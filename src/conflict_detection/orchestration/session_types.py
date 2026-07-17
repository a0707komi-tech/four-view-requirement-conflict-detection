from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass(frozen=True)
class DetectionPair:
    pair_id: str
    r1_id: str
    r1_text: str
    r2_id: str
    r2_text: str
    cosine_similarity: float | None = None


@dataclass(frozen=True)
class DuplicateRequirementGroup:
    canonical_id: str
    canonical_text: str
    member_ids: list[str]


@dataclass(frozen=True)
class PairRoute:
    pair_id: str
    r1_id: str
    r1_text: str
    r2_id: str
    r2_text: str
    cosine_similarity: float | None = None
    route_type: str = "canonical_candidate"
    canonical_pair_id: str | None = None
    canonical_r1_id: str | None = None
    canonical_r1_text: str | None = None
    canonical_r2_id: str | None = None
    canonical_r2_text: str | None = None


@dataclass(frozen=True)
class PreprocessResult:
    dataset: str
    total_requirements: int
    total_pairs: int
    candidate_count: int
    filtered_count: int
    threshold: float
    candidate_pairs: list[DetectionPair]
    filtered_pairs: list[DetectionPair]
    duplicate_groups: list[DuplicateRequirementGroup] = field(default_factory=list)
    canonical_requirement_map: dict[str, str] = field(default_factory=dict)
    pair_routes: list[PairRoute] = field(default_factory=list)


@dataclass(frozen=True)
class PromptMetadata:
    role_name: str
    supports_system_role: bool
    temperature_policy: dict[str, Any]
    max_tokens_policy: dict[str, Any]
    paper_patterns: Sequence[str]


@dataclass(frozen=True)
class PromptBundle:
    metadata: PromptMetadata
    system_prompt: str | None
    user_prompt: str


@dataclass
class AgentDecision:
    agent: str
    model: str
    verdict: str
    confidence: float
    reasoning: str
    key_evidence: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    pairwise_conflict_grounded: bool = True
    global_unsat_proven: bool = False
    raw_json: dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""
    pair_id: str = ""


@dataclass
class CrossExamResult:
    da_verdict: dict[str, Any] = field(default_factory=dict)
    target_agent: str = ""
    challenge: str = ""
    rebuttal: dict[str, Any] = field(default_factory=dict)


@dataclass
class VerdictResult:
    pair: DetectionPair
    verdict: str
    confidence: float
    phase1_results: list[AgentDecision] = field(default_factory=list)
    phase2_result: CrossExamResult | None = None
    phase3_result: dict[str, Any] = field(default_factory=dict)
    early_consensus: bool = False
    needs_human_review: bool = False
    total_api_calls: int = 0
    source_pair_id: str | None = None
    resolution_stage: str = "full_pipeline"
    duplicate_conflict: bool = False
