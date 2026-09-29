"""B-14: the SDK and the schema disagree about what a capability id may be.

**This file records an unresolved product call. It is not a fix.** Nothing here changes
either validator; the assertions pin the *current* disagreement so that resolving it in
either direction is a visible decision rather than a silent drift.

There is one id space, not two: ``define_capability`` returns an
``aegis_schema.models.Capability``, the same model whose ``id`` field the schema constrains.
But the SDK validates the id first, with its own regex, and the two disagree **in both
directions**:

===========  ==============================================  =========  ========
id           shape                                           SDK regex  schema
===========  ==============================================  =========  ========
``weather.get_forecast``            the SDK's own docstring example    accepts  rejects
``my_server.read_sensor``           the SDK's own ``server_prefix`` help  accepts  rejects
``ai-server.get_forecast``          a roster prefix, short form        rejects  accepts
``pc-server.screenshot.get_screenshot``  the canonical 3-segment form  rejects  accepts
===========  ==============================================  =========  ========

The SDK pattern is an **open class** (``[a-z][a-z0-9_]*``) — any lowercase prefix, exactly one
dot. The schema pattern is a **closed allowlist** of 12 prefixes, any number of segments. They
are therefore not merely different in size; each accepts ids the other refuses.

Consequences, all measured 2026-09-29:

- ``docs/plugin-sdk.md``'s Quick Start and ``capability.py``'s docstring both use
  ``server_prefix="weather"`` — that call raises a raw ``pydantic`` ``ValidationError``.
- ``examples/example-weather-server/weather_server.py`` cannot be **imported at all**.
- ``tools/create-capability-server`` emits ``server_prefix="{prefix}"``, so every generated
  server raises at import unless the user happened to choose ``dev``.
- ``define_capability`` defaults ``server_type=ServerType.DEV`` and never derives it from
  ``server_prefix``, so even a legitimate roster prefix needs an explicit ``server_type`` the
  SDK neither documents as required nor supplies. With default arguments, **only ``dev`` builds** —
  i.e. the SDK works out of the box solely for the server deleted in Phase 9.
- All 11 pre-existing SDK tests borrow that identity (``server_prefix="dev"``), which is why
  this is green.

The two product options — widen the schema pattern to admit third-party prefixes, or make the
SDK refuse them explicitly and say so — are recorded in ``PROJECT_STATUS_REVIEW.md`` §4.1 (B-14).
"""

from __future__ import annotations

import ast
import importlib.util
import re
from pathlib import Path

import pytest
from aegis_schema.models import Capability, RiskLevel, ServerType
from aegis_sdk.capability import define_capability

_SDK_PACKAGE = Path(__file__).resolve().parents[1]
_SAFETY_PY = _SDK_PACKAGE / "aegis_sdk" / "safety.py"


# ── Discovery: read both patterns from the thing that enforces them ───────────


def _schema_id_pattern() -> str:
    """The pattern the *live* ``Capability`` model enforces on ``id``.

    Read off the model rather than copied, so a copy cannot drift from the constraint.
    """
    for meta in Capability.model_fields["id"].metadata:
        pattern = getattr(meta, "pattern", None)
        if pattern:
            return str(pattern)
    raise AssertionError(
        "Capability.id no longer carries a pattern constraint — B-14 has changed shape; "
        "re-derive this pin instead of deleting it."
    )


def _sdk_id_pattern() -> str:
    """The pattern the SDK's own validator enforces.

    It is an inline literal inside ``validate_capability_definition``, so it is not
    importable; read it from source by AST.
    """
    tree = ast.parse(_SAFETY_PY.read_text(encoding="utf-8", newline=""))
    literals = [
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "match"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    ]
    assert len(literals) == 1, (
        f"expected exactly one re.match string literal in safety.py, found {literals!r} — "
        "if the id check moved, move this pin with it"
    )
    return str(literals[0])


def _alternation_of(pattern: str) -> tuple[str, ...] | None:
    """The prefix alternation of a pattern, or ``None`` when it has none.

    ``None`` is the meaningful answer: it means the pattern is an open class, not an allowlist.
    """
    match = re.search(r"\(([^()]*\|[^()]*)\)", pattern)
    return tuple(match.group(1).split("|")) if match else None


_SCHEMA_PATTERN = _schema_id_pattern()
_SDK_PATTERN = _sdk_id_pattern()

# The schema's allowlist as of 2026-09-29, 6 servers x {short, long} form.
_RECORDED_SCHEMA_PREFIXES: tuple[str, ...] = (
    "ai-server",
    "pc-server",
    "browser-server",
    "android-server",
    "room-server",
    "dev-server",
    "pc",
    "android",
    "browser",
    "room",
    "dev",
    "ai",
)


def _builds_with_default_arguments(prefix: str) -> bool:
    """Does ``define_capability`` succeed for ``prefix`` without the caller tuning anything?"""
    try:
        define_capability(
            server_prefix=prefix,
            action="thing",
            name="Thing",
            description="Probe capability, used only to measure the default path.",
            risk_level=RiskLevel.READ_ONLY,
        )
    except Exception:
        return False
    return True


# ── The two patterns themselves ──────────────────────────────────────────────


def test_the_schema_id_is_a_closed_allowlist_of_the_recorded_prefixes() -> None:
    """Widening the schema to admit third-party prefixes must fail here."""
    prefixes = _alternation_of(_SCHEMA_PATTERN)
    assert prefixes is not None, "the schema pattern is no longer an allowlist"
    assert set(prefixes) == set(_RECORDED_SCHEMA_PREFIXES)


def test_the_sdk_id_is_an_open_class_not_an_allowlist() -> None:
    """The SDK pattern accepts *any* lowercase prefix — that is the whole disagreement."""
    assert _alternation_of(_SDK_PATTERN) is None


@pytest.mark.parametrize(
    ("cap_id", "note"),
    [
        ("weather.get_forecast", "the SDK's own documented example"),
        ("my_server.read_sensor", "the SDK's own server_prefix help text"),
        ("ai-server.get_forecast", "a roster prefix in its short form"),
        ("pc-server.screenshot.get_screenshot", "the canonical 3-segment form"),
    ],
)
def test_the_two_patterns_disagree(cap_id: str, note: str) -> None:
    """Each of these is accepted by exactly one of the two validators."""
    sdk_verdict = bool(re.match(_SDK_PATTERN, cap_id))
    schema_verdict = bool(re.match(_SCHEMA_PATTERN, cap_id))
    assert sdk_verdict != schema_verdict, (
        f"{cap_id!r} ({note}) is now judged the same by both validators — "
        "if that is the fix, delete this pin and update B-14"
    )


def test_the_sdk_refuses_every_long_form_roster_prefix() -> None:
    """``-`` is not in the SDK's character class, so all six ``*-server`` prefixes are refused.

    This is the half of the disagreement that no ``server_prefix`` choice can work around.
    """
    long_form = tuple(p for p in _RECORDED_SCHEMA_PREFIXES if "-" in p)
    assert len(long_form) == 6
    for prefix in long_form:
        assert re.match(_SCHEMA_PATTERN, f"{prefix}.get_thing"), prefix
        assert not re.match(_SDK_PATTERN, f"{prefix}.get_thing"), prefix


# ── The behavioural half: what a user actually gets ──────────────────────────


@pytest.mark.parametrize("prefix", _RECORDED_SCHEMA_PREFIXES)
def test_default_arguments_build_only_for_the_deleted_servers_prefix(prefix: str) -> None:
    """``define_capability`` defaults ``server_type`` to DEV and never derives it.

    So a roster prefix builds only when the caller also passes the matching ``server_type``.
    With defaults, exactly one prefix works — ``dev``, whose server was deleted in Phase 9.
    """
    assert _builds_with_default_arguments(prefix) is (prefix == "dev")


def test_only_one_prefix_survives_the_default_path() -> None:
    """The summary form of the parametrised test above, so the set is asserted by equality."""
    survivors = tuple(p for p in _RECORDED_SCHEMA_PREFIXES if _builds_with_default_arguments(p))
    assert survivors == ("dev",)


def test_a_live_prefix_needs_an_explicit_server_type_the_sdk_never_derives() -> None:
    """The failure names a server_type the caller never chose, and never mentions the prefix."""
    with pytest.raises(Exception) as excinfo:
        define_capability(
            server_prefix="pc",
            action="screenshot",
            name="Screenshot",
            description="Take a screenshot.",
            risk_level=RiskLevel.READ_ONLY,
        )
    message = str(excinfo.value)
    assert "should start with one of ('dev', 'dev-server')" in message
    assert "server_type=DEV" in message

    # ...and the very same call works once the caller supplies the mapping the SDK does not.
    cap = define_capability(
        server_prefix="pc",
        action="screenshot",
        name="Screenshot",
        description="Take a screenshot.",
        risk_level=RiskLevel.READ_ONLY,
        server_type=ServerType.PC,
    )
    assert cap.id == "pc.screenshot"


def test_the_documented_example_cannot_be_built() -> None:
    """``server_prefix="weather"`` is the SDK's own docstring example and the docs' Quick Start.

    It fails on the *schema's* field constraint, so the user sees a raw pydantic error rather
    than the SDK's friendly ``ValueError``. (``ValidationError`` subclasses ``ValueError``, so
    the SDK's documented ``Raises: ValueError`` is technically honoured — the message is not.)
    """
    with pytest.raises(Exception) as excinfo:
        define_capability(
            server_prefix="weather",
            action="get_forecast",
            name="Get Weather Forecast",
            description="Retrieve weather forecast for a location.",
            risk_level=RiskLevel.READ_ONLY,
        )
    message = str(excinfo.value)
    assert "weather.get_forecast" in message
    assert "string_pattern_mismatch" in message or "match pattern" in message


def test_the_shipped_example_server_cannot_be_imported() -> None:
    """``examples/example-weather-server`` raises at import, and nothing in the repo imports it.

    No test, script or CI job referenced this file, which is how it stayed broken.
    """
    example = _SDK_PACKAGE.parents[1] / "examples" / "example-weather-server" / "weather_server.py"
    assert example.is_file(), f"the shipped example moved or was deleted: {example}"

    spec = importlib.util.spec_from_file_location("_b14_example_server", example)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    with pytest.raises(Exception) as excinfo:
        spec.loader.exec_module(module)
    assert "weather.get_forecast" in str(excinfo.value)
