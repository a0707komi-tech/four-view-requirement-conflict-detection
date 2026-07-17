from pathlib import Path

from scripts.evaluate_results import DATASETS, evaluate_dataset, score_conflicts


ROOT = Path(__file__).resolve().parents[1]


def test_conflict_metrics_exclude_duplicate_labels() -> None:
    metrics = score_conflicts(
        gold_positive={"1_2"},
        predicted_positive={"1_2", "1_3"},
        all_pair_ids={"1_2", "1_3", "2_3"},
    )

    assert (metrics.tp, metrics.fp, metrics.fn, metrics.tn) == (1, 1, 0, 1)


def test_all_dataset_metrics_match_formal_counts() -> None:
    expected = {
        "ETCS-GOLD": (36, 26, 13, 1941),
        "OpenAPI Specification 3.0": (20, 2, 0, 1631),
        "promise-project2": (7, 1, 4, 2004),
        "Broker-All": (8, 1, 5, 976),
        "Library-Gold": (17, 0, 3, 5866),
    }

    for dataset, config in DATASETS.items():
        metrics, _, _, _ = evaluate_dataset(ROOT, dataset, config)
        assert (metrics.tp, metrics.fp, metrics.fn, metrics.tn) == expected[dataset]
