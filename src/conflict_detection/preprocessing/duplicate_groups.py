from __future__ import annotations

from dataclasses import dataclass

from conflict_detection.orchestration.session_types import (
    DetectionPair,
    DuplicateRequirementGroup,
    PairRoute,
)


def _numeric_req_sort_key(req_id: str) -> tuple[int, str]:
    digits = "".join(char for char in req_id if char.isdigit())
    if digits:
        return int(digits), req_id
    return 10**12, req_id


@dataclass
class DuplicateRouteResult:
    candidate_pairs: list[DetectionPair]
    filtered_pairs: list[DetectionPair]
    duplicate_groups: list[DuplicateRequirementGroup]
    canonical_requirement_map: dict[str, str]
    pair_routes: list[PairRoute]


class _DisjointSet:
    def __init__(self, node_ids: list[str]) -> None:
        self._parent = {node_id: node_id for node_id in node_ids}

    def find(self, node_id: str) -> str:
        parent = self._parent[node_id]
        if parent != node_id:
            self._parent[node_id] = self.find(parent)
        return self._parent[node_id]

    def union(self, left: str, right: str) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return
        if _numeric_req_sort_key(left_root) <= _numeric_req_sort_key(right_root):
            self._parent[right_root] = left_root
        else:
            self._parent[left_root] = right_root


@dataclass(frozen=True)
class _PairRouteContext:
    pair_id: str
    r1_id: str
    r1_text: str
    r2_id: str
    r2_text: str
    similarity: float
    canonical_r1_id: str
    canonical_r1_text: str
    canonical_r2_id: str
    canonical_r2_text: str
    canonical_pair_id: str | None
    candidate_pair: DetectionPair | None
    same_duplicate_group: bool
    both_endpoints_canonical: bool


def build_duplicate_routes(
    scored_pairs: list[dict[str, str | float]],
    *,
    threshold: float,
    duplicate_threshold: float,
) -> DuplicateRouteResult:
    requirement_texts: dict[str, str] = {}
    for pair in scored_pairs:
        requirement_texts[str(pair["r1_id"])] = str(pair["r1_text"])
        requirement_texts[str(pair["r2_id"])] = str(pair["r2_text"])

    dsu = _DisjointSet(list(requirement_texts.keys()))
    for pair in scored_pairs:
        similarity = float(pair["cosine_similarity"])
        if similarity >= duplicate_threshold:
            dsu.union(str(pair["r1_id"]), str(pair["r2_id"]))

    group_members: dict[str, list[str]] = {}
    for req_id in requirement_texts:
        root = dsu.find(req_id)
        group_members.setdefault(root, []).append(req_id)

    canonical_requirement_map: dict[str, str] = {}
    duplicate_groups: list[DuplicateRequirementGroup] = []
    for members in group_members.values():
        ordered_members = sorted(members, key=_numeric_req_sort_key)
        canonical_id = ordered_members[0]
        canonical_text = requirement_texts[canonical_id]
        duplicate_groups.append(
            DuplicateRequirementGroup(
                canonical_id=canonical_id,
                canonical_text=canonical_text,
                member_ids=ordered_members,
            )
        )
        for member_id in ordered_members:
            canonical_requirement_map[member_id] = canonical_id
    duplicate_groups.sort(key=lambda item: _numeric_req_sort_key(item.canonical_id))

    candidate_pairs: list[DetectionPair] = []
    filtered_pairs: list[DetectionPair] = []
    pair_routes: list[PairRoute] = []
    candidate_canonical_pair_ids: set[str] = set()
    route_contexts: list[_PairRouteContext] = []

    for pair in scored_pairs:
        pair_id = str(pair["pair_id"])
        r1_id = str(pair["r1_id"])
        r2_id = str(pair["r2_id"])
        r1_text = str(pair["r1_text"])
        r2_text = str(pair["r2_text"])
        similarity = float(pair["cosine_similarity"])
        canonical_r1_id = canonical_requirement_map[r1_id]
        canonical_r2_id = canonical_requirement_map[r2_id]
        canonical_r1_text = requirement_texts[canonical_r1_id]
        canonical_r2_text = requirement_texts[canonical_r2_id]

        if canonical_r1_id == canonical_r2_id:
            route_contexts.append(
                _PairRouteContext(
                    pair_id=pair_id,
                    r1_id=r1_id,
                    r1_text=r1_text,
                    r2_id=r2_id,
                    r2_text=r2_text,
                    similarity=similarity,
                    canonical_r1_id=canonical_r1_id,
                    canonical_r1_text=canonical_r1_text,
                    canonical_r2_id=canonical_r2_id,
                    canonical_r2_text=canonical_r2_text,
                    canonical_pair_id=None,
                    candidate_pair=None,
                    same_duplicate_group=True,
                    both_endpoints_canonical=(r1_id == canonical_r1_id and r2_id == canonical_r2_id),
                )
            )
            continue

        ordered_canonical = sorted(
            [
                (canonical_r1_id, canonical_r1_text),
                (canonical_r2_id, canonical_r2_text),
            ],
            key=lambda item: _numeric_req_sort_key(item[0]),
        )
        canonical_pair_id = f"{ordered_canonical[0][0]}_{ordered_canonical[1][0]}"
        canonical_pair = DetectionPair(
            pair_id=canonical_pair_id,
            r1_id=ordered_canonical[0][0],
            r1_text=ordered_canonical[0][1],
            r2_id=ordered_canonical[1][0],
            r2_text=ordered_canonical[1][1],
            cosine_similarity=similarity,
        )
        both_endpoints_canonical = r1_id == canonical_r1_id and r2_id == canonical_r2_id
        route_contexts.append(
            _PairRouteContext(
                pair_id=pair_id,
                r1_id=r1_id,
                r1_text=r1_text,
                r2_id=r2_id,
                r2_text=r2_text,
                similarity=similarity,
                canonical_r1_id=ordered_canonical[0][0],
                canonical_r1_text=ordered_canonical[0][1],
                canonical_r2_id=ordered_canonical[1][0],
                canonical_r2_text=ordered_canonical[1][1],
                canonical_pair_id=canonical_pair_id,
                candidate_pair=canonical_pair,
                same_duplicate_group=False,
                both_endpoints_canonical=both_endpoints_canonical,
            )
        )

    for context in route_contexts:
        if context.same_duplicate_group:
            continue
        if not context.both_endpoints_canonical:
            continue
        if context.canonical_pair_id is None or context.candidate_pair is None:
            continue
        if threshold <= context.similarity < duplicate_threshold:
            if context.canonical_pair_id not in candidate_canonical_pair_ids:
                candidate_pairs.append(context.candidate_pair)
                candidate_canonical_pair_ids.add(context.canonical_pair_id)

    for context in route_contexts:
        raw_pair = DetectionPair(
            pair_id=context.pair_id,
            r1_id=context.r1_id,
            r1_text=context.r1_text,
            r2_id=context.r2_id,
            r2_text=context.r2_text,
            cosine_similarity=context.similarity,
        )
        if context.same_duplicate_group:
            filtered_pairs.append(raw_pair)
            route_type = "duplicate_conflict"
        elif (
            context.canonical_pair_id is not None
            and context.both_endpoints_canonical
            and context.canonical_pair_id in candidate_canonical_pair_ids
        ):
            route_type = "canonical_candidate"
        elif context.canonical_pair_id is not None and context.canonical_pair_id in candidate_canonical_pair_ids:
            route_type = "canonical_alias"
        else:
            filtered_pairs.append(raw_pair)
            route_type = "filtered_non_candidate"

        pair_routes.append(
            PairRoute(
                pair_id=context.pair_id,
                r1_id=context.r1_id,
                r1_text=context.r1_text,
                r2_id=context.r2_id,
                r2_text=context.r2_text,
                cosine_similarity=context.similarity,
                route_type=route_type,
                canonical_pair_id=context.canonical_pair_id,
                canonical_r1_id=context.canonical_r1_id,
                canonical_r1_text=context.canonical_r1_text,
                canonical_r2_id=context.canonical_r2_id,
                canonical_r2_text=context.canonical_r2_text,
            )
        )

    return DuplicateRouteResult(
        candidate_pairs=candidate_pairs,
        filtered_pairs=filtered_pairs,
        duplicate_groups=duplicate_groups,
        canonical_requirement_map=canonical_requirement_map,
        pair_routes=pair_routes,
    )
