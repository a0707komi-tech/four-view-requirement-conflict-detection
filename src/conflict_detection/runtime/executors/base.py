from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from conflict_detection.io.prompt_loader import PromptLoader
from conflict_detection.io.prompt_rendering import render_prompt_template
from conflict_detection.agents.feasibility_agent import FeasibilityAgent
from conflict_detection.agents.goal_agent import GoalAgent
from conflict_detection.agents.logic_agent import LogicAgent
from conflict_detection.agents.semantic_agent import SemanticAgent
from conflict_detection.runtime.consensus import evaluate_strict_consensus_from_summaries
from conflict_detection.runtime.errors import TechnicalParseError
from conflict_detection.llm.request_factory import build_chat_body as build_provider_chat_body
from conflict_detection.orchestration.session_types import AgentDecision, CrossExamResult, DetectionPair
from conflict_detection.llm.response_parser import parse_json_response
from conflict_detection.runtime.artifacts.bundle_store import ArtifactBundleStore
from conflict_detection.runtime.artifacts.debate_summary import (
    build_arbiter_input_bundle,
    build_da_challenge_artifact,
    build_rebuttal_summary_artifact,
)
from conflict_detection.runtime.artifacts.phase1_summary import build_phase1_summary
from conflict_detection.runtime.artifacts.phase1_summary import serialize_phase1_summary
from conflict_detection.runtime.batch.contracts import BatchItemResult
from conflict_detection.runtime.contracts import AgentRecord, AgentTask, TaskStatus
from conflict_detection.runtime.executors.arbiter import execute_arbiter_agent
from conflict_detection.runtime.executors.da import execute_da_agent
from conflict_detection.runtime.executors.rebuttal import execute_rebuttal_agent
from conflict_detection.runtime.state.builder import (
    update_memory_after_arbiter,
    update_memory_after_da,
    update_memory_after_phase1,
    update_memory_after_rebuttal,
)
from conflict_detection.runtime.state.store import StateStore

PHASE1_AGENT_NAMES = ("semantic", "logic", "feasibility", "goal")
PHASE1_AGENT_MAP = {
    "semantic": SemanticAgent,
    "logic": LogicAgent,
    "feasibility": FeasibilityAgent,
    "goal": GoalAgent,
}


@dataclass(frozen=True)
class ExecutorContext:
    pair_lookup: dict[str, object]
    result_store: object
    llm_client: object
    phase1_prompt_root: Path
    debate_prompt_root: Path
    run_dir: Path
    execution_profile_name: str
def execute_agent_task(task: AgentTask, *, context: ExecutorContext) -> AgentRecord:
    pair_record = context.pair_lookup[task.pair_id]
    pair = DetectionPair(
        pair_id=pair_record.pair_id,
        r1_id=pair_record.r1_id,
        r1_text=pair_record.r1_text,
        r2_id=pair_record.r2_id,
        r2_text=pair_record.r2_text,
        cosine_similarity=pair_record.cosine_similarity,
    )
    prompt_loader = PromptLoader(Path(context.debate_prompt_root))
    started_at = _timestamp()
    artifact_store = ArtifactBundleStore(context.run_dir, dataset_name=getattr(pair_record, "dataset_name", None))
    state_store = StateStore(context.run_dir)

    if task.agent in PHASE1_AGENT_NAMES:
        prompt_loader = PromptLoader(Path(context.phase1_prompt_root))
        phase1_agent = PHASE1_AGENT_MAP[task.agent](context.llm_client, prompt_loader)
        decision = phase1_agent.analyze_pair(pair)
        if decision.raw_json.get("_parse_error"):
            raise TechnicalParseError(f"{task.agent} response could not be parsed as JSON")
        summary_artifact = build_phase1_summary(decision, pair_id=task.pair_id)
        artifact_store.write_phase1_summary(summary_artifact)
        all_summaries: dict[str, object] = {}
        for agent_name in PHASE1_AGENT_NAMES:
            try:
                all_summaries[agent_name] = artifact_store.read_phase1_summary(agent_name, task.pair_id)
            except FileNotFoundError:
                continue
        state_store.update_memory(
            task.pair_id,
            lambda memory: update_memory_after_phase1(
                memory,
                pair=pair,
                summary=summary_artifact,
                all_phase1_summaries=all_summaries,
            )
        )
        result = {
            "agent_decision": {
                "agent": decision.agent,
                "model": decision.model,
                "verdict": decision.verdict,
                "confidence": decision.confidence,
                "reasoning": decision.reasoning,
                "key_evidence": list(decision.key_evidence),
                "assumptions": list(decision.assumptions),
                "pairwise_conflict_grounded": decision.pairwise_conflict_grounded,
                "raw_json": dict(decision.raw_json),
                "raw_text": decision.raw_text,
                "pair_id": task.pair_id,
            }
        }
        return _build_record(task, pair, started_at, decision.model, result)

    if task.agent == "da":
        phase1_bundle = artifact_store.load_phase1_bundle(task.pair_id, agent_names=PHASE1_AGENT_NAMES)
        early_consensus = evaluate_strict_consensus_from_summaries(pair, dict(phase1_bundle.summaries))
        if early_consensus is not None:
            verdict = early_consensus.verdict
            confidence = early_consensus.confidence
            if state_store.read_memory(task.pair_id) is not None:
                state_store.update_memory(
                    task.pair_id,
                    lambda memory: update_memory_after_phase1(
                        memory,
                        pair=pair,
                        summary=next(iter(phase1_bundle.summaries.values())),
                        all_phase1_summaries=dict(phase1_bundle.summaries),
                    )
                )
            result = {
                "cross_exam": {
                    "skipped": True,
                    "reason": "strict_phase1_consensus",
                    "consensus_verdict": verdict,
                    "consensus_confidence": confidence,
                }
            }
            state_store.update_memory(
                task.pair_id,
                lambda memory: update_memory_after_da(
                    memory,
                    challenge=build_da_challenge_artifact(
                        CrossExamResult(
                            da_verdict={
                                "target_agent": "semantic",
                                "challenge": "Strict phase-1 consensus: DA skipped.",
                                "challenge_type": "strict_consensus_skip",
                                "reason": "All four phase-1 agents produced the same verdict.",
                            },
                            target_agent="semantic",
                            challenge="Strict phase-1 consensus: DA skipped.",
                            rebuttal={},
                        ),
                        pair_id=task.pair_id,
                    ),
                ),
            )
            return _build_record(task, pair, started_at, "skipped", result)
        cross_exam = execute_da_agent(context.llm_client, prompt_loader, pair, phase1_bundle)
        da_artifact = build_da_challenge_artifact(cross_exam, pair_id=task.pair_id)
        artifact_store.write_da_challenge(da_artifact)
        state_store.update_memory(
            task.pair_id,
            lambda memory: update_memory_after_da(memory, challenge=da_artifact),
        )
        result = {"cross_exam": _cross_exam_payload(cross_exam)}
        return _build_record(task, pair, started_at, context.llm_client.get_model_name("da"), result)

    if task.agent == "rebuttal":
        phase1_bundle = artifact_store.load_phase1_bundle(task.pair_id, agent_names=PHASE1_AGENT_NAMES)
        early_consensus = evaluate_strict_consensus_from_summaries(pair, dict(phase1_bundle.summaries))
        if early_consensus is not None:
            verdict = early_consensus.verdict
            confidence = early_consensus.confidence
            rebuttal = {
                "skipped": True,
                "reason": "strict_phase1_consensus",
                "consensus_verdict": verdict,
                "consensus_confidence": confidence,
            }
            state_store.update_memory(
                task.pair_id,
                lambda memory: update_memory_after_rebuttal(
                    memory,
                    rebuttal=build_rebuttal_summary_artifact(
                        CrossExamResult(
                            da_verdict={},
                            target_agent="semantic",
                            challenge="Strict phase-1 consensus: rebuttal skipped.",
                            rebuttal={
                                "response": "Strict phase-1 consensus: rebuttal skipped.",
                                "verdict_revised": False,
                                "revised_verdict": "",
                                "unresolved_issues": [],
                            },
                        ),
                        pair_id=task.pair_id,
                    ),
                ),
            )
            return _build_record(task, pair, started_at, "skipped", {"rebuttal": rebuttal})
        da_artifact = artifact_store.read_da_challenge(task.pair_id)
        cross_exam = execute_rebuttal_agent(context.llm_client, prompt_loader, pair, phase1_bundle, da_artifact)
        rebuttal_artifact = build_rebuttal_summary_artifact(cross_exam, pair_id=task.pair_id)
        artifact_store.write_rebuttal_summary(rebuttal_artifact)
        state_store.update_memory(
            task.pair_id,
            lambda memory: update_memory_after_rebuttal(
                memory,
                rebuttal=rebuttal_artifact,
            )
        )
        result = {"rebuttal": dict(cross_exam.rebuttal), "target_agent": cross_exam.target_agent}
        model_name = context.llm_client.get_model_name(cross_exam.target_agent)
        return _build_record(task, pair, started_at, model_name, result)

    if task.agent == "arbiter":
        phase1_bundle = artifact_store.load_phase1_bundle(task.pair_id, agent_names=PHASE1_AGENT_NAMES)
        early_consensus = evaluate_strict_consensus_from_summaries(pair, dict(phase1_bundle.summaries))
        if early_consensus is not None:
            verdict = early_consensus.verdict
            confidence = early_consensus.confidence
            arbiter_output = {
                "verdict": verdict,
                "confidence": confidence,
                "reasoning": "Skipped debate and arbitration because all four phase-1 agents produced the same verdict.",
                "uncertainty_source": "none",
                "needs_human_review": False,
                "early_consensus": True,
                "consensus_agents": list(PHASE1_AGENT_NAMES),
            }
            state_store.update_memory(
                task.pair_id,
                lambda memory: update_memory_after_arbiter(
                    memory,
                    pair_id=task.pair_id,
                    arbiter_output=arbiter_output,
                ),
            )
            result = {"arbiter_output": arbiter_output}
            return _build_record(task, pair, started_at, "skipped", result)
        da_artifact = artifact_store.read_da_challenge(task.pair_id)
        rebuttal_artifact = artifact_store.read_rebuttal_summary(task.pair_id)
        arbiter_bundle = build_arbiter_input_bundle(phase1_bundle, da_artifact, rebuttal_artifact)
        artifact_store.write_arbiter_bundle(arbiter_bundle)
        arbiter_output = execute_arbiter_agent(context.llm_client, prompt_loader, pair, arbiter_bundle)
        state_store.update_memory(
            task.pair_id,
            lambda memory: update_memory_after_arbiter(
                memory,
                pair_id=task.pair_id,
                arbiter_output=arbiter_output,
            )
        )
        result = {"arbiter_output": arbiter_output}
        return _build_record(task, pair, started_at, context.llm_client.get_model_name("arbiter"), result)

    raise ValueError(f"Unsupported agent: {task.agent}")

def execute_any_task(task: AgentTask, *, context: ExecutorContext):
    return execute_agent_task(task, context=context)


def build_batch_chat_body(task: AgentTask, *, context: ExecutorContext) -> dict[str, object]:
    pair = _load_pair(task, context=context)
    pair_record = context.pair_lookup[task.pair_id]
    artifact_store = ArtifactBundleStore(context.run_dir, dataset_name=getattr(pair_record, "dataset_name", None))

    if task.agent in PHASE1_AGENT_NAMES:
        prompt_loader = PromptLoader(Path(context.phase1_prompt_root))
        bundle = prompt_loader.load(task.agent)
        user_prompt = PHASE1_AGENT_MAP[task.agent](context.llm_client, prompt_loader).build_user_prompt(bundle.user_prompt, pair)
        return build_provider_chat_body(
            role=task.agent,
            model=context.llm_client.get_batch_model_name(task.agent),
            system_prompt=bundle.system_prompt if bundle.metadata.supports_system_role else None,
            user_prompt=user_prompt,
            temperature=bundle.metadata.temperature_policy.get("value"),
            max_tokens=bundle.metadata.max_tokens_policy.get("value"),
            supports_system_role=bundle.metadata.supports_system_role,
            batch_mode=True,
        )

    if task.agent == "da":
        prompt_loader = PromptLoader(Path(context.debate_prompt_root))
        bundle = prompt_loader.load("da")
        phase1_bundle = artifact_store.load_phase1_bundle(task.pair_id, agent_names=PHASE1_AGENT_NAMES)
        outputs = {
            agent_name: serialize_phase1_summary(summary)
            for agent_name, summary in phase1_bundle.summaries.items()
        }
        prompt = render_prompt_template(
            bundle.user_prompt,
            {
                "r1_text": pair.r1_text,
                "r2_text": pair.r2_text,
                "semantic_model": context.llm_client.get_batch_model_name("semantic"),
                "semantic_output": outputs.get("semantic", ""),
                "logic_model": context.llm_client.get_batch_model_name("logic"),
                "logic_output": outputs.get("logic", ""),
                "feasibility_model": context.llm_client.get_batch_model_name("feasibility"),
                "feasibility_output": outputs.get("feasibility", ""),
                "goal_model": context.llm_client.get_batch_model_name("goal"),
                "goal_output": outputs.get("goal", ""),
            },
        )
        return build_provider_chat_body(
            role="da",
            model=context.llm_client.get_batch_model_name("da"),
            system_prompt=bundle.system_prompt if bundle.metadata.supports_system_role else None,
            user_prompt=prompt,
            temperature=bundle.metadata.temperature_policy.get("value"),
            max_tokens=bundle.metadata.max_tokens_policy.get("value"),
            supports_system_role=bundle.metadata.supports_system_role,
            batch_mode=True,
        )

    raise ValueError(f"Batch mode is not supported for agent: {task.agent}")


def build_record_from_batch_result(
    task: AgentTask,
    batch_result: BatchItemResult,
    *,
    context: ExecutorContext,
) -> AgentRecord:
    pair = _load_pair(task, context=context)
    pair_record = context.pair_lookup[task.pair_id]
    artifact_store = ArtifactBundleStore(context.run_dir, dataset_name=getattr(pair_record, "dataset_name", None))
    state_store = StateStore(context.run_dir)
    started_at = _timestamp()

    if task.agent in PHASE1_AGENT_NAMES:
        parsed = parse_json_response(batch_result.raw_text)
        if parsed.get("_parse_error"):
            raise TechnicalParseError(f"{task.agent} batch response could not be parsed as JSON")
        decision = AgentDecision(
            agent=task.agent,
            model=context.llm_client.get_batch_model_name(task.agent),
            verdict=str(parsed.get("verdict", "uncertain")),
            confidence=float(parsed.get("confidence", 0.5)),
            reasoning=str(parsed.get("reasoning", "")),
            key_evidence=list(parsed.get("key_evidence", [])),
            assumptions=list(parsed.get("assumptions", [])),
            pairwise_conflict_grounded=bool(parsed.get("pairwise_conflict_grounded", True)),
            raw_json=parsed,
            raw_text=batch_result.raw_text,
            pair_id=task.pair_id,
        )
        summary_artifact = build_phase1_summary(decision, pair_id=task.pair_id)
        artifact_store.write_phase1_summary(summary_artifact)
        all_summaries: dict[str, object] = {}
        for agent_name in PHASE1_AGENT_NAMES:
            try:
                all_summaries[agent_name] = artifact_store.read_phase1_summary(agent_name, task.pair_id)
            except FileNotFoundError:
                continue
        state_store.update_memory(
            task.pair_id,
            lambda memory: update_memory_after_phase1(
                memory,
                pair=pair,
                summary=summary_artifact,
                all_phase1_summaries=all_summaries,
            )
        )
        return _build_record(
            task,
            pair,
            started_at,
            decision.model,
            {
                "agent_decision": {
                    "agent": decision.agent,
                    "model": decision.model,
                    "verdict": decision.verdict,
                    "confidence": decision.confidence,
                    "reasoning": decision.reasoning,
                    "key_evidence": list(decision.key_evidence),
                    "assumptions": list(decision.assumptions),
                    "pairwise_conflict_grounded": decision.pairwise_conflict_grounded,
                    "raw_json": dict(decision.raw_json),
                    "raw_text": decision.raw_text,
                    "pair_id": task.pair_id,
                }
            },
        )

    if task.agent == "da":
        parsed = parse_json_response(batch_result.raw_text)
        if parsed.get("_parse_error"):
            raise ValueError(f"DA response could not be parsed as JSON: {batch_result.raw_text[:200]}")
        cross_exam = CrossExamResult(
            da_verdict=parsed,
            target_agent=str(parsed.get("target_agent", "")),
            challenge=str(parsed.get("challenge", "")),
            rebuttal={},
        )
        da_artifact = build_da_challenge_artifact(cross_exam, pair_id=task.pair_id)
        artifact_store.write_da_challenge(da_artifact)
        state_store.update_memory(
            task.pair_id,
            lambda memory: update_memory_after_da(memory, challenge=da_artifact),
        )
        return _build_record(
            task,
            pair,
            started_at,
            context.llm_client.get_batch_model_name("da"),
            {"cross_exam": _cross_exam_payload(cross_exam)},
        )

    raise ValueError(f"Batch result handling is not supported for agent: {task.agent}")


def _cross_exam_payload(cross_exam: CrossExamResult) -> dict:
    return {
        "da_verdict": dict(cross_exam.da_verdict),
        "target_agent": cross_exam.target_agent,
        "challenge": cross_exam.challenge,
        "rebuttal": dict(cross_exam.rebuttal),
    }


def _load_pair(task: AgentTask, *, context: ExecutorContext) -> DetectionPair:
    pair_record = context.pair_lookup[task.pair_id]
    return DetectionPair(
        pair_id=pair_record.pair_id,
        r1_id=pair_record.r1_id,
        r1_text=pair_record.r1_text,
        r2_id=pair_record.r2_id,
        r2_text=pair_record.r2_text,
        cosine_similarity=pair_record.cosine_similarity,
    )


def _build_record(
    task: AgentTask,
    pair: DetectionPair,
    started_at: str,
    model_name: str,
    result: dict,
) -> AgentRecord:
    return AgentRecord(
        run_id=task.run_id,
        pair_id=task.pair_id,
        agent=task.agent,
        status=TaskStatus.SUCCEEDED,
        attempt=task.attempt,
        started_at=started_at,
        finished_at=_timestamp(),
        input_ref={"r1_id": pair.r1_id, "r2_id": pair.r2_id},
        model=model_name,
        prompt_version=f"{task.agent}-v1",
        result=result,
        error=None,
    )


def build_success_record(
    *,
    run_id: str,
    pair_id: str,
    agent: str,
    attempt: int,
    pair: DetectionPair,
    started_at: str,
    model_name: str,
    result: dict,
) -> AgentRecord:
    return AgentRecord(
        run_id=run_id,
        pair_id=pair_id,
        agent=agent,
        status=TaskStatus.SUCCEEDED,
        attempt=attempt,
        started_at=started_at,
        finished_at=_timestamp(),
        input_ref={"r1_id": pair.r1_id, "r2_id": pair.r2_id},
        model=model_name,
        prompt_version=f"{agent}-v1",
        result=result,
        error=None,
    )


def _timestamp() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()
