from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PHASE1_AGENTS = ("semantic", "logic", "feasibility", "goal")
DATASETS = {
    "ETCS-GOLD": "ETCS-GOLD",
    "OpenAPI Specification 3.0": "OpenAPI-Specification-3.0",
    "promise-project2": "promise-project2",
    "Broker-All": "Broker-All",
    "Library-Gold": "Library-Gold",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def route_type(row: dict[str, Any]) -> str:
    stage = str(row.get("resolution_stage") or "").strip()
    if stage:
        return stage
    if row.get("source_pair_id"):
        return "canonical_alias"
    return "unknown"


def phase1_verdict(row: dict[str, Any], agent: str) -> str:
    votes = row.get("phase1_votes") or {}
    vote = votes.get(agent) or {}
    return str(vote.get("verdict") or "missing")


def latest_successful_agent_records(
    root: Path, agent: str, slug: str
) -> dict[str, dict[str, Any]]:
    path = root / "results" / "agents" / agent / f"{slug}.jsonl"
    if not path.is_file():
        return {}
    latest: dict[str, dict[str, Any]] = {}
    for row in load_jsonl(path):
        if row.get("status") == "succeeded":
            latest[str(row.get("pair_id"))] = row
    return latest


def agent_decision(record: dict[str, Any] | None) -> dict[str, Any]:
    if not record:
        return {}
    result = record.get("result") or {}
    return result.get("agent_decision") or {}


def clean_text(value: Any, limit: int = 420) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def md_cell(value: Any, limit: int = 420) -> str:
    return clean_text(value, limit).replace("|", "\\|") or "-"


def percentage(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def phase1_abstention_records(
    dataset: str,
    candidate_rows: list[dict[str, Any]],
    agent_records: dict[str, dict[str, dict[str, Any]]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in candidate_rows:
        pair_id = str(row.get("pair_id"))
        for agent in PHASE1_AGENTS:
            if phase1_verdict(row, agent) != "uncertain":
                continue
            decision = agent_decision(agent_records.get(agent, {}).get(pair_id))
            vote = (row.get("phase1_votes") or {}).get(agent) or {}
            records.append(
                {
                    "dataset": dataset,
                    "pair_id": pair_id,
                    "agent": agent,
                    "verdict": "uncertain",
                    "confidence": decision.get("confidence", vote.get("confidence")),
                    "model": decision.get("model", vote.get("model")),
                    "reasoning": decision.get("reasoning", ""),
                    "key_evidence": decision.get("key_evidence", []),
                    "final_verdict": row.get("verdict"),
                    "final_confidence": row.get("confidence"),
                    "final_uncertainty_source": row.get("uncertainty_source"),
                    "final_resolution_stage": row.get("resolution_stage"),
                }
            )
    return records


def build_dataset_report(root: Path, dataset: str, slug: str) -> dict[str, Any]:
    result_dir = root / "results" / "final" / slug
    final_rows = load_jsonl(result_dir / "verdicts.jsonl")
    candidate_rows = [row for row in final_rows if route_type(row) == "canonical_candidate"]
    uncertain_rows = [row for row in final_rows if row.get("verdict") == "uncertain"]
    agent_records = {
        agent: latest_successful_agent_records(root, agent, slug)
        for agent in PHASE1_AGENTS
    }
    abstention_rows = phase1_abstention_records(
        dataset, candidate_rows, agent_records
    )

    route_counts = Counter(route_type(row) for row in final_rows)
    final_verdict_counts = Counter(str(row.get("verdict") or "missing") for row in final_rows)
    uncertainty_by_route = Counter(route_type(row) for row in uncertain_rows)
    uncertainty_by_stage = Counter(str(row.get("resolution_stage") or "missing") for row in uncertain_rows)
    uncertainty_sources = Counter(
        str(row.get("uncertainty_source") or "none recorded") for row in uncertain_rows
    )
    vote_patterns = Counter(
        "; ".join(f"{agent}={phase1_verdict(row, agent)}" for agent in PHASE1_AGENTS)
        for row in candidate_rows
    )

    view_stats: dict[str, dict[str, Any]] = {}
    for agent in PHASE1_AGENTS:
        counts = Counter(phase1_verdict(row, agent) for row in candidate_rows)
        evaluated = len(candidate_rows) - counts.get("missing", 0)
        view_stats[agent] = {
            "evaluated_pairs": evaluated,
            "compatible": counts.get("compatible", 0),
            "incompatible": counts.get("incompatible", 0),
            "uncertain": counts.get("uncertain", 0),
            "missing": counts.get("missing", 0),
            "abstention_rate": round(percentage(counts.get("uncertain", 0), evaluated), 4),
        }

    any_view_abstention = sum(
        any(phase1_verdict(row, agent) == "uncertain" for agent in PHASE1_AGENTS)
        for row in candidate_rows
    )
    review_true = sum(bool(row.get("needs_human_review")) for row in uncertain_rows)
    report = {
        "dataset": dataset,
        "slug": slug,
        "scope": {
            "final_pairs": len(final_rows),
            "canonical_candidate_pairs": len(candidate_rows),
            "duplicate_route_pairs": route_counts.get("duplicate_group_rule", 0),
            "phase1_denominator": "canonical_candidate pairs with stored Phase-1 votes",
            "final_uncertainty_denominator": "all final verdict rows",
        },
        "final_outcomes": dict(final_verdict_counts),
        "route_counts": dict(route_counts),
        "uncertainty": {
            "count": len(uncertain_rows),
            "rate": round(percentage(len(uncertain_rows), len(final_rows)), 4),
            "by_route": dict(uncertainty_by_route),
            "by_resolution_stage": dict(uncertainty_by_stage),
            "raw_sources": dict(uncertainty_sources),
            "explicit_human_review_count": review_true,
            "explicit_human_review_rate_among_uncertain": round(
                percentage(review_true, len(uncertain_rows)), 4
            ),
            "uncertain_without_review_flag": len(uncertain_rows) - review_true,
        },
        "phase1_view_abstention": view_stats,
        "phase1_pairs_with_any_abstention": any_view_abstention,
        "phase1_any_abstention_rate": round(
            percentage(any_view_abstention, len(candidate_rows)), 4
        ),
        "phase1_vote_patterns": [
            {"pattern": pattern, "count": count}
            for pattern, count in vote_patterns.most_common()
        ],
        "representative_uncertain_cases": [
            {
                "pair_id": row.get("pair_id"),
                "route_type": route_type(row),
                "confidence": row.get("confidence"),
                "needs_human_review": bool(row.get("needs_human_review")),
                "uncertainty_source": row.get("uncertainty_source"),
                "phase1_votes": row.get("phase1_votes"),
                "phase2_cross_exam": row.get("phase2_cross_exam"),
                "arbiter_reasoning": row.get("arbiter_reasoning"),
            }
            for row in uncertain_rows[:10]
        ],
    }

    write_json(result_dir / "uncertainty_report.json", report)
    (result_dir / "uncertainty_reasons.jsonl").write_text(
        "".join(json.dumps({
            "dataset": dataset,
            "pair_id": row.get("pair_id"),
            "route_type": route_type(row),
            "resolution_stage": row.get("resolution_stage"),
            "source_pair_id": row.get("source_pair_id"),
            "verdict": row.get("verdict"),
            "confidence": row.get("confidence"),
            "needs_human_review": bool(row.get("needs_human_review")),
            "uncertainty_source": row.get("uncertainty_source"),
            "phase1_votes": row.get("phase1_votes"),
            "phase2_cross_exam": row.get("phase2_cross_exam"),
            "arbiter_reasoning": row.get("arbiter_reasoning"),
        }, ensure_ascii=False) + "\n" for row in uncertain_rows),
        encoding="utf-8",
    )
    (result_dir / "phase1_abstentions.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in abstention_rows),
        encoding="utf-8",
    )
    write_dataset_markdown(result_dir / "uncertainty_report.md", report, abstention_rows)
    return report


def write_dataset_markdown(
    path: Path, report: dict[str, Any], abstention_rows: list[dict[str, Any]]
) -> None:
    final_outcomes = report["final_outcomes"]
    uncertainty = report["uncertainty"]
    lines = [
        f"# Uncertainty and Abstention Report: {report['dataset']}",
        "",
        "This report is generated offline from the stored final verdicts and agent records. It does not call any model API.",
        "",
        "## Scope and Denominators",
        "",
        f"- Final verdict rows: **{report['scope']['final_pairs']}**.",
        f"- Canonical candidate rows with Phase-1 execution: **{report['scope']['canonical_candidate_pairs']}**.",
        "- Final uncertainty rate uses all final verdict rows, including canonical aliases and duplicate routes.",
        "- Duplicate-group rows are shown as a separate route because the historical final artifact stores them as `incompatible` with `duplicate_conflict=true`; conflict metrics exclude them.",
        "- View-level abstention rates use canonical candidate rows only; aliases inherit a result and are not counted as new view decisions.",
        "",
        "## Final Outcomes",
        "",
        "| Outcome | Count | Rate |",
        "| --- | ---: | ---: |",
    ]
    total = report["scope"]["final_pairs"]
    for outcome in ("compatible", "incompatible", "uncertain"):
        count = int(final_outcomes.get(outcome, 0))
        lines.append(f"| `{outcome}` | {count} | {percentage(count, total):.2%} |")
    duplicate_routes = report["scope"]["duplicate_route_pairs"]
    lines.append(f"| `duplicate_group_rule` route (subset of incompatible) | {duplicate_routes} | subset |")
    lines.extend(
        [
            "",
            "## Uncertainty and Human Review",
            "",
            "| Measure | Count | Rate |",
            "| --- | ---: | ---: |",
            f"| Final `uncertain` | {uncertainty['count']} | {uncertainty['rate']:.2%} of final rows |",
            f"| `needs_human_review=true` among uncertain rows | {uncertainty['explicit_human_review_count']} | {uncertainty['explicit_human_review_rate_among_uncertain']:.2%} of uncertain rows |",
            f"| Uncertain rows without review flag | {uncertainty['uncertain_without_review_flag']} | - |",
            "",
            "Uncertainty is reported exactly as stored. The report does not infer a human-review flag from the verdict; the finalizer's stored `needs_human_review` value is shown separately.",
            "",
            "## Final Uncertainty by Route and Stage",
            "",
            "| Dimension | Count |",
            "| --- | ---: |",
        ]
    )
    for key, count in uncertainty["by_route"].items():
        lines.append(f"| Route `{md_cell(key)}` | {count} |")
    for key, count in uncertainty["by_resolution_stage"].items():
        lines.append(f"| Stage `{md_cell(key)}` | {count} |")

    lines.extend(
        [
            "",
            "## Phase-1 View Abstention",
            "",
            "| View | Evaluated pairs | Compatible | Incompatible | Uncertain | Missing | Abstention rate |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for agent in PHASE1_AGENTS:
        stats = report["phase1_view_abstention"][agent]
        lines.append(
            f"| {agent} | {stats['evaluated_pairs']} | {stats['compatible']} | {stats['incompatible']} | {stats['uncertain']} | {stats['missing']} | {stats['abstention_rate']:.2%} |"
        )
    lines.extend(
        [
            "",
            f"Canonical candidate pairs with at least one Phase-1 abstention: **{report['phase1_pairs_with_any_abstention']}** ({report['phase1_any_abstention_rate']:.2%}).",
            "",
            "## Phase-1 Vote Patterns",
            "",
            "| Vote pattern | Count |",
            "| --- | ---: |",
        ]
    )
    for item in report["phase1_vote_patterns"]:
        lines.append(f"| `{md_cell(item['pattern'])}` | {item['count']} |")

    lines.extend(["", "## Stored Uncertainty Sources", "", "| Source | Count |", "| --- | ---: |"])
    for source, count in uncertainty["raw_sources"].items():
        lines.append(f"| {md_cell(source)} | {count} |")

    lines.extend(["", "## Representative Final Uncertain Cases", ""])
    for case in report["representative_uncertain_cases"]:
        lines.extend(
            [
                f"### {case['pair_id']}",
                "",
                f"- Route: `{case['route_type']}`; confidence: `{case['confidence']}`; human review flag: `{case['needs_human_review']}`.",
                f"- Stored uncertainty source: {md_cell(case['uncertainty_source'])}.",
                f"- Phase-1 votes: `{md_cell(json.dumps(case['phase1_votes'], ensure_ascii=False), 900)}`.",
                f"- Cross-examination: {md_cell(json.dumps(case['phase2_cross_exam'], ensure_ascii=False), 900)}.",
                f"- Arbiter reasoning: {md_cell(case['arbiter_reasoning'], 900)}.",
                "",
            ]
        )
    if not report["representative_uncertain_cases"]:
        lines.append("No final uncertain cases were recorded.")

    lines.extend(["", "## Phase-1 Abstention Evidence", ""])
    if not abstention_rows:
        lines.append("No Phase-1 view abstentions were recorded for canonical candidates.")
    else:
        for row in abstention_rows[:20]:
            lines.extend(
                [
                    f"- `{row['agent']}` on `{row['pair_id']}`: {md_cell(row['reasoning'], 700)}",
                    f"  Evidence: {md_cell(json.dumps(row['key_evidence'], ensure_ascii=False), 700)}",
                ]
            )
        if len(abstention_rows) > 20:
            lines.append(f"- Additional abstention records: see `phase1_abstentions.jsonl` ({len(abstention_rows)} total).")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_summary(root: Path, reports: list[dict[str, Any]]) -> None:
    summary_dir = root / "results" / "summary"
    rows: list[dict[str, Any]] = []
    for report in reports:
        uncertainty = report["uncertainty"]
        row: dict[str, Any] = {
            "dataset": report["dataset"],
            "final_pairs": report["scope"]["final_pairs"],
            "canonical_candidate_pairs": report["scope"]["canonical_candidate_pairs"],
            "compatible": report["final_outcomes"].get("compatible", 0),
            "incompatible": report["final_outcomes"].get("incompatible", 0),
            "uncertain": report["final_outcomes"].get("uncertain", 0),
            "duplicate_route": report["scope"]["duplicate_route_pairs"],
            "uncertainty_rate": uncertainty["rate"],
            "human_review_true_among_uncertain": uncertainty["explicit_human_review_count"],
            "human_review_rate_among_uncertain": uncertainty["explicit_human_review_rate_among_uncertain"],
            "uncertain_without_review_flag": uncertainty["uncertain_without_review_flag"],
            "phase1_any_abstention": report["phase1_pairs_with_any_abstention"],
            "phase1_any_abstention_rate": report["phase1_any_abstention_rate"],
        }
        for agent in PHASE1_AGENTS:
            stats = report["phase1_view_abstention"][agent]
            row[f"{agent}_uncertain"] = stats["uncertain"]
            row[f"{agent}_abstention_rate"] = stats["abstention_rate"]
        rows.append(row)

    write_json(summary_dir / "uncertainty_summary.json", {"datasets": reports})
    if rows:
        with (summary_dir / "uncertainty_summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    with (summary_dir / "phase1_abstention_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "dataset",
            "agent",
            "evaluated_pairs",
            "compatible",
            "incompatible",
            "uncertain",
            "missing",
            "abstention_rate",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for report in reports:
            for agent in PHASE1_AGENTS:
                stats = report["phase1_view_abstention"][agent]
                writer.writerow({"dataset": report["dataset"], "agent": agent, **stats})

    lines = [
        "# Uncertainty and Abstention Summary",
        "",
        "This summary is generated offline from the published final verdicts and effective agent records. No model API is called.",
        "",
        "Final uncertainty uses all final verdict rows. Phase-1 view abstention rates use canonical candidate rows only, because canonical aliases inherit a result and do not represent a new view decision.",
        "",
        "## Final Uncertainty",
        "",
        "| Dataset | Final pairs | Compatible | Incompatible | Uncertain | Duplicate route (subset) | Uncertainty rate | Review flag true | Uncertain without flag |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['dataset']} | {row['final_pairs']} | {row['compatible']} | {row['incompatible']} | {row['uncertain']} | {row['duplicate_route']} | {row['uncertainty_rate']:.2%} | {row['human_review_true_among_uncertain']} | {row['uncertain_without_review_flag']} |"
        )
    lines.extend(
        [
            "",
            "## Phase-1 View Abstention",
            "",
            "| Dataset | View | Uncertain | Abstention rate |",
            "| --- | --- | ---: | ---: |",
        ]
    )
    for row in rows:
        for agent in PHASE1_AGENTS:
            lines.append(
                f"| {row['dataset']} | {agent} | {row[f'{agent}_uncertain']} | {row[f'{agent}_abstention_rate']:.2%} |"
            )
    lines.extend(
        [
            "",
            "The per-dataset reports contain vote patterns, route/stage breakdowns, raw stored uncertainty sources, representative arbiter reasoning, and complete JSONL evidence files.",
            "",
        ]
    )
    (summary_dir / "uncertainty_summary.md").write_text("\n".join(lines), encoding="utf-8")


def generate_reports(root: Path = ROOT) -> list[dict[str, Any]]:
    reports = [
        build_dataset_report(root, dataset, slug)
        for dataset, slug in DATASETS.items()
    ]
    write_summary(root, reports)
    return reports


def main() -> int:
    reports = generate_reports()
    print(json.dumps({"datasets": [report["dataset"] for report in reports]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
