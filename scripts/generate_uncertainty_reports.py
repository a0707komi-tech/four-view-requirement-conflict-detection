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


def review_unit_id(row: dict[str, Any]) -> str:
    return str(row.get("source_pair_id") or row.get("pair_id"))


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
            uncertain_views = [
                name
                for name in PHASE1_AGENTS
                if phase1_verdict(row, name) == "uncertain"
            ]
            cross_exam = row.get("phase2_cross_exam") or {}
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
                    "uncertain_views": uncertain_views,
                    "abstention_context": (
                        "single_view" if len(uncertain_views) == 1 else "multiple_views"
                    ),
                    "targeted_by_da": cross_exam.get("target") == agent,
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
    unique_review_units = {review_unit_id(row) for row in uncertain_rows}
    vote_patterns = Counter(
        "; ".join(f"{agent}={phase1_verdict(row, agent)}" for agent in PHASE1_AGENTS)
        for row in candidate_rows
    )

    view_stats: dict[str, dict[str, Any]] = {}
    for agent in PHASE1_AGENTS:
        counts = Counter(phase1_verdict(row, agent) for row in candidate_rows)
        evaluated = len(candidate_rows) - counts.get("missing", 0)
        agent_abstentions = [
            row for row in candidate_rows if phase1_verdict(row, agent) == "uncertain"
        ]
        downstream = Counter(str(row.get("verdict") or "missing") for row in agent_abstentions)
        single_view = sum(
            sum(phase1_verdict(row, name) == "uncertain" for name in PHASE1_AGENTS) == 1
            for row in agent_abstentions
        )
        targeted_by_da = sum(
            (row.get("phase2_cross_exam") or {}).get("target") == agent
            for row in agent_abstentions
        )
        view_stats[agent] = {
            "evaluated_pairs": evaluated,
            "compatible": counts.get("compatible", 0),
            "incompatible": counts.get("incompatible", 0),
            "uncertain": counts.get("uncertain", 0),
            "missing": counts.get("missing", 0),
            "abstention_rate": round(percentage(counts.get("uncertain", 0), evaluated), 4),
            "single_view_abstention": single_view,
            "multiple_view_abstention": len(agent_abstentions) - single_view,
            "targeted_by_da": targeted_by_da,
            "final_compatible": downstream.get("compatible", 0),
            "final_incompatible": downstream.get("incompatible", 0),
            "final_uncertain": downstream.get("uncertain", 0),
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
            "recommended_review_rows": len(uncertain_rows),
            "recommended_unique_review_units": len(unique_review_units),
            "recommended_review_policy": "Every final uncertain verdict is an abstention and enters the review queue; canonical aliases share the source pair's review unit.",
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
            f"| Recommended review queue | {uncertainty['recommended_review_rows']} rows / {uncertainty['recommended_unique_review_units']} unique units | all final uncertain rows |",
            "",
            "Uncertainty is reported exactly as stored. The legacy `needs_human_review` value is retained for provenance, but the reporting policy sends every final uncertain verdict to review. Canonical aliases share their source pair's review unit.",
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
            "| View | Evaluated | Uncertain | Rate | Single-view | Multi-view | DA target | Final C | Final I | Final U |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for agent in PHASE1_AGENTS:
        stats = report["phase1_view_abstention"][agent]
        lines.append(
            f"| {agent} | {stats['evaluated_pairs']} | {stats['uncertain']} | {stats['abstention_rate']:.2%} | {stats['single_view_abstention']} | {stats['multiple_view_abstention']} | {stats['targeted_by_da']} | {stats['final_compatible']} | {stats['final_incompatible']} | {stats['final_uncertain']} |"
        )
    lines.extend(
        [
            "",
            "`Single-view` means that this was the only Phase-1 view to abstain; `multi-view` means at least one other view also abstained. `Final C/I/U` reports the final compatible, incompatible, or uncertain outcome after disagreement handling for the pairs on which that view abstained.",
        ]
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
            "recommended_unique_review_units": uncertainty["recommended_unique_review_units"],
            "phase1_any_abstention": report["phase1_pairs_with_any_abstention"],
            "phase1_any_abstention_rate": report["phase1_any_abstention_rate"],
        }
        for agent in PHASE1_AGENTS:
            stats = report["phase1_view_abstention"][agent]
            for key in (
                "uncertain",
                "abstention_rate",
                "single_view_abstention",
                "multiple_view_abstention",
                "targeted_by_da",
                "final_compatible",
                "final_incompatible",
                "final_uncertain",
            ):
                row[f"{agent}_{key}"] = stats[key]
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
            "single_view_abstention",
            "multiple_view_abstention",
            "targeted_by_da",
            "final_compatible",
            "final_incompatible",
            "final_uncertain",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for report in reports:
            for agent in PHASE1_AGENTS:
                stats = report["phase1_view_abstention"][agent]
                writer.writerow({"dataset": report["dataset"], "agent": agent, **stats})

    with (summary_dir / "uncertainty_reason_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["dataset", "stored_uncertainty_source", "count"],
        )
        writer.writeheader()
        for report in reports:
            for source, count in report["uncertainty"]["raw_sources"].items():
                writer.writerow(
                    {
                        "dataset": report["dataset"],
                        "stored_uncertainty_source": source,
                        "count": count,
                    }
                )

    with (summary_dir / "phase1_abstention_reasons.csv").open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "dataset",
            "pair_id",
            "agent",
            "model",
            "confidence",
            "abstention_context",
            "uncertain_views",
            "targeted_by_da",
            "reasoning",
            "key_evidence",
            "final_verdict",
            "final_confidence",
            "final_uncertainty_source",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for report in reports:
            path = root / "results" / "final" / report["slug"] / "phase1_abstentions.jsonl"
            for record in load_jsonl(path):
                writer.writerow(
                    {
                        key: json.dumps(record.get(key), ensure_ascii=False)
                        if key in {"uncertain_views", "key_evidence"}
                        else record.get(key)
                        for key in fieldnames
                    }
                )

    lines = [
        "# Uncertainty and Abstention Summary",
        "",
        "This summary is generated offline from the published final verdicts and effective agent records. No model API is called.",
        "",
        "Final uncertainty uses all final verdict rows. Phase-1 view abstention rates use canonical candidate rows only, because canonical aliases inherit a result and do not represent a new view decision.",
        "",
        "## Final Uncertainty",
        "",
        "| Dataset | Final pairs | Compatible | Incompatible | Uncertain | Duplicate route (subset) | Uncertainty rate | Unique review units | Legacy review flag true |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['dataset']} | {row['final_pairs']} | {row['compatible']} | {row['incompatible']} | {row['uncertain']} | {row['duplicate_route']} | {row['uncertainty_rate']:.2%} | {row['recommended_unique_review_units']} | {row['human_review_true_among_uncertain']} |"
        )
    lines.extend(
        [
            "",
            "## Phase-1 View Abstention",
            "",
            "| Dataset | View | Uncertain | Rate | Single-view | Multi-view | DA target | Final C | Final I | Final U |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        for agent in PHASE1_AGENTS:
            lines.append(
                f"| {row['dataset']} | {agent} | {row[f'{agent}_uncertain']} | {row[f'{agent}_abstention_rate']:.2%} | {row[f'{agent}_single_view_abstention']} | {row[f'{agent}_multiple_view_abstention']} | {row[f'{agent}_targeted_by_da']} | {row[f'{agent}_final_compatible']} | {row[f'{agent}_final_incompatible']} | {row[f'{agent}_final_uncertain']} |"
            )
    lines.extend(
        [
            "",
            "The per-dataset reports contain vote patterns, route/stage breakdowns, raw stored uncertainty sources, representative arbiter reasoning, and complete JSONL evidence files.",
            "",
        ]
    )
    (summary_dir / "uncertainty_summary.md").write_text("\n".join(lines), encoding="utf-8")


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    return "".join(replacements.get(character, character) for character in value)


def aggregate_view_stats(reports: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    keys = (
        "evaluated_pairs",
        "uncertain",
        "single_view_abstention",
        "multiple_view_abstention",
        "targeted_by_da",
        "final_compatible",
        "final_incompatible",
        "final_uncertain",
    )
    output: dict[str, dict[str, int]] = {}
    for agent in PHASE1_AGENTS:
        output[agent] = {
            key: sum(int(report["phase1_view_abstention"][agent][key]) for report in reports)
            for key in keys
        }
    return output


def write_paper_artifacts(root: Path, reports: list[dict[str, Any]]) -> None:
    docs_dir = root / "docs"
    total_final = sum(int(report["scope"]["final_pairs"]) for report in reports)
    total_uncertain = sum(int(report["uncertainty"]["count"]) for report in reports)
    total_review_units = sum(
        int(report["uncertainty"]["recommended_unique_review_units"])
        for report in reports
    )
    total_candidates = sum(
        int(report["scope"]["canonical_candidate_pairs"])
        for report in reports
    )
    total_any_abstention = sum(
        int(report["phase1_pairs_with_any_abstention"])
        for report in reports
    )
    aggregate_views = aggregate_view_stats(reports)

    latex_lines = [
        "% Requires \\usepackage{booktabs}.",
        "\\begin{table*}[t]",
        "\\centering",
        "\\caption{Final uncertainty outcomes and review workload. Uncertainty rate is computed over stored final verdict rows; review units collapse canonical aliases to their source pair.}",
        "\\label{tab:uncertainty-final}",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        "Dataset & Final rows & Uncertain & Rate (\\%) & Review units \\\\",
        "\\midrule",
    ]
    for report in reports:
        uncertainty = report["uncertainty"]
        latex_lines.append(
            f"{latex_escape(report['dataset'])} & {report['scope']['final_pairs']} & "
            f"{uncertainty['count']} & {100 * uncertainty['rate']:.2f} & "
            f"{uncertainty['recommended_unique_review_units']} \\\\"
        )
    latex_lines.extend(
        [
            "\\midrule",
            f"Overall & {total_final} & {total_uncertain} & {100 * percentage(total_uncertain, total_final):.2f} & {total_review_units} \\\\ ".rstrip(),
            "\\bottomrule",
            "\\end{tabular}",
            "\\end{table*}",
            "",
            "\\begin{table*}[t]",
            "\\centering",
            "\\caption{Phase-1 view abstention and downstream resolution across canonical candidates. C, I, and U denote final compatible, incompatible, and uncertain outcomes.}",
            "\\label{tab:uncertainty-views}",
            "\\begin{tabular}{lrrrrrrrrr}",
            "\\toprule",
            "View & Evaluated & Abstained & Rate (\\%) & Single & Multi & DA target & Final C & Final I & Final U \\\\",
            "\\midrule",
        ]
    )
    for agent in PHASE1_AGENTS:
        stats = aggregate_views[agent]
        latex_lines.append(
            f"{agent.capitalize()} & {stats['evaluated_pairs']} & {stats['uncertain']} & "
            f"{100 * percentage(stats['uncertain'], stats['evaluated_pairs']):.2f} & "
            f"{stats['single_view_abstention']} & {stats['multiple_view_abstention']} & "
            f"{stats['targeted_by_da']} & {stats['final_compatible']} & "
            f"{stats['final_incompatible']} & {stats['final_uncertain']} \\\\"
        )
    latex_lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            "\\end{table*}",
            "",
        ]
    )
    (docs_dir / "paper-uncertainty-tables.tex").write_text(
        "\n".join(latex_lines), encoding="utf-8"
    )

    view_sentences = []
    for agent in PHASE1_AGENTS:
        stats = aggregate_views[agent]
        view_sentences.append(
            f"{agent} {stats['uncertain']}/{stats['evaluated_pairs']} "
            f"({percentage(stats['uncertain'], stats['evaluated_pairs']):.2%})"
        )
    dataset_sentences = [
        f"{report['dataset']} {report['uncertainty']['count']}/{report['scope']['final_pairs']} ({report['uncertainty']['rate']:.2%})"
        for report in reports
    ]
    paper_text = [
        "# Paper-Ready Uncertainty Reporting",
        "",
        "## Reporting Definition",
        "",
        "A Phase-1 view abstains when it emits `uncertain` for a canonical candidate pair. A final abstention occurs when the disagreement handler and arbiter still return `uncertain`. Every final abstention is assigned to human review. Canonical aliases inherit the source pair's decision, so review workload is counted using unique source-pair units rather than duplicated alias rows.",
        "",
        "## Results Paragraph",
        "",
        f"Across {total_final:,} stored final verdict rows, the framework abstained on {total_uncertain:,} ({percentage(total_uncertain, total_final):.2%}). Collapsing inherited canonical aliases produced {total_review_units:,} unique human-review units. Dataset-level uncertainty was "
        + "; ".join(dataset_sentences)
        + ".",
        "",
        f"Phase-1 analysis covered {total_candidates:,} canonical candidates. At least one view abstained on {total_any_abstention:,} pairs ({percentage(total_any_abstention, total_candidates):.2%}). The view-level abstention frequencies were "
        + "; ".join(view_sentences)
        + ". Because more than one view may abstain on the same pair, view-level counts are not additive. The artifact reports whether each abstention occurred alone or with other abstentions, whether DA selected that view for challenge, and whether the final decision became compatible, incompatible, or remained uncertain.",
        "",
        "ETCS-GOLD used normalized final uncertainty labels: 55 unverifiable assumptions, 22 missing-domain-knowledge cases, 18 ambiguous requirements, and 2 verifiable assumptions. OpenAPI Specification 3.0 recorded four unverifiable-assumption cases. The older result schemas for promise-project2, Broker-All, and Library-Gold stored the uncertainty source as verbatim text rather than a controlled label. We therefore publish those reasons without post-hoc relabeling in `results/summary/uncertainty_reason_summary.csv` and the per-dataset JSONL evidence files.",
        "",
        "## Interpretation",
        "",
        "The uncertainty mechanism is an abstention mechanism, not a conflict-positive prediction. It prevents unresolved pairs from being forced into compatible or incompatible classes and exposes them as review cases. The primary quantitative result is therefore the final uncertainty rate; the unique review-unit count estimates manual workload after removing inherited aliases.",
        "",
    ]
    (docs_dir / "paper-uncertainty-reporting.md").write_text(
        "\n".join(paper_text), encoding="utf-8"
    )

    response_lines = [
        "# Reviewer Response: Uncertainty and Abstention Reporting",
        "",
        "**Reviewer comment.** The paper defines uncertainty as an abstention outcome but does not report when or why views abstain, limiting the practical usefulness of the uncertainty mechanism for identifying cases requiring human review. The paper also claims that uncertainty rates are reported separately, but they are absent from the results.",
        "",
        "**Response.** We agree that the original results did not substantiate this claim. We revised the evaluation to report uncertainty at two levels. First, a view-level abstention is recorded whenever a Phase-1 view returns `uncertain` for a canonical candidate. Second, a final abstention is recorded when disagreement handling and arbitration still produce `uncertain`. We now report the denominator, count, and rate for both levels; the Phase-1 vote pattern; whether DA challenged the abstaining view; the final outcome after adjudication; and the stored reason and evidence for every abstention.",
        "",
        f"Across {total_final:,} final verdict rows, {total_uncertain:,} were uncertain ({percentage(total_uncertain, total_final):.2%}). Because canonical aliases inherit their source pair's result, these rows correspond to {total_review_units:,} unique review units. Across {total_candidates:,} canonical candidates, at least one Phase-1 view abstained on {total_any_abstention:,} pairs ({percentage(total_any_abstention, total_candidates):.2%}). The revised tables provide dataset-specific rates and view-specific abstention behavior.",
        "",
        "We also made the operational policy explicit: every final `uncertain` verdict enters the human-review queue. Alias rows are collapsed to the canonical source pair so that the reported review workload is not inflated. We retained the legacy `needs_human_review` field only as provenance because older runs did not populate it consistently; it is no longer used to define the review queue in the report.",
        "",
        "The replication package now includes the aggregate tables, per-dataset reports, exact uncertainty-source strings, Phase-1 reasoning records, and an offline generation script. This revision corrects the unsupported statement that uncertainty was already reported separately.",
        "",
    ]
    (docs_dir / "reviewer-response-uncertainty.md").write_text(
        "\n".join(response_lines), encoding="utf-8"
    )


def generate_reports(root: Path = ROOT) -> list[dict[str, Any]]:
    reports = [
        build_dataset_report(root, dataset, slug)
        for dataset, slug in DATASETS.items()
    ]
    write_summary(root, reports)
    write_paper_artifacts(root, reports)
    return reports


def main() -> int:
    reports = generate_reports()
    print(json.dumps({"datasets": [report["dataset"] for report in reports]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
