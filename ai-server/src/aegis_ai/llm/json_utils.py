"""Utilities for parsing structured JSON from LLM responses."""

from __future__ import annotations

import json
from typing import Any


def extract_json_object(text: str) -> dict[str, Any]:
    """Parse the first complete JSON object from an LLM response.

    LLMs sometimes wrap valid JSON in markdown fences or add short prose around it.
    This keeps callers strict about requiring a JSON object while avoiding brittle
    whole-response parsing.
    """
    clean = text.strip()
    if clean.startswith("```"):
        lines = clean.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        clean = "\n".join(lines).strip()

    try:
        data = json.loads(clean)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    start = clean.find("{")
    if start < 0:
        raise json.JSONDecodeError("No JSON object found", clean, 0)

    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(clean)):
        char = clean[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = clean[start : index + 1]
                data = json.loads(candidate)
                if not isinstance(data, dict):
                    raise json.JSONDecodeError("Top-level JSON value is not an object", candidate, 0)
                return data

    raise json.JSONDecodeError("Unterminated JSON object", clean, start)
