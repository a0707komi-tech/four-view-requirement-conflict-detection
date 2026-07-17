from __future__ import annotations

import json
from typing import Any


def _strip_code_fence(raw_text: str) -> str:
    raw_text = raw_text.strip()
    if not raw_text.startswith("```"):
        return raw_text

    lines = raw_text.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def parse_json_response(
    raw_text: str, *, default_verdict: str = "uncertain"
) -> dict[str, Any]:
    cleaned = _strip_code_fence(raw_text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        try:
            start = cleaned.index("{")
            end = cleaned.rindex("}") + 1
            return json.loads(cleaned[start:end])
        except (ValueError, json.JSONDecodeError):
            return {
                "verdict": default_verdict,
                "confidence": 0.0,
                "reasoning": "Failed to parse LLM output",
                "key_evidence": [],
                "assumptions": [],
                "pairwise_conflict_grounded": False,
                "technical_issue": "parse_error",
                "_parse_error": True,
                "_raw": raw_text[:500],
            }
