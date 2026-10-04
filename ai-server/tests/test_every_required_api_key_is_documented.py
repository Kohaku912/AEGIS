"""Every API key the shipped `config/llm.yaml` requires must be settable from the
repo's tracked env template, `.env.example`.

Measured 2026-10-05: `l1_default` (and `jev_decision`) declare
`api_key_env: TYPESAFE_API_KEY`, but `.env.example` listed only `LLM_API_KEY`
and `LLM_VISION_API_KEY`. A fresh deployment that followed the template would
build L1's TypeSafe provider with an EMPTY key, every L1 call would fail, and
every routed event would escalate -- L1 could not classify at all
(DELEGATION.md section 4 item 46). The key is now documented; this pin keeps the
whole class from coming back, not just the one instance.

The check is structural, not prose. It parses the profiles in llm.yaml for
`api_key_env`, then requires each key to appear in the template as an **assignment
line** (`KEY=`) -- a *mention* inside a comment does not count, which is the
difference between "the template tells you the key exists" and "the template sets
it". Four cases, so the main assertion can be neither vacuous nor tautological:
  - the scan finds keys we know are required (non-vacuity);
  - every required key has an assignment line;
  - the assignment check rejects a comment-only mention (a control);
  - a bogus key is reported as missing (a control).
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

_AI_SERVER = Path(__file__).resolve().parents[1]
_LLM_YAML = _AI_SERVER / "config" / "llm.yaml"
_ENV_EXAMPLE = _AI_SERVER.parent / ".env.example"

# Keys the shipped config is known to require. `LLM_API_KEY` is used by most
# profiles and `TYPESAFE_API_KEY` by the TypeSafe (L1 / decision) profiles;
# naming them is what makes the scan non-vacuous.
_KNOWN_KEYS = frozenset({"LLM_API_KEY", "TYPESAFE_API_KEY"})


def _required_api_key_envs() -> set[str]:
    """Every distinct non-empty `api_key_env` named by a profile in llm.yaml."""
    cfg = yaml.safe_load(_LLM_YAML.read_text(encoding="utf-8"))
    profiles = cfg.get("profiles") or {}
    return {
        p["api_key_env"]
        for p in profiles.values()
        if isinstance(p, dict) and p.get("api_key_env")
    }


def _documented(required, template: str) -> set[str]:
    """Keys the template actually *assigns* -- `KEY=` at the start of a line."""
    return {
        k for k in required if re.search(rf"^{re.escape(k)}=", template, re.MULTILINE)
    }


def test_the_scan_finds_the_known_keys() -> None:
    required = _required_api_key_envs()
    missing = sorted(_KNOWN_KEYS - required)
    assert not missing, (
        f"llm.yaml no longer declares {missing} -- either the profiles changed or the "
        f"scan is broken, and the documentation assertion below would be weakened "
        f"(found {sorted(required)})"
    )


def test_every_required_key_has_an_assignment_line_in_the_env_template() -> None:
    required = _required_api_key_envs()
    template = _ENV_EXAMPLE.read_text(encoding="utf-8")
    missing = sorted(required - _documented(required, template))
    assert not missing, (
        f"{missing} is required by config/llm.yaml but has no `KEY=` line in .env.example "
        "-- a deployment following the template would run those profiles with an empty key"
    )


def test_the_assignment_check_rejects_a_comment_only_mention() -> None:
    """Control: a mention in a comment is not an assignment."""
    synthetic = "# see FOO_API_KEY= for details\nBAR_API_KEY=\n"
    assert _documented({"FOO_API_KEY"}, synthetic) == set()
    assert _documented({"BAR_API_KEY"}, synthetic) == {"BAR_API_KEY"}


def test_the_assignment_check_reports_a_missing_key() -> None:
    """Control: the check can fail."""
    template = _ENV_EXAMPLE.read_text(encoding="utf-8")
    assert _documented({"__AEGIS_NOT_A_REAL_KEY__"}, template) == set()
