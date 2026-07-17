from __future__ import annotations


def generate_pairs(requirements: list[dict[str, str]]) -> list[dict[str, str]]:
    pairs: list[dict[str, str]] = []
    for left_index, left in enumerate(requirements):
        for right in requirements[left_index + 1 :]:
            pairs.append(
                {
                    "pair_id": f"{left['req_id']}_{right['req_id']}",
                    "r1_id": left["req_id"],
                    "r1_text": left["text"],
                    "r2_id": right["req_id"],
                    "r2_text": right["text"],
                }
            )
    return pairs
