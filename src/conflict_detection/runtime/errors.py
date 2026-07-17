from __future__ import annotations


class TechnicalParseError(RuntimeError):
    """Raised when an LLM response cannot be parsed into the expected JSON shape."""

