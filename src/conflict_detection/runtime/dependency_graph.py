from __future__ import annotations

from conflict_detection.runtime.contracts import AgentRecord, TaskStatus


DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "semantic": (),
    "logic": (),
    "feasibility": (),
    "goal": (),
    "da": ("semantic", "logic", "feasibility", "goal"),
    "rebuttal": ("da",),
    "arbiter": ("semantic", "logic", "feasibility", "goal", "da", "rebuttal"),
}


def get_dependencies(agent_name: str) -> tuple[str, ...]:
    return DEPENDENCIES.get(agent_name, ())


def is_task_ready(
    agent_name: str,
    pair_id: str,
    latest_status_by_agent: dict[str, dict[str, AgentRecord]],
) -> bool:
    for dependency in get_dependencies(agent_name):
        dependency_records = latest_status_by_agent.get(dependency, {})
        record = dependency_records.get(pair_id)
        if record is None or record.status is not TaskStatus.SUCCEEDED:
            return False
    return True
