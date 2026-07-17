from __future__ import annotations

import argparse
import json
from pathlib import Path

from config.execution_profiles import load_execution_profile
from conflict_detection.runtime.executors.base import (
    ExecutorContext,
    build_batch_chat_body,
    build_record_from_batch_result,
    execute_any_task,
)
from conflict_detection.runtime.result_store import AgentResultStore
from conflict_detection.runtime.run_manifest import load_pair_manifest
from conflict_detection.runtime.scheduler import Scheduler

DEFAULT_AGENT_ORDER = ("semantic", "logic", "feasibility", "goal", "da", "rebuttal", "arbiter")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the agent-first conflict detection scheduler.")
    parser.add_argument("--run-dir", required=True, help="Prepared run directory")
    parser.add_argument("--profile", default="", help="Optional execution profile override")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    from conflict_detection.llm.client import LLMClient

    run_dir = Path(args.run_dir)
    scheduler_state_path = run_dir / "manifests" / "scheduler_state.json"
    scheduler_state = json.loads(scheduler_state_path.read_text(encoding="utf-8"))
    profile_name = args.profile or str(scheduler_state.get("profile_name", "phase1_batch"))
    profile = load_execution_profile(profile_name)
    manifest = load_pair_manifest(run_dir / "manifests" / "pairs.jsonl")
    pair_lookup = {record.pair_id: record for record in manifest}
    result_store = AgentResultStore(run_dir)
    llm_client = LLMClient()
    context = ExecutorContext(
        pair_lookup=pair_lookup,
        result_store=result_store,
        llm_client=llm_client,
        phase1_prompt_root=profile.phase1_prompt_root,
        debate_prompt_root=profile.debate_prompt_root,
        run_dir=run_dir,
        execution_profile_name=profile.name,
    )
    scheduler = Scheduler(
        run_id=str(scheduler_state["run_id"]),
        run_dir=run_dir,
        pair_lookup=pair_lookup,
        result_store=result_store,
        execute_task=lambda task: execute_any_task(task, context=context),
        build_batch_chat_body=lambda task, *, context=context: build_batch_chat_body(task, context=context),
        build_record_from_batch_result=lambda task, batch_result, *, context=context: build_record_from_batch_result(
            task,
            batch_result,
            context=context,
        ),
        llm_client=llm_client,
        executor_context=context,
        agent_names=DEFAULT_AGENT_ORDER,
        global_max_workers=profile.scheduler.global_max_workers,
        per_agent_max_workers=dict(profile.scheduler.per_agent_max_workers),
        max_attempts=dict(profile.scheduler.max_attempts),
        role_execution=_effective_role_execution(profile.role_execution, llm_client),
    )
    effective_profile_path = run_dir / "manifests" / "effective_execution_profile.json"
    effective_profile_path.write_text(
        json.dumps(
            {
                "profile_name": profile.name,
                "role_execution": {
                    role: {
                        "mode": cfg.mode,
                        "provider": cfg.provider,
                        "batch_max_items": cfg.batch_max_items,
                    }
                    for role, cfg in scheduler.role_execution.items()
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    summary = scheduler.run()
    scheduler_state_path.write_text(
        json.dumps(
            {
                **scheduler_state,
                "profile_name": profile.name,
                "completed": summary.completed,
                "failed": summary.failed,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return 0


def _effective_role_execution(role_execution, llm_client):
    resolved = {}
    for role, cfg in role_execution.items():
        if cfg.mode != "batch":
            resolved[role] = cfg
            continue
        supports_batch = hasattr(llm_client, "supports_batch_submission") and llm_client.supports_batch_submission(role)
        if not supports_batch:
            resolved[role] = type(cfg)(mode="sync", provider=cfg.provider, batch_max_items=1)
            continue
        resolved[role] = cfg
    return resolved


if __name__ == "__main__":
    raise SystemExit(main())
