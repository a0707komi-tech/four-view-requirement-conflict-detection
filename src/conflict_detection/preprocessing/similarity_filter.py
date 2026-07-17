from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from pathlib import Path


ScorePair = dict[str, str | float]
DUPLICATE_SIMILARITY_THRESHOLD = 1.0


def _cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    numerator = sum(float(a) * float(b) for a, b in zip(left, right))
    left_norm = math.sqrt(sum(float(value) * float(value) for value in left))
    right_norm = math.sqrt(sum(float(value) * float(value) for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)


class SimilarityFilter:
    def __init__(
        self,
        model_path: str | Path | None = None,
        scorer: Callable[[list[dict[str, str]]], list[float]] | None = None,
    ) -> None:
        self.model_path = Path(model_path) if model_path else None
        self._scorer = scorer

    def score_pairs(self, pairs: list[dict[str, str]]) -> list[ScorePair]:
        if not pairs:
            return []

        scores = self._score_values(pairs)
        scored_pairs: list[ScorePair] = []
        for pair, score in zip(pairs, scores):
            enriched = dict(pair)
            enriched["cosine_similarity"] = round(float(score), 6)
            scored_pairs.append(enriched)
        return scored_pairs

    def _score_values(self, pairs: list[dict[str, str]]) -> list[float]:
        if self._scorer is not None:
            return [float(value) for value in self._scorer(pairs)]

        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "sentence_transformers is required for SimilarityFilter unless "
                "a test explicitly injects a scorer or similarity_filter."
            ) from exc

        texts_by_id: dict[str, str] = {}
        for pair in pairs:
            texts_by_id[pair["r1_id"]] = pair["r1_text"]
            texts_by_id[pair["r2_id"]] = pair["r2_text"]

        ordered_ids = list(texts_by_id.keys())
        model = SentenceTransformer(str(self.model_path) if self.model_path else None)
        embeddings = model.encode(
            [texts_by_id[req_id] for req_id in ordered_ids],
            show_progress_bar=False,
        )
        embedding_by_id = dict(zip(ordered_ids, embeddings))
        return [
            _cosine_similarity(embedding_by_id[pair["r1_id"]], embedding_by_id[pair["r2_id"]])
            for pair in pairs
        ]
