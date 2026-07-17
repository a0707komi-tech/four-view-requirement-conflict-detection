from __future__ import annotations

import json
import time
from collections import defaultdict
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from config.execution_profiles import RoleExecutionConfig
from conflict_detection.runtime.batch.contracts import BatchJob
from conflict_detection.runtime.batch import BatchItem, BatchStore
from conflict_detection.runtime.contracts import AgentError, AgentRecord, AgentTask, TaskStatus
from conflict_detection.runtime.dependency_graph import is_task_ready
from conflict_detection.runtime.state.schemas import NextAction
from conflict_detection.runtime.state.store import StateStore


@dataclass(frozen=True)
class SchedulerSummary:
    completed: dict[str, int]
    failed: dict[str, int]


class Scheduler:
    def __init__(
        self,
        *,
        run_id: str,
        run_dir: str | Path,
        pair_lookup: dict[str, object],
        result_store,
        execute_task,
        build_batch_chat_body=None,
        build_record_from_batch_result=None,
        llm_client=None,
        executor_context=None,
        agent_names: tuple[str, ...],
        global_max_workers: int,
        per_agent_max_workers: dict[str, int],
        max_attempts: dict[str, int],
        role_execution: dict[str, RoleExecutionConfig] | None = None,
    ) -> None:
        self.run_id = run_id
        self.run_dir = Path(run_dir)
        self.pair_lookup = pair_lookup
        self.result_store = result_store
        self.execute_task = execute_task
        self.build_batch_chat_body = build_batch_chat_body
        self.build_record_from_batch_result = build_record_from_batch_result
        self.llm_client = llm_client
        self.executor_context = executor_context
        self.agent_names = agent_names
        self.global_max_workers = max(1, global_max_workers)
        self.per_agent_max_workers = dict(per_agent_max_workers)
        self.max_attempts = dict(max_attempts)
        self.role_execution = dict(role_execution or {})
        self.batch_store = BatchStore(self.run_dir)
        self.state_store = StateStore(self.run_dir)

    def run(self) -> SchedulerSummary:
        latest_status_by_agent = {
            agent_name: self.result_store.load_latest_records(agent_name) for agent_name in self.agent_names
        }
        in_flight: dict[Future, AgentTask] = {}
        active_per_agent = defaultdict(int)
        pair_ids = list(self.pair_lookup.keys())
        open_batch_jobs: dict[str, dict[str, object]] = self._restore_open_batch_jobs(
            latest_status_by_agent=latest_status_by_agent,
            active_per_agent=active_per_agent,
        )

        with ThreadPoolExecutor(max_workers=self.global_max_workers) as executor:
            while True:
                scheduled_any = self._schedule_ready_tasks(
                    executor,
                    pair_ids,
                    latest_status_by_agent,
                    in_flight,
                    active_per_agent,
                    open_batch_jobs,
                )
                completed_batch = self._poll_batch_jobs(open_batch_jobs, latest_status_by_agent, active_per_agent)
                scheduled_any = scheduled_any or completed_batch

                if not in_flight and not open_batch_jobs and not scheduled_any:
                    break

                if in_flight:
                    done, _ = wait(in_flight.keys(), return_when=FIRST_COMPLETED)
                    for future in done:
                        task = in_flight.pop(future)
                        active_per_agent[task.agent] -= 1
                        try:
                            record = future.result()
                        except Exception as exc:  # noqa: BLE001
                            record = self._exception_records(task, exc)
                        for item in self._as_record_list(record):
                            self.result_store.append_record(item.agent, item)
                            latest_status_by_agent.setdefault(item.agent, {})[item.pair_id] = item

        return SchedulerSummary(
            completed={
                agent_name: sum(
                    1
                    for record in latest_status_by_agent.get(agent_name, {}).values()
                    if record.status is TaskStatus.SUCCEEDED
                )
                for agent_name in self.agent_names
            },
            failed={
                agent_name: sum(
                    1
                    for record in latest_status_by_agent.get(agent_name, {}).values()
                    if record.status in {TaskStatus.FAILED_RETRYABLE, TaskStatus.FAILED_TERMINAL}
                )
                for agent_name in self.agent_names
            },
        )

    def _schedule_ready_tasks(
        self,
        executor: ThreadPoolExecutor,
        pair_ids: list[str],
        latest_status_by_agent,
        in_flight: dict[Future, AgentTask],
        active_per_agent,
        open_batch_jobs,
    ) -> bool:
        scheduled_any = False
        scheduled_any = self._schedule_batch_jobs(pair_ids, latest_status_by_agent, active_per_agent, open_batch_jobs) or scheduled_any
        while len(in_flight) < self.global_max_workers:
            next_task = self._next_ready_task(pair_ids, latest_status_by_agent, in_flight, active_per_agent)
            if next_task is None:
                break
            role_cfg = self.role_execution.get(next_task.agent)
            if role_cfg and role_cfg.mode == "batch" and not self._should_force_sync(next_task.agent, next_task.pair_id):
                break
            future = executor.submit(self.execute_task, next_task)
            in_flight[future] = next_task
            active_per_agent[next_task.agent] += 1
            scheduled_any = True
        return scheduled_any

    def _schedule_batch_jobs(self, pair_ids, latest_status_by_agent, active_per_agent, open_batch_jobs) -> bool:
        scheduled_any = False
        for agent_name in self.agent_names:
            role_cfg = self.role_execution.get(agent_name)
            if role_cfg is None or role_cfg.mode != "batch":
                continue
            if active_per_agent[agent_name] >= self.per_agent_max_workers.get(agent_name, 1):
                continue
            ready: list[AgentTask] = []
            for pair_id in pair_ids:
                if not is_task_ready(agent_name, pair_id, latest_status_by_agent):
                    continue
                if not self._is_task_enabled_by_memory(agent_name, pair_id):
                    continue
                if self._should_force_sync(agent_name, pair_id):
                    continue
                latest_records = latest_status_by_agent.setdefault(agent_name, {})
                latest = latest_records.get(pair_id)
                if latest is None:
                    ready.append(AgentTask(run_id=self.run_id, pair_id=pair_id, agent=agent_name, attempt=1))
                elif latest.status is TaskStatus.FAILED_RETRYABLE and latest.attempt < self.max_attempts.get(agent_name, 1):
                    ready.append(AgentTask(run_id=self.run_id, pair_id=pair_id, agent=agent_name, attempt=latest.attempt + 1))
                if len(ready) >= max(1, role_cfg.batch_max_items):
                    break
            if not ready:
                continue
            self._submit_batch(agent_name, role_cfg, ready, latest_status_by_agent, active_per_agent, open_batch_jobs)
            scheduled_any = True
        return scheduled_any

    def _submit_batch(self, agent_name, role_cfg, tasks, latest_status_by_agent, active_per_agent, open_batch_jobs) -> None:
        provider = self.llm_client.get_provider_client(agent_name)
        timestamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S_%f")
        job_id = f"{agent_name}_{timestamp}"
        items: list[BatchItem] = []
        for task in tasks:
            body = self.build_batch_chat_body(task, context=self.executor_context)
            custom_id = self._custom_id(task)
            item = BatchItem(
                custom_id=custom_id,
                pair_id=task.pair_id,
                agent=task.agent,
                attempt=task.attempt,
                method="POST",
                url="/v1/chat/completions",
                body=body,
            )
            items.append(item)
        request_path = self.batch_store.write_request_items(agent_name, job_id, items)
        batch_job = provider.submit_chat_batch(
            request_file=request_path,
            metadata={"run_id": self.run_id, "agent": agent_name, "provider": role_cfg.provider},
        )
        batch_job = BatchJob(
            job_id=job_id,
            agent=agent_name,
            provider=role_cfg.provider,
            batch_id=batch_job.batch_id,
            input_file_id=batch_job.input_file_id,
            output_file_id=batch_job.output_file_id,
            error_file_id=batch_job.error_file_id,
            status=batch_job.status,
            item_count=len(items),
            item_ids=tuple(item.custom_id for item in items),
            metadata=dict(batch_job.metadata),
        )
        self.batch_store.write_submitted_job(batch_job)
        self.batch_store.write_job_status(batch_job)
        open_batch_jobs[job_id] = {"agent": agent_name, "tasks": tasks, "job": batch_job}
        active_per_agent[agent_name] += 1
        for task in tasks:
            record = self._submitted_record(task)
            self.result_store.append_record(agent_name, record)
            latest_status_by_agent.setdefault(agent_name, {})[task.pair_id] = record

    def _poll_batch_jobs(self, open_batch_jobs, latest_status_by_agent, active_per_agent) -> bool:
        completed_any = False
        finished_job_ids: list[str] = []
        for job_id, bundle in list(open_batch_jobs.items()):
            agent_name = str(bundle["agent"])
            tasks: list[AgentTask] = list(bundle["tasks"])
            job = bundle["job"]
            provider = self.llm_client.get_provider_client(agent_name)
            try:
                refreshed = provider.retrieve_batch(job.batch_id)
            except Exception:  # noqa: BLE001
                time.sleep(0.5)
                continue
            refreshed = BatchJob(
                job_id=job_id,
                agent=agent_name,
                provider=job.provider,
                batch_id=refreshed.batch_id,
                input_file_id=refreshed.input_file_id,
                output_file_id=refreshed.output_file_id,
                error_file_id=refreshed.error_file_id,
                status=refreshed.status,
                item_count=job.item_count,
                item_ids=job.item_ids,
                metadata=dict(refreshed.metadata),
            )
            self.batch_store.write_job_status(refreshed)
            if refreshed.status not in {"completed", "failed", "cancelled", "expired"}:
                time.sleep(0.1)
                continue
            if refreshed.status in {"failed", "cancelled", "expired"}:
                for task in tasks:
                    record = self._exception_records(
                        task,
                        RuntimeError(f"Batch job ended with status: {refreshed.status}"),
                    )
                    self.result_store.append_record(task.agent, record)
                    latest_status_by_agent.setdefault(task.agent, {})[task.pair_id] = record
                finished_job_ids.append(job_id)
                completed_any = True
                continue
            raw_items = provider.fetch_batch_output(refreshed.output_file_id or "")
            self.batch_store.write_response_items(agent_name, job_id, raw_items)
            parsed_items = provider.parse_batch_results(raw_items)
            self.batch_store.write_parsed_results(agent_name, job_id, parsed_items)
            parsed_by_custom_id = {item.custom_id: item for item in parsed_items}
            for task in tasks:
                parsed = parsed_by_custom_id.get(self._custom_id(task))
                if parsed is None:
                    record = self._exception_records(task, ValueError("Missing batch item result"))
                elif parsed.status_code >= 400:
                    record = self._exception_records(task, RuntimeError(parsed.error or {"message": "Batch item failed"}))
                else:
                    try:
                        record = self.build_record_from_batch_result(task, parsed, context=self.executor_context)
                    except Exception as exc:  # noqa: BLE001
                        record = self._exception_records(task, exc)
                self.result_store.append_record(task.agent, record)
                latest_status_by_agent.setdefault(task.agent, {})[task.pair_id] = record
            finished_job_ids.append(job_id)
            completed_any = True
        for job_id in finished_job_ids:
            agent_name = str(open_batch_jobs[job_id]["agent"])
            active_per_agent[agent_name] = max(0, active_per_agent[agent_name] - 1)
            del open_batch_jobs[job_id]
        return completed_any

    def _restore_open_batch_jobs(self, *, latest_status_by_agent, active_per_agent) -> dict[str, dict[str, object]]:
        open_batch_jobs: dict[str, dict[str, object]] = {}
        terminal_statuses = {
            TaskStatus.SUCCEEDED,
            TaskStatus.FAILED_RETRYABLE,
            TaskStatus.FAILED_TERMINAL,
            TaskStatus.SKIPPED,
        }
        for agent_name in self.agent_names:
            role_cfg = self.role_execution.get(agent_name)
            if role_cfg is None or role_cfg.mode != "batch":
                continue
            for submitted_job in self.batch_store.list_submitted_jobs(agent_name):
                job = self.batch_store.load_job_status(agent_name, submitted_job.job_id) or submitted_job
                if job.status in {"failed", "cancelled", "expired"}:
                    continue
                tasks = [self._task_from_custom_id(item_id) for item_id in job.item_ids]
                if not tasks:
                    continue
                latest_records = latest_status_by_agent.setdefault(agent_name, {})
                if all(
                    latest_records.get(task.pair_id) is not None
                    and latest_records[task.pair_id].status in terminal_statuses
                    for task in tasks
                ):
                    continue
                open_batch_jobs[job.job_id] = {
                    "agent": agent_name,
                    "tasks": tasks,
                    "job": job,
                }
                active_per_agent[agent_name] += 1
        return open_batch_jobs

    def _next_ready_task(
        self,
        pair_ids,
        latest_status_by_agent,
        in_flight,
        active_per_agent,
    ) -> AgentTask | None:
        inflight_keys = self._inflight_keys(in_flight)
        for agent_name in self.agent_names:
            if active_per_agent[agent_name] >= self.per_agent_max_workers.get(agent_name, 1):
                continue
            for pair_id in pair_ids:
                if (agent_name, pair_id) in inflight_keys:
                    continue
                if not is_task_ready(agent_name, pair_id, latest_status_by_agent):
                    continue
                if not self._is_task_enabled_by_memory(agent_name, pair_id):
                    continue
                latest_records = latest_status_by_agent.setdefault(agent_name, {})
                latest = latest_records.get(pair_id)
                if latest is None:
                    return AgentTask(run_id=self.run_id, pair_id=pair_id, agent=agent_name, attempt=1)
                if latest.status is TaskStatus.SUCCEEDED:
                    continue
                if latest.status is TaskStatus.FAILED_RETRYABLE and latest.attempt < self.max_attempts.get(agent_name, 1):
                    return AgentTask(
                        run_id=self.run_id,
                        pair_id=pair_id,
                        agent=agent_name,
                        attempt=latest.attempt + 1,
                    )
        return None

    def _exception_records(self, task: AgentTask, exc: Exception) -> AgentRecord:
        terminal = isinstance(exc, (FileNotFoundError, ValueError, KeyError))
        timestamp = datetime.now(timezone.utc).astimezone().isoformat()
        return AgentRecord(
            run_id=task.run_id,
            pair_id=task.pair_id,
            agent=task.agent,
            status=TaskStatus.FAILED_TERMINAL if terminal else TaskStatus.FAILED_RETRYABLE,
            attempt=task.attempt,
            started_at=timestamp,
            finished_at=timestamp,
            input_ref={},
            model="",
            prompt_version=f"{task.agent}-v1",
            result=None,
            error=AgentError(
                type=type(exc).__name__,
                message=str(exc),
                raw={},
            ),
        )

    def _as_record_list(self, record: AgentRecord) -> list[AgentRecord]:
        return [record]

    def _inflight_keys(self, in_flight: dict[Future, AgentTask]) -> set[tuple[str, str]]:
        keys: set[tuple[str, str]] = set()
        for task in in_flight.values():
            keys.add((task.agent, task.pair_id))
        return keys

    def _custom_id(self, task: AgentTask) -> str:
        return f"run:{task.run_id}|agent:{task.agent}|pair:{task.pair_id}|attempt:{task.attempt}"

    def _task_from_custom_id(self, custom_id: str) -> AgentTask:
        parts: dict[str, str] = {}
        for item in custom_id.split("|"):
            if ":" not in item:
                continue
            key, value = item.split(":", 1)
            parts[key] = value
        return AgentTask(
            run_id=str(parts.get("run", self.run_id)),
            pair_id=str(parts.get("pair", "")),
            agent=str(parts.get("agent", "")),
            attempt=int(parts.get("attempt", "1")),
        )

    def _submitted_record(self, task: AgentTask) -> AgentRecord:
        timestamp = datetime.now(timezone.utc).astimezone().isoformat()
        return AgentRecord(
            run_id=task.run_id,
            pair_id=task.pair_id,
            agent=task.agent,
            status=TaskStatus.SUBMITTED,
            attempt=task.attempt,
            started_at=timestamp,
            finished_at=timestamp,
            input_ref={},
            model="",
            prompt_version=f"{task.agent}-v1",
            result={"submitted": True},
            error=None,
        )

    def _is_task_enabled_by_memory(self, agent_name: str, pair_id: str) -> bool:
        memory = self.state_store.read_memory(pair_id)
        if memory is None:
            return agent_name in {"semantic", "logic", "feasibility", "goal"}

        if agent_name in {"semantic", "logic", "feasibility", "goal"}:
            return memory.next_action is NextAction.RUN_PHASE1
        if agent_name == "da":
            return memory.next_action in {NextAction.RUN_DA, NextAction.SKIP_TO_FINALIZE_CONSENSUS}
        if agent_name == "rebuttal":
            return memory.next_action is NextAction.RUN_REBUTTAL
        if agent_name == "arbiter":
            return memory.next_action in {NextAction.RUN_ARBITER, NextAction.SKIP_TO_FINALIZE_CONSENSUS}
        return True

    def _should_force_sync(self, agent_name: str, pair_id: str) -> bool:
        memory = self.state_store.read_memory(pair_id)
        if memory is None:
            return False
        return agent_name == "da" and memory.next_action is NextAction.SKIP_TO_FINALIZE_CONSENSUS
