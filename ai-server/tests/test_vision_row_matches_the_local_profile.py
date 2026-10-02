"""The §3.2 vision row is a claim about the code — check it against the resolver.

Why this file exists
--------------------
On 2026-10-01 the §3.2 feature table still read, of ``vision のローカル代替``:

    ❌ ``llm.yaml`` が Aliyun を指したまま。egress ゲートが止めるため視覚機能は実質不可

Both halves are false. ``llm.yaml`` does define ``profiles.local_vision``
(``http://localhost:11434/v1``, Ollama ``qwen2.5vl:7b``), and
``LLMSettingsResolver._LOCAL_PROFILE_MAP`` remaps ``vision_observation`` onto it, so under
``mode: local`` the *resolved* destination is inside the environment. The Aliyun URL is the
cloud definition that the remap **replaces** — reading it as the effective one is the
mistake. AEGIS's own ``verify_egress_configuration`` consequently reports
``local_llm_readiness: ok`` with zero violations.

The stale row was not merely cosmetic, it was *actionable*: ``DECISION_DRAFTS.md`` §C read it
as a mandate to "declare in the UI/docs that vision is disabled". Executing that literally
would have published, to the user, a claim contradicting the system's own readiness verdict.

Why not a forbidden-phrase scan. The corrected row **quotes** the refuted wording, so a
phrase scan would fail on the correction itself — the same shape that makes a
hand-maintained exclusion list a defect (``PROJECT_STATUS_REVIEW.md`` §4.3). So this pins the
row's *verdict marker* to the resolved destination instead: a check that fails in **both**
directions and needs no list.

How it checks. ``vision_observation`` is resolved through the real resolver and the
resulting ``base_url`` is classified with the same ``is_local_destination`` the gate uses.
Resolves locally -> the row must read ✅. Resolves externally -> the row must read ❌. There
is one right answer, and it is in the code.
"""

from __future__ import annotations

import re
from pathlib import Path

from aegis_ai.egress import is_local_destination
from aegis_ai.llm.settings_resolver import LLMSettingsResolver

_REPO = Path(__file__).resolve().parents[2]
_STATUS_REVIEW = _REPO / "PROJECT_STATUS_REVIEW.md"
_LLM_YAML = _REPO / "ai-server" / "config" / "llm.yaml"

#: The row under test. Greedy ``.+`` so a ``|`` inside the cell cannot truncate it.
_ROW = re.compile(r"^\|\s*vision のローカル代替\s*\|\s*(?P<body>.+)\s*\|\s*$", re.M)

#: Verdict markers used by §3.2. ``⚠️`` is two code points (U+26A0 U+FE0F), so the check
#: is a prefix test, not an equality on ``body[0]``.
_VERDICTS = ("✅", "❌", "⚠")


def _row_body() -> str:
    text = _STATUS_REVIEW.read_text(encoding="utf-8")
    match = _ROW.search(text)
    assert match is not None, (
        "PROJECT_STATUS_REVIEW.md §3.2 has no 'vision のローカル代替' row — the table was "
        "probably reformatted, which would make this file vacuous"
    )
    return match.group("body")


def _resolved_vision_base_url() -> str:
    """Resolve ``vision_observation`` **under local mode**.

    The row's claim is that a local replacement *exists* — which is a property of
    ``mode: local`` (the ``local_vision`` profile plus the remap that reaches it). The
    shipped config moved to ``mode: cloud`` on 2026-10-03 so that L1 reaches JEV, and in
    cloud mode ``vision_observation`` resolves to its declared Aliyun endpoint **by
    configuration** — a permitted choice, not "no local replacement exists". Reading the
    shipped mode here would conflate the two and make the row wrong for a reason it does
    not assert.
    """
    import tempfile

    import yaml

    data = yaml.safe_load(_LLM_YAML.read_text(encoding="utf-8"))
    data["mode"] = "local"
    path = Path(tempfile.mkdtemp(prefix="aegis-vision-local-")) / "llm.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")

    settings = LLMSettingsResolver(str(path)).resolve(profile_id="vision_observation")
    return settings.base_url


# ── Non-vacuity: the row must exist and carry a verdict ───────────────────────


def test_the_vision_row_carries_a_verdict_marker() -> None:
    body = _row_body()
    assert body.startswith(_VERDICTS), (
        f"the vision row starts with {body[:2]!r}, not a verdict marker {_VERDICTS}. The "
        "verdict is the thing this pin ties to the code, so it must be present."
    )


# ── The invariant: the row agrees with what the resolver actually returns ─────


def test_the_vision_row_verdict_matches_the_resolved_destination() -> None:
    """✅ while vision resolves locally; ❌ if it ever resolves outside the environment."""
    marker = _row_body()[0]
    base_url = _resolved_vision_base_url()
    local = is_local_destination(base_url)

    expected = "✅" if local else "❌"
    assert marker == expected, (
        f"§3.2 marks vision {marker} but vision_observation resolves to {base_url!r} "
        f"(is_local_destination={local}). The row and the resolver disagree.\n"
        "  - resolves locally     -> a local replacement exists -> ✅\n"
        "  - resolves externally  -> no local replacement      -> ❌\n"
        "Fix whichever is wrong — do not make the row the thing that has to stay wrong."
    )


def test_the_vision_row_names_what_makes_the_replacement_real() -> None:
    """A ✅ has to be explained by the two things that make it true.

    The profile alone is inert: it is ``_LOCAL_PROFILE_MAP`` that routes
    ``vision_observation`` onto it. Naming only one of the two would leave the reader
    unable to tell whether the replacement is actually reached.
    """
    body = _row_body()
    assert "local_vision" in body, (
        "the row must name the local profile that provides the replacement"
    )
    assert "_LOCAL_PROFILE_MAP" in body, (
        "the row must name the remap that routes vision_observation onto it — without it the "
        "local profile would exist but never be reached"
    )
