from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from itertools import combinations
from pathlib import Path
from typing import Any

try:
    from generate_uncertainty_reports import generate_reports
except ModuleNotFoundError:  # Supports both direct execution and module execution.
    from scripts.generate_uncertainty_reports import generate_reports


ROOT = Path(__file__).resolve().parents[1]

DATASETS = {
    "ETCS-GOLD": {
        "slug": "ETCS-GOLD",
        "requirements": "ETCS-GOLD.csv",
        "labels": "ETCS-GOLD.csv",
        "blank_class_is_conflict": False,
    },
    "OpenAPI Specification 3.0": {
        "slug": "OpenAPI-Specification-3.0",
        "requirements": "OpenAPI-Specification-3.0.csv",
        "labels": "OpenAPI-Specification-3.0.csv",
        "blank_class_is_conflict": False,
    },
    "promise-project2": {
        "slug": "promise-project2",
        "requirements": "promise-project2.csv",
        "labels": "promise-project2.csv",
        "blank_class_is_conflict": False,
    },
    "Broker-All": {
        "slug": "Broker-All",
        "requirements": "Broker-All.csv",
        "labels": "Broker-All.csv",
        "blank_class_is_conflict": False,
    },
    "Library-Gold": {
        "slug": "Library-Gold",
        "requirements": "Library-Gold.csv",
        "labels": "Library-Gold.csv",
        "blank_class_is_conflict": True,
    },
}


@dataclass(frozen=True)
class ConflictMetrics:
    total_pairs: int
    gold_positive: int
    predicted_positive: int
    tp: int
    fp: int
    fn: int
    tn: int
    precision: float
    recall: float
    f1: float
    accuracy: float
    tp_pairs: tuple[str, ...]
    fp_pairs: tuple[str, ...]
    fn_pairs: tuple[str, ...]


def read_text_flexible(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def id_sort_key(value: str) -> tuple[int, str]:
    value = str(value).strip()
    try:
        return int(value), value
    except ValueError:
        return 10**12, value


def normalize_pair(left: str, right: str) -> str:
    first, second = sorted((str(left).strip(), str(right).strip()), key=id_sort_key)
    return f"{first}_{second}"


def pair_sort_key(pair_id: str) -> tuple[tuple[int, str], tuple[int, str]]:
    left, right = pair_id.split("_", 1)
    return id_sort_key(left), id_sort_key(right)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in read_text_flexible(path).splitlines() if line.strip()]


def load_requirements(path: Path) -> dict[str, str]:
    rows = list(csv.DictReader(read_text_flexible(path).splitlines()))
    requirements: dict[str, str] = {}
    for row in rows:
        requirement_id = str(row.get("ID", row.get("id", ""))).strip()
        text = str(row.get("Requirement", row.get("requirement text", ""))).strip()
        if not requirement_id or not text:
            raise ValueError(f"Invalid requirement row in {path}: {row}")
        requirements[requirement_id] = text
    return requirements


def load_gold(path: Path, *, blank_class_is_conflict: bool) -> tuple[set[str], dict[str, str]]:
    conflicts: set[str] = set()
    classes: dict[str, str] = {}
    for row in csv.DictReader(read_text_flexible(path).splitlines()):
        pair_id = normalize_pair(row["R1"], row["R2"])
        label = str(row.get("class", "")).strip()
        classes[pair_id] = label
        if label.lower() == "duplicate":
            continue
        if label or blank_class_is_conflict:
            conflicts.add(pair_id)
    return conflicts, classes


def score_conflicts(
    gold_positive: set[str],
    predicted_positive: set[str],
    all_pair_ids: set[str],
) -> ConflictMetrics:
    tp_pairs = gold_positive & predicted_positive
    fp_pairs = predicted_positive - gold_positive
    fn_pairs = gold_positive - predicted_positive
    tn_pairs = all_pair_ids - tp_pairs - fp_pairs - fn_pairs
    tp, fp, fn, tn = map(len, (tp_pairs, fp_pairs, fn_pairs, tn_pairs))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(all_pair_ids) if all_pair_ids else 0.0
    return ConflictMetrics(
        total_pairs=len(all_pair_ids),
        gold_positive=len(gold_positive),
        predicted_positive=len(predicted_positive),
        tp=tp,
        fp=fp,
        fn=fn,
        tn=tn,
        precision=precision,
        recall=recall,
        f1=f1,
        accuracy=accuracy,
        tp_pairs=tuple(sorted(tp_pairs, key=pair_sort_key)),
        fp_pairs=tuple(sorted(fp_pairs, key=pair_sort_key)),
        fn_pairs=tuple(sorted(fn_pairs, key=pair_sort_key)),
    )


def evaluate_dataset(root: Path, dataset: str, config: dict[str, Any]) -> tuple[ConflictMetrics, dict[str, str], dict[str, dict[str, Any]], dict[str, str]]:
    requirements = load_requirements(root / "datasets" / "requirements" / config["requirements"])
    gold, gold_classes = load_gold(
        root / "datasets" / "labels" / config["labels"],
        blank_class_is_conflict=bool(config["blank_class_is_conflict"]),
    )
    verdict_rows = load_jsonl(root / "results" / "final" / config["slug"] / "verdicts.jsonl")
    verdicts = {str(row["pair_id"]): row for row in verdict_rows}
    predicted = {
        pair_id
        for pair_id, row in verdicts.items()
        if row.get("verdict") == "incompatible"
        and not row.get("duplicate_conflict")
        and row.get("resolution_stage") != "duplicate_group_rule"
    }
    all_pair_ids = {
        normalize_pair(left, right)
        for left, right in combinations(sorted(requirements, key=id_sort_key), 2)
    }
    return score_conflicts(gold, predicted, all_pair_ids), requirements, verdicts, gold_classes


def rounded_metrics(metrics: ConflictMetrics) -> dict[str, Any]:
    payload = asdict(metrics)
    for key in ("precision", "recall", "f1", "accuracy"):
        payload[key] = round(float(payload[key]), 2)
    for key in ("tp_pairs", "fp_pairs", "fn_pairs"):
        payload[key] = list(payload[key])
    return payload


def render_pair_report(
    title: str,
    pair_ids: tuple[str, ...],
    requirements: dict[str, str],
    verdicts: dict[str, dict[str, Any]],
    gold_classes: dict[str, str],
) -> str:
    lines = [f"# {title}", "", f"Total pairs: **{len(pair_ids)}**", ""]
    if not pair_ids:
        lines.append("No pairs in this category.")
        return "\n".join(lines) + "\n"
    for pair_id in pair_ids:
        left, right = pair_id.split("_", 1)
        verdict = verdicts.get(pair_id, {})
        predicted = str(verdict.get("verdict", "compatible (implicit non-positive)"))
        confidence = verdict.get("confidence", "not available")
        reasoning = str(verdict.get("arbiter_reasoning", "")).strip() or "No final reasoning was emitted."
        gold_class = gold_classes.get(pair_id, "not labeled") or "conflict (blank source class)"
        lines.extend(
            [
                f"## {pair_id}",
                "",
                f"- Gold class: `{gold_class}`",
                f"- Predicted verdict: `{predicted}`",
                f"- Confidence: `{confidence}`",
                f"- R{left}: {requirements[left]}",
                f"- R{right}: {requirements[right]}",
                f"- Final reasoning: {reasoning}",
                "",
            ]
        )
    return "\n".join(lines)


def load_formal_expectations(root: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads((root / "results" / "summary" / "metrics.json").read_text(encoding="utf-8"))
    return {
        row["dataset"]: row["conflict_detection"]
        for row in payload["results"]
        if row.get("dataset") in DATASETS
    }


def sanitize_formal_summary(root: Path) -> None:
    path = root / "results" / "summary" / "metrics.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    for row in payload.get("results", []):
        dataset = row.get("dataset")
        config = DATASETS.get(str(dataset))
        if config is None:
            continue
        row.pop("run_dir", None)
        row.pop("routes_path", None)
        row["verdicts_path"] = f"results/final/{config['slug']}/verdicts.jsonl"
        row["gold_file"] = f"datasets/labels/{config['labels']}"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def assert_formal_metrics(dataset: str, actual: ConflictMetrics, expected: dict[str, Any]) -> None:
    for key in ("total_pairs", "gold_positive", "predicted_positive", "tp", "fp", "fn", "tn"):
        if getattr(actual, key) != int(expected[key]):
            raise AssertionError(
                f"{dataset} {key}: expected {expected[key]}, got {getattr(actual, key)}"
            )


def write_summary_markdown(root: Path, rows: list[tuple[str, ConflictMetrics]]) -> None:
    lines = [
        "# Full Four-View Framework Results",
        "",
        "Conflict detection metrics use `incompatible` as the positive prediction. Duplicate labels are excluded from the conflict-positive gold set.",
        "",
        "| Dataset | TP | FP | FN | TN | Precision | Recall | F1 | Accuracy |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for dataset, metrics in rows:
        lines.append(
            f"| {dataset} | {metrics.tp} | {metrics.fp} | {metrics.fn} | {metrics.tn} | "
            f"{metrics.precision:.2f} | {metrics.recall:.2f} | {metrics.f1:.2f} | {metrics.accuracy:.2f} |"
        )
    macro_f1 = sum(metrics.f1 for _, metrics in rows) / len(rows)
    lines.extend(
        [
            "",
            f"Mean F1 across datasets: **{macro_f1:.2f}**",
            "",
            "Uncertainty and abstention analysis: [uncertainty_summary.md](uncertainty_summary.md)",
            "",
        ]
    )
    (root / "results" / "summary" / "metrics.md").write_text("\n".join(lines), encoding="utf-8")


def generate_outputs(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    sanitize_formal_summary(root)
    expectations = load_formal_expectations(root)
    output: dict[str, dict[str, Any]] = {}
    summary_rows: list[tuple[str, ConflictMetrics]] = []
    for dataset, config in DATASETS.items():
        metrics, requirements, verdicts, gold_classes = evaluate_dataset(root, dataset, config)
        assert_formal_metrics(dataset, metrics, expectations[dataset])
        result_dir = root / "results" / "final" / config["slug"]
        result_dir.joinpath("metrics.json").write_text(
            json.dumps(rounded_metrics(metrics), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        result_dir.joinpath("false_positives.md").write_text(
            render_pair_report("False Positive Conflicts", metrics.fp_pairs, requirements, verdicts, gold_classes),
            encoding="utf-8",
        )
        result_dir.joinpath("missed_conflicts.md").write_text(
            render_pair_report("Missed Conflicts", metrics.fn_pairs, requirements, verdicts, gold_classes),
            encoding="utf-8",
        )
        result_dir.joinpath("correctly_detected_conflicts.md").write_text(
            render_pair_report("Correctly Detected Conflicts", metrics.tp_pairs, requirements, verdicts, gold_classes),
            encoding="utf-8",
        )
        output[dataset] = rounded_metrics(metrics)
        summary_rows.append((dataset, metrics))
    write_summary_markdown(root, summary_rows)
    return output


def main() -> int:
    output = generate_outputs()
    generate_reports()
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
