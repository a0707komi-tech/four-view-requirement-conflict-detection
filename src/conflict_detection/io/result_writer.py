from __future__ import annotations

import json
from pathlib import Path

from conflict_detection.orchestration.session_types import VerdictResult


def build_verdict_payload(result: VerdictResult) -> dict:
    return {
        "pair_id": result.pair.pair_id,
        "r1_id": result.pair.r1_id,
        "r1_text": result.pair.r1_text,
        "r2_id": result.pair.r2_id,
        "r2_text": result.pair.r2_text,
        "verdict": result.verdict,
        "confidence": result.confidence,
        "early_consensus": result.early_consensus,
        "needs_human_review": result.needs_human_review,
        "total_api_calls": result.total_api_calls,
        "phase1_votes": {
            item.agent: {
                "verdict": item.verdict,
                "confidence": item.confidence,
                "model": item.model,
            }
            for item in result.phase1_results
        },
        "phase2_cross_exam": {
            "target": result.phase2_result.target_agent,
            "challenge": result.phase2_result.challenge,
            "rebuttal_verdict_revised": result.phase2_result.rebuttal.get("verdict_revised", False),
        }
        if result.phase2_result
        else None,
        "arbiter_reasoning": str(result.phase3_result.get("reasoning", "")),
        "uncertainty_source": result.phase3_result.get("uncertainty_source", ""),
        "source_pair_id": result.source_pair_id,
        "resolution_stage": result.resolution_stage,
        "duplicate_conflict": result.duplicate_conflict,
    }


def build_full_payload(result: VerdictResult) -> dict:
    return {
        "pair_id": result.pair.pair_id,
        "verdict": result.verdict,
        "confidence": result.confidence,
        "phase1": [
            {
                "agent": item.agent,
                "model": item.model,
                "verdict": item.verdict,
                "confidence": item.confidence,
                "reasoning": item.reasoning,
                "key_evidence": item.key_evidence,
                "assumptions": item.assumptions,
                "raw_json": item.raw_json,
            }
            for item in result.phase1_results
        ],
        "phase2": {
            "target": result.phase2_result.target_agent,
            "challenge": result.phase2_result.challenge,
            "da_full": result.phase2_result.da_verdict,
            "rebuttal": result.phase2_result.rebuttal,
        }
        if result.phase2_result
        else None,
        "phase3": result.phase3_result,
        "source_pair_id": result.source_pair_id,
        "resolution_stage": result.resolution_stage,
        "duplicate_conflict": result.duplicate_conflict,
    }


def append_verdict_jsonl(result: VerdictResult, output_path: str | Path) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(build_verdict_payload(result), ensure_ascii=False) + "\n")
    return destination


def append_full_jsonl(result: VerdictResult, output_path: str | Path) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(build_full_payload(result), ensure_ascii=False) + "\n")
    return destination


def write_verdicts_jsonl(results: list[VerdictResult], output_path: str | Path) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(build_verdict_payload(result), ensure_ascii=False) + "\n")
    return destination


def write_full_jsonl(results: list[VerdictResult], output_path: str | Path) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(build_full_payload(result), ensure_ascii=False) + "\n")
    return destination


def write_results(
    results: list[VerdictResult],
    *,
    output_root: str | Path,
    dataset_name: str,
    run_id: str,
    write_full_trace: bool,
) -> tuple[Path, Path | None]:
    run_dir = Path(output_root) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    verdict_path = write_verdicts_jsonl(results, run_dir / f"{dataset_name}_verdicts.jsonl")
    full_path = None
    if write_full_trace:
        full_path = write_full_jsonl(results, run_dir / f"{dataset_name}_full.jsonl")
    return verdict_path, full_path
