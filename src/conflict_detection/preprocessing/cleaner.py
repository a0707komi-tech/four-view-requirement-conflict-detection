from __future__ import annotations

import re


_CHAR_REPLACEMENTS = {
    "\u2013": "-",
    "\u2014": "--",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
}


def clean_text(text: object) -> str:
    if not isinstance(text, str):
        return ""

    normalized = text.replace("\r", " ").replace("\n", " ").strip()
    for source, target in _CHAR_REPLACEMENTS.items():
        normalized = normalized.replace(source, target)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized
