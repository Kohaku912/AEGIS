from __future__ import annotations

import pytest

from aegis_ai.llm.json_utils import extract_json_object


def test_extract_json_object_from_plain_json() -> None:
    assert extract_json_object('{"interval_seconds": 900}') == {"interval_seconds": 900}


def test_extract_json_object_from_markdown_fence() -> None:
    response = """```json
{"emotion_label": "satisfied", "learning": "Keep the server status visible."}
```"""

    assert extract_json_object(response)["emotion_label"] == "satisfied"


def test_extract_json_object_from_wrapped_text_with_braces_in_string() -> None:
    response = 'Here is the result:\n{"reason": "PowerShell returned {ok}", "interval_seconds": 300}\nDone.'

    assert extract_json_object(response) == {
        "reason": "PowerShell returned {ok}",
        "interval_seconds": 300,
    }


def test_extract_json_object_rejects_missing_object() -> None:
    with pytest.raises(ValueError):
        extract_json_object("no structured data")
