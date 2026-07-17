from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from conflict_detection.io.result_writer import build_full_payload, build_verdict_payload
from conflict_detection.orchestration.session_types import AgentDecision, CrossExamResult, DetectionPair, VerdictResult
from conflict_detection.runtime.consensus import evaluate_strict_consensus_from_decisions
from conflict_detection.runtime.contracts import AgentRecord, PairManifestRecord, TaskStatus
from conflict_detection.runtime.executors.base import PHASE1_AGENT_NAMES
from conflict_detection.runtime.result_store import AgentResultStore
from conflict_detection.runtime.route_manifest import load_pair_routes_manifest
from conflict_detection.runtime.run_manifest import load_pair_manifest

PIPELINE_AGENT_NAMES = PHASE1_AGENT_NAMES + ("da", "rebuttal", "arbiter")


class FinalizerOutputs:
    def __init__(
        self,
        *,
        final_index_path: Path,
        verdict_path: Path,
        full_path: Path,
        split_report_paths: dict[str, Path],
    ) -> None:
        self.final_index_path = final_index_path
        self.verdict_path = verdict_path
        self.full_path = full_path
        self.split_report_paths = split_report_paths


def rebuild_final_outputs(run_dir: str | Path, *, dataset_name: str) -> FinalizerOutputs:
    run_path = Path(run_dir)
    store = AgentResultStore(run_path)
    final_index_path = run_path / "manifests" / "final_index.jsonl"
    verdict_path = run_path / f"{dataset_name}_verdicts.jsonl"
    full_path = run_path / f"{dataset_name}_full.jsonl"
    final_index_path.parent.mkdir(parents=True, exist_ok=True)

    manifest_lookup = {
        item.pair_id: item for item in load_pair_manifest(run_path / "manifests" / "pairs.jsonl")
    }
    pair_routes = load_pair_routes_manifest(run_path / "manifests" / "pair_routes.jsonl")
    latest_records_by_agent = {
        agent_name: store.load_latest_records(agent_name)
        for agent_name in PIPELINE_AGENT_NAMES
    }
    canonical_results = _build_canonical_results(latest_records_by_agent, manifest_lookup, pair_routes)
    expanded_results = _expand_results(pair_routes, canonical_results)
    split_report_paths = _write_split_reports(run_path, dataset_name=dataset_name, results=expanded_results)

    ordered_pair_ids = sorted(expanded_results.keys(), key=_pair_sort_key)
    with final_index_path.open("w", encoding="utf-8") as final_handle, verdict_path.open(
        "w", encoding="utf-8"
    ) as verdict_handle, full_path.open("w", encoding="utf-8") as full_handle:
        for pair_id in ordered_pair_ids:
            verdict_result = expanded_results[pair_id]
            final_payload = {
                "pair_id": pair_id,
                "verdict": verdict_result.verdict,
                "confidence": verdict_result.confidence,
                "needs_human_review": verdict_result.needs_human_review,
                "dataset_name": dataset_name,
                "run_id": next(iter(manifest_lookup.values())).run_id if manifest_lookup else "",
                "source_pair_id": verdict_result.source_pair_id,
                "resolution_stage": verdict_result.resolution_stage,
                "duplicate_conflict": verdict_result.duplicate_conflict,
            }
            final_handle.write(json.dumps(final_payload, ensure_ascii=False) + "\n")
            verdict_handle.write(json.dumps(build_verdict_payload(verdict_result), ensure_ascii=False) + "\n")
            full_handle.write(json.dumps(build_full_payload(verdict_result), ensure_ascii=False) + "\n")

    return FinalizerOutputs(
        final_index_path=final_index_path,
        verdict_path=verdict_path,
        full_path=full_path,
        split_report_paths=split_report_paths,
    )


def _build_canonical_results(
    latest_records_by_agent: dict[str, dict[str, AgentRecord]],
    manifest_lookup: dict[str, PairManifestRecord],
    pair_routes,
) -> dict[str, VerdictResult]:
    canonical_pair_ids = list(
        dict.fromkeys(
            route.canonical_pair_id or route.pair_id
            for route in pair_routes
            if route.route_type == "canonical_candidate"
        )
    )
    return {
        pair_id: _rebuild_verdict_result(pair_id, latest_records_by_agent, manifest_lookup)
        for pair_id in canonical_pair_ids
    }


def _expand_results(
    pair_routes,
    canonical_results: dict[str, VerdictResult],
) -> dict[str, VerdictResult]:
    expanded: dict[str, VerdictResult] = {}
    for route in pair_routes:
        pair = DetectionPair(
            pair_id=route.pair_id,
            r1_id=route.r1_id,
            r1_text=route.r1_text,
            r2_id=route.r2_id,
            r2_text=route.r2_text,
            cosine_similarity=route.cosine_similarity,
        )

        if route.route_type == "duplicate_conflict":
            expanded[route.pair_id] = VerdictResult(
                pair=pair,
                verdict="incompatible",
                confidence=1.0,
                phase1_results=[],
                phase2_result=None,
                phase3_result={
                    "verdict": "incompatible",
                    "confidence": 1.0,
                    "reasoning": "Classified as duplicate conflict through canonical duplicate-group routing.",
                    "uncertainty_source": "none",
                    "needs_human_review": False,
                },
                early_consensus=False,
                needs_human_review=False,
                total_api_calls=0,
                source_pair_id=None,
                resolution_stage="duplicate_group_rule",
                duplicate_conflict=True,
            )
            continue

        if route.route_type == "filtered_non_candidate":
            continue

        source_pair_id = route.canonical_pair_id
        if source_pair_id is None:
            continue
        base = canonical_results[source_pair_id]
        resolution_stage = "canonical_candidate" if route.route_type == "canonical_candidate" else "canonical_alias"
        expanded[route.pair_id] = replace(
            base,
            pair=pair,
            source_pair_id=source_pair_id if route.route_type == "canonical_alias" else None,
            resolution_stage=resolution_stage,
            duplicate_conflict=False,
        )
    return expanded


def _write_split_reports(
    run_path: Path,
    *,
    dataset_name: str,
    results: dict[str, VerdictResult],
) -> dict[str, Path]:
    report_dir = run_path / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    buckets: dict[str, list[dict[str, object]]] = {
        "incompatible": [],
        "compatible": [],
        "uncertain": [],
    }
    for pair_id in sorted(results.keys(), key=_pair_sort_key):
        verdict_result = results[pair_id]
        route_type = _infer_route_type(verdict_result)
        row = _build_split_report_row(pair_id, verdict_result, route_type=route_type)
        if verdict_result.duplicate_conflict or verdict_result.verdict == "incompatible":
            buckets["incompatible"].append(row)
        elif verdict_result.verdict == "compatible":
            buckets["compatible"].append(row)
        else:
            buckets["uncertain"].append(row)

    paths = {
        "incompatible": report_dir / f"{dataset_name}_incompatible_report.jsonl",
        "compatible": report_dir / f"{dataset_name}_compatible_report.jsonl",
        "uncertain": report_dir / f"{dataset_name}_uncertain_report.jsonl",
        "summary": report_dir / f"{dataset_name}_report_summary.json",
    }
    for bucket_name in ("incompatible", "compatible", "uncertain"):
        _write_jsonl(paths[bucket_name], buckets[bucket_name])

    summary = {
        "dataset_name": dataset_name,
        "total_pairs": sum(len(rows) for rows in buckets.values()),
        "incompatible_count": len(buckets["incompatible"]),
        "compatible_count": len(buckets["compatible"]),
        "uncertain_count": len(buckets["uncertain"]),
    }
    paths["summary"].write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return paths


def _build_split_report_row(
    pair_id: str,
    verdict_result: VerdictResult,
    *,
    route_type: str,
) -> dict[str, object]:
    return {
        "pair_id": pair_id,
        "source_pair_id": verdict_result.source_pair_id,
        "route_type": route_type,
        "resolution_stage": verdict_result.resolution_stage,
        "verdict": verdict_result.verdict,
        "confidence": verdict_result.confidence,
        "needs_human_review": verdict_result.needs_human_review,
        "duplicate_conflict": verdict_result.duplicate_conflict,
        "total_api_calls": verdict_result.total_api_calls,
        "phase1_votes": {
            item.agent: {
                "verdict": item.verdict,
                "confidence": item.confidence,
                "reasoning": item.reasoning,
                "key_evidence": list(item.key_evidence),
                "assumptions": list(item.assumptions),
            }
            for item in verdict_result.phase1_results
        },
        "phase2_target": verdict_result.phase2_result.target_agent if verdict_result.phase2_result else "",
        "arbiter_reasoning": str(verdict_result.phase3_result.get("reasoning", "")),
        "uncertainty_source": verdict_result.phase3_result.get("uncertainty_source", ""),
        "key_evidence": _collect_key_evidence(verdict_result),
        "assumptions": _collect_assumptions(verdict_result),
    }


def _infer_route_type(verdict_result: VerdictResult) -> str:
    if verdict_result.duplicate_conflict:
        return "duplicate_conflict"
    if verdict_result.source_pair_id is not None:
        return "canonical_alias"
    return "canonical_candidate"


def _collect_key_evidence(verdict_result: VerdictResult) -> list[str]:
    evidence: list[str] = []
    for item in verdict_result.phase1_results:
        evidence.extend(item.key_evidence)
    if verdict_result.phase2_result is not None:
        evidence.extend(
            str(item)
            for item in verdict_result.phase2_result.da_verdict.get("key_evidence", [])
            if item
        )
    reasoning = str(verdict_result.phase3_result.get("reasoning", ""))
    if reasoning:
        evidence.append(reasoning)
    return [item for item in dict.fromkeys(evidence) if item]


def _collect_assumptions(verdict_result: VerdictResult) -> list[str]:
    assumptions: list[str] = []
    for item in verdict_result.phase1_results:
        assumptions.extend(item.assumptions)
    if verdict_result.phase2_result is not None:
        assumptions.extend(
            str(item)
            for item in verdict_result.phase2_result.da_verdict.get("assumptions", [])
            if item
        )
    return [item for item in dict.fromkeys(assumptions) if item]


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> Path:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path


def _rebuild_verdict_result(
    pair_id: str,
    latest_records_by_agent: dict[str, dict[str, AgentRecord]],
    manifest_lookup: dict[str, PairManifestRecord],
) -> VerdictResult:
    phase1_records = {
        agent_name: latest_records_by_agent.get(agent_name, {}).get(pair_id)
        for agent_name in PHASE1_AGENT_NAMES
    }
    da_record = latest_records_by_agent.get("da", {}).get(pair_id)
    rebuttal_record = latest_records_by_agent.get("rebuttal", {}).get(pair_id)
    arbiter_record = latest_records_by_agent.get("arbiter", {}).get(pair_id)
    manifest_record = manifest_lookup[pair_id]
    pair = DetectionPair(
        pair_id=pair_id,
        r1_id=manifest_record.r1_id,
        r1_text=manifest_record.r1_text,
        r2_id=manifest_record.r2_id,
        r2_text=manifest_record.r2_text,
        cosine_similarity=manifest_record.cosine_similarity,
    )
    if arbiter_record is not None and arbiter_record.status == TaskStatus.SUCCEEDED:
        return _rebuild_completed_verdict_result(
            pair=pair,
            phase1_records=phase1_records,
            da_record=da_record,
            rebuttal_record=rebuttal_record,
            arbiter_record=arbiter_record,
        )

    strict_consensus = _strict_consensus_from_phase1_records(pair=pair, phase1_records=phase1_records)
    if strict_consensus is not None:
        verdict, confidence = strict_consensus
        return _build_strict_consensus_verdict_result(
            pair=pair,
            phase1_records=phase1_records,
            verdict=verdict,
            confidence=confidence,
        )

    pipeline_status, reasoning = _infer_incomplete_pipeline_reason(
        phase1_records=phase1_records,
        da_record=da_record,
        rebuttal_record=rebuttal_record,
        arbiter_record=arbiter_record,
    )
    phase1_results = [
        _agent_decision_from_phase1_record(agent_name, phase1_records.get(agent_name))
        for agent_name in PHASE1_AGENT_NAMES
    ]
    phase2_result = _rebuild_partial_phase2_result(da_record=da_record, rebuttal_record=rebuttal_record)
    total_api_calls = _count_observed_api_calls(
        list(phase1_records.values()) + [da_record, rebuttal_record, arbiter_record]
    )
    phase3_result = {
        "verdict": "uncertain",
        "confidence": 0.0,
        "reasoning": reasoning,
        "uncertainty_source": pipeline_status,
        "needs_human_review": True,
        "pipeline_status": pipeline_status,
    }
    return VerdictResult(
        pair=pair,
        verdict="uncertain",
        confidence=0.0,
        phase1_results=phase1_results,
        phase2_result=phase2_result,
        phase3_result=phase3_result,
        early_consensus=False,
        needs_human_review=True,
        total_api_calls=total_api_calls,
        source_pair_id=None,
        resolution_stage="full_pipeline",
        duplicate_conflict=False,
    )


def _rebuild_completed_verdict_result(
    *,
    pair: DetectionPair,
    phase1_records: dict[str, AgentRecord | None],
    da_record: AgentRecord | None,
    rebuttal_record: AgentRecord | None,
    arbiter_record: AgentRecord,
) -> VerdictResult:
    phase1_results = [_agent_decision_from_record(phase1_records[agent_name]) for agent_name in PHASE1_AGENT_NAMES]
    phase3_result = dict((arbiter_record.result or {}).get("arbiter_output", {}))
    da_payload = dict((da_record.result or {}).get("cross_exam", {})) if da_record and da_record.result else {}
    rebuttal_payload = (
        dict((rebuttal_record.result or {}).get("rebuttal", {}))
        if rebuttal_record and rebuttal_record.result
        else {}
    )
    early_consensus = bool(phase3_result.get("early_consensus", False))
    phase2_result = None
    if not da_payload.get("skipped", False):
        phase2_result = CrossExamResult(
            da_verdict=dict(da_payload.get("da_verdict", {})),
            target_agent=str(da_payload.get("target_agent", "")),
            challenge=str(da_payload.get("challenge", "")),
            rebuttal=rebuttal_payload,
        )

    total_api_calls = len(phase1_results) if early_consensus else 7
    resolution_stage = "phase1_strict_consensus" if early_consensus else "full_pipeline"
    return VerdictResult(
        pair=pair,
        verdict=str(phase3_result.get("verdict", "uncertain")),
        confidence=float(phase3_result.get("confidence", 0.5)),
        phase1_results=phase1_results,
        phase2_result=phase2_result,
        phase3_result=phase3_result,
        early_consensus=early_consensus,
        needs_human_review=bool(phase3_result.get("needs_human_review", False)),
        total_api_calls=total_api_calls,
        source_pair_id=None,
        resolution_stage=resolution_stage,
        duplicate_conflict=False,
    )


def _build_strict_consensus_verdict_result(
    *,
    pair: DetectionPair,
    phase1_records: dict[str, AgentRecord | None],
    verdict: str,
    confidence: float,
) -> VerdictResult:
    phase1_results = [_agent_decision_from_record(phase1_records[agent_name]) for agent_name in PHASE1_AGENT_NAMES]
    phase3_result = {
        "verdict": verdict,
        "confidence": confidence,
        "reasoning": "Rebuilt from strict phase-1 consensus because all four phase-1 agents produced the same verdict.",
        "uncertainty_source": "none",
        "needs_human_review": False,
        "early_consensus": True,
        "consensus_agents": list(PHASE1_AGENT_NAMES),
    }
    return VerdictResult(
        pair=pair,
        verdict=verdict,
        confidence=confidence,
        phase1_results=phase1_results,
        phase2_result=None,
        phase3_result=phase3_result,
        early_consensus=True,
        needs_human_review=False,
        total_api_calls=len(phase1_results),
        source_pair_id=None,
        resolution_stage="phase1_strict_consensus",
        duplicate_conflict=False,
    )


def _strict_consensus_from_phase1_records(
    *,
    pair: DetectionPair,
    phase1_records: dict[str, AgentRecord | None],
) -> tuple[str, float] | None:
    decisions: list[AgentDecision] = []
    for agent_name in PHASE1_AGENT_NAMES:
        record = phase1_records.get(agent_name)
        if record is None or record.status != TaskStatus.SUCCEEDED:
            return None
        decisions.append(_agent_decision_from_record(record))
    evaluated = evaluate_strict_consensus_from_decisions(pair, decisions)
    if evaluated is None:
        return None
    return evaluated.verdict, evaluated.confidence


def _rebuild_partial_phase2_result(
    *,
    da_record: AgentRecord | None,
    rebuttal_record: AgentRecord | None,
) -> CrossExamResult | None:
    if da_record is None or da_record.status != TaskStatus.SUCCEEDED or not da_record.result:
        return None
    da_payload = dict(da_record.result.get("cross_exam", {}))
    if da_payload.get("skipped", False):
        return None
    rebuttal_payload = {}
    if rebuttal_record is not None and rebuttal_record.status == TaskStatus.SUCCEEDED and rebuttal_record.result:
        rebuttal_payload = dict(rebuttal_record.result.get("rebuttal", {}))
    return CrossExamResult(
        da_verdict=dict(da_payload.get("da_verdict", {})),
        target_agent=str(da_payload.get("target_agent", "")),
        challenge=str(da_payload.get("challenge", "")),
        rebuttal=rebuttal_payload,
    )


def _infer_incomplete_pipeline_reason(
    *,
    phase1_records: dict[str, AgentRecord | None],
    da_record: AgentRecord | None,
    rebuttal_record: AgentRecord | None,
    arbiter_record: AgentRecord | None,
) -> tuple[str, str]:
    parse_error_agents = _phase1_parse_error_agents(phase1_records)
    if parse_error_agents:
        agent_list = ", ".join(parse_error_agents)
        return "phase1_parse_error", f"Pipeline halted because phase-1 parse failed for: {agent_list}"
    incomplete_phase1 = [
        (agent_name, phase1_records.get(agent_name))
        for agent_name in PHASE1_AGENT_NAMES
        if phase1_records.get(agent_name) is None or phase1_records.get(agent_name).status != TaskStatus.SUCCEEDED
    ]
    if incomplete_phase1:
        details = "; ".join(_describe_missing_or_failed_record(agent_name, record) for agent_name, record in incomplete_phase1)
        return "phase1_incomplete", f"Pipeline incomplete before debate because phase-1 did not finish: {details}"

    if da_record is None:
        return "da_incomplete", "Pipeline incomplete after phase-1 because the DA result is missing."
    if da_record.status != TaskStatus.SUCCEEDED:
        return "da_failed", f"Pipeline stopped at DA: {_describe_record_status('da', da_record)}"

    if rebuttal_record is None:
        return "rebuttal_incomplete", "Pipeline incomplete after DA because the rebuttal result is missing."
    if rebuttal_record.status != TaskStatus.SUCCEEDED:
        return "rebuttal_failed", f"Pipeline stopped at rebuttal: {_describe_record_status('rebuttal', rebuttal_record)}"

    if arbiter_record is None:
        return "arbiter_incomplete", "Pipeline incomplete after rebuttal because the arbiter result is missing."
    if arbiter_record.status != TaskStatus.SUCCEEDED:
        return "arbiter_failed", f"Pipeline stopped at arbiter: {_describe_record_status('arbiter', arbiter_record)}"

    return "pipeline_error", "Pipeline state is inconsistent: canonical pair has no rebuildable final verdict."


def _phase1_parse_error_agents(phase1_records: dict[str, AgentRecord | None]) -> list[str]:
    agents: list[str] = []
    for agent_name in PHASE1_AGENT_NAMES:
        record = phase1_records.get(agent_name)
        if record is None:
            continue
        if record.status == TaskStatus.SUCCEEDED and record.result:
            payload = dict(record.result.get("agent_decision", {}))
            raw_json = dict(payload.get("raw_json", {}))
            if raw_json.get("_parse_error"):
                agents.append(agent_name)
            continue
        if record.error is not None and record.error.type == "TechnicalParseError":
            agents.append(agent_name)
    return agents


def _describe_missing_or_failed_record(agent_name: str, record: AgentRecord | None) -> str:
    if record is None:
        return f"{agent_name} result missing"
    return _describe_record_status(agent_name, record)


def _describe_record_status(agent_name: str, record: AgentRecord) -> str:
    message = f"{agent_name} {record.status.value} at attempt {record.attempt}"
    if record.error is not None:
        error_message = f"{record.error.type}: {record.error.message}".strip()
        message += f" ({_truncate_text(error_message, limit=220)})"
    return message


def _count_observed_api_calls(records: list[AgentRecord | None]) -> int:
    total = 0
    for record in records:
        if record is None:
            continue
        if record.status == TaskStatus.SKIPPED:
            continue
        total += max(0, int(record.attempt))
    return total


def _truncate_text(text: str, *, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _agent_decision_from_record(record: AgentRecord) -> AgentDecision:
    payload = record.result["agent_decision"]
    return AgentDecision(
        agent=record.agent,
        model=record.model,
        verdict=str(payload.get("verdict", "uncertain")),
        confidence=float(payload.get("confidence", 0.5)),
        reasoning=str(payload.get("reasoning", "")),
        key_evidence=list(payload.get("key_evidence", [])),
        assumptions=list(payload.get("assumptions", [])),
        pairwise_conflict_grounded=bool(payload.get("pairwise_conflict_grounded", True)),
        raw_json=dict(payload.get("raw_json", payload)),
        raw_text=str(payload.get("raw_text", "")),
    )


def _agent_decision_from_phase1_record(agent_name: str, record: AgentRecord | None) -> AgentDecision:
    if record is not None and record.status == TaskStatus.SUCCEEDED:
        return _agent_decision_from_record(record)
    reasoning = (
        f"{agent_name} did not complete."
        if record is None
        else f"{agent_name} did not complete: {_describe_record_status(agent_name, record)}"
    )
    return AgentDecision(
        agent=agent_name,
        model="" if record is None else record.model,
        verdict="uncertain",
        confidence=0.0,
        reasoning=reasoning,
        key_evidence=[],
        assumptions=[],
        pairwise_conflict_grounded=False,
        raw_json={},
        raw_text="",
    )


def _pair_sort_key(pair_id: str) -> tuple[int, int, str]:
    left, right = pair_id.split("_", 1)
    return _req_sort_key(left), _req_sort_key(right), pair_id


def _req_sort_key(req_id: str) -> int:
    digits = "".join(char for char in req_id if char.isdigit())
    return int(digits) if digits else 10**12
