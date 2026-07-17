import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ("semantic", "logic", "feasibility", "goal", "da", "rebuttal", "arbiter")
EXPECTED_COUNTS = {
    "ETCS-GOLD": 778,
    "OpenAPI-Specification-3.0": 595,
    "promise-project2": 913,
    "Broker-All": 654,
    "Library-Gold": 2875,
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_all_agent_exports_are_complete_unique_and_successful() -> None:
    for agent in AGENTS:
        for dataset, expected_count in EXPECTED_COUNTS.items():
            path = ROOT / "results" / "agents" / agent / f"{dataset}.jsonl"
            rows = load_jsonl(path)
            pair_ids = [str(row["pair_id"]) for row in rows]

            assert len(rows) == expected_count
            assert len(pair_ids) == len(set(pair_ids))
            assert all(row.get("status") == "succeeded" for row in rows)


def test_final_verdict_partitions_reconcile() -> None:
    for dataset in EXPECTED_COUNTS:
        result_dir = ROOT / "results" / "final" / dataset
        all_rows = load_jsonl(result_dir / "verdicts.jsonl")
        partitioned = sum(
            len(load_jsonl(result_dir / f"{verdict}.jsonl"))
            for verdict in ("compatible", "incompatible", "uncertain")
        )

        assert partitioned == len(all_rows)
