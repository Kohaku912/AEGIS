"""B-14: the SDK and the schema now agree about what a capability id may be — pin the agreement.

**This file used to pin the opposite.** Until 2026-09-29 it asserted that the SDK's id regex and
the schema's id pattern disagreed *in both directions*, so that fixing either side turned it red.
The owner chose option ② of the register's A-2 row — **make the SDK refuse third-party prefixes
explicitly and say so** — so the disagreement is gone and this file now pins the contract that
replaced it:

1. There is **one rule**, ``aegis_schema.models.CAPABILITY_ID_PATTERN``. The SDK imports it; it
   does not carry a second regex. The SDK accepts exactly what the schema accepts.
2. A prefix outside the roster is refused by **name**, as a plain ``ValueError``, before pydantic
   ever sees the id.
3. ``server_type`` is **derived** from the prefix. It used to default to ``ServerType.DEV`` and
   never be derived, so with default arguments only ``dev`` built — the server deleted in Phase 9.
4. The three artefacts that drifted under the old rule — the docstring example, the shipped
   example server, and the scaffold's output — **build**, and are executed here rather than
   described.

Every test below fails if its half is reverted; the ones that execute an artefact exist because
the artefacts were shipped broken for as long as nothing ran them (bug class 11 in
``PROJECT_STATUS_REVIEW.md`` §4.3: *nobody runs it, so nothing checks it*).
"""

from __future__ import annotations

import ast
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from aegis_schema.models import CAPABILITY_ID_PATTERN, Capability, RiskLevel, ServerType
from aegis_schema.roster import PREFIXES_BY_TYPE_WITH_RETIRED

from aegis_sdk import ALLOWED_SERVER_PREFIXES, SERVER_TYPE_BY_PREFIX, define_capability
from aegis_sdk.testing import MockAEGISCore

_SDK_PACKAGE = Path(__file__).resolve().parents[1]
_REPO = _SDK_PACKAGE.parents[1]
_CAPABILITY_PY = _SDK_PACKAGE / "aegis_sdk" / "capability.py"
_SAFETY_PY = _SDK_PACKAGE / "aegis_sdk" / "safety.py"
_EXAMPLE = _REPO / "examples" / "example-weather-server" / "weather_server.py"
_SCAFFOLD = _REPO / "tools" / "create-capability-server" / "create_server.py"

#: The prefixes the roster declares, flattened — the SDK's allowed set must equal this, not
#: resemble it. Derived here as well so the comparison is between two independent expressions.
_ROSTER_PREFIXES: tuple[str, ...] = tuple(
    prefix for prefixes in PREFIXES_BY_TYPE_WITH_RETIRED.values() for prefix in prefixes
)

#: Ids that used to be judged differently by the two validators, plus the shapes around them.
#: Each is split at its first dot into ``(server_prefix, action)`` to drive ``define_capability``,
#: which rebuilds exactly the same id.
_ID_CORPUS: tuple[str, ...] = (
    "weather.get_forecast",  # the SDK's own old docstring example: was SDK-accepts/schema-rejects
    "my_server.read_sensor",  # the old ``server_prefix`` help text: same
    "ai-server.get_forecast",  # a roster prefix, short form: was SDK-rejects/schema-accepts
    "pc-server.screenshot.get_screenshot",  # the canonical 3-segment form: same
    "room-server.weather.get_forecast",  # the shape the example and docs now use
    "room.get_forecast",
    "dev.thing",
    "pc-server.a.b.c.d",  # any number of trailing segments
    "pcs.get_forecast",  # looks like a prefix, is not one
    "weather-server.thing",  # a plausible-looking server that is not in the roster
    "pc-server.Bad",  # uppercase segment
    "pc-server.",  # empty action
    ".get_forecast",  # empty prefix
)


def _build(cap_id: str) -> Capability:
    """Build ``cap_id`` through the SDK, splitting it the same way the SDK joins it."""
    prefix, _, action = cap_id.partition(".")
    return define_capability(
        server_prefix=prefix,
        action=action,
        name="Thing",
        description="Probe capability, used only to pin the id contract.",
        risk_level=RiskLevel.READ_ONLY,
    )


def _sdk_accepts(cap_id: str) -> bool:
    """Whether the SDK lets ``cap_id`` through — *any* refusal counts, not just the id one."""
    try:
        _build(cap_id)
    except ValueError:
        return False
    return True


def _docstring_call_source() -> str:
    """The ``define_capability(...)`` call inside ``capability.py``'s own module docstring.

    Read from source so the documented example cannot drift from a working call: the call is
    extracted by balancing parentheses, parsed as an expression, and executed by the test below.
    """
    module = ast.parse(_CAPABILITY_PY.read_text(encoding="utf-8", newline=""))
    docstring = ast.get_docstring(module)
    assert docstring, "capability.py no longer has a module docstring to check"

    start = docstring.find("define_capability(")
    assert start != -1, "the module docstring no longer shows a define_capability() call"
    call = docstring[start:]
    depth = 0
    for index, char in enumerate(call):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return call[: index + 1]
    raise AssertionError("the documented define_capability() call has unbalanced parentheses")


def _load_module(path: Path, name: str):
    """Import a file by path, so an artefact outside the package can be executed."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _listed_prefixes(message: str) -> tuple[str, ...]:
    """The prefixes the refusal *lists* as allowed, parsed out of the message.

    The message renders ``ALLOWED_SERVER_PREFIXES``, so the rendered tuple is the claim under
    test — and a substring check cannot read it. ``"room" in "...'room-server'..."`` is ``True``,
    so a message that spelled every prefix in its *short* form would pass one; and a message
    listing an **extra** prefix the SDK still refuses passes one too, which sends the caller to a
    spelling that fails. Parse the tuple and compare it whole, so both directions fail.
    """
    marker = "must be one of "
    start = message.find(marker)
    assert start != -1, f"the refusal no longer says what the prefix must be one of: {message}"
    tail = message[start + len(marker) :]
    depth = 0
    for index, char in enumerate(tail):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                parsed = ast.literal_eval(tail[: index + 1])
                assert isinstance(parsed, tuple), f"the listed prefixes are not a tuple: {parsed!r}"
                assert all(isinstance(p, str) for p in parsed), f"non-string prefix: {parsed!r}"
                return parsed
    raise AssertionError(f"the refusal's prefix list has unbalanced parentheses: {message}")


# ── 1. One rule, shared with the schema ──────────────────────────────────────


def test_the_schema_field_enforces_the_named_pattern() -> None:
    """The constant is not a copy — it is what the live model validates against."""
    live = Capability.model_fields["id"].metadata[0].pattern
    assert live == CAPABILITY_ID_PATTERN, (
        "Capability.id no longer uses CAPABILITY_ID_PATTERN, so the SDK and the model are two "
        "rules again — which is the defect this file exists to prevent (B-14)."
    )


def test_the_sdk_carries_no_second_id_pattern() -> None:
    """``safety.py`` must not re-spell the rule. A second regex is how the drift started."""
    tree = ast.parse(_SAFETY_PY.read_text(encoding="utf-8", newline=""))
    inline = [
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "match"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    ]
    assert inline == [], (
        f"safety.py matches an inline regex literal again: {inline!r}. The id rule belongs to "
        "aegis_schema.models.CAPABILITY_ID_PATTERN; import it instead."
    )


def test_the_allowed_prefixes_are_the_roster() -> None:
    """The SDK's allowlist is derived from the roster, so it cannot drift from it (B-15)."""
    assert ALLOWED_SERVER_PREFIXES == _ROSTER_PREFIXES
    assert len(ALLOWED_SERVER_PREFIXES) == 12


@pytest.mark.parametrize("cap_id", _ID_CORPUS)
def test_the_sdk_judges_every_id_exactly_as_the_schema_does(cap_id: str) -> None:
    """The whole point of the fix: one id space, one verdict.

    Before it, ``weather.get_forecast`` was SDK-accepts/schema-rejects and
    ``pc-server.screenshot.get_screenshot`` was the reverse.
    """
    assert _sdk_accepts(cap_id) is bool(re.match(CAPABILITY_ID_PATTERN, cap_id)), (
        f"{cap_id!r}: the SDK and the schema disagree again — that is B-14 coming back"
    )


def test_the_corpus_still_contains_both_verdicts() -> None:
    """Guard the guard: a corpus that is all-accept or all-reject would prove nothing."""
    verdicts = {bool(re.match(CAPABILITY_ID_PATTERN, cap_id)) for cap_id in _ID_CORPUS}
    assert verdicts == {True, False}


# ── 2. The refusal, by name ──────────────────────────────────────────────────


@pytest.mark.parametrize("prefix", ["weather", "my_server", "weather-server", "pcs"])
def test_a_third_party_prefix_is_refused_by_name(prefix: str) -> None:
    """The decision (A-2 ②): refuse explicitly, naming the prefix and the allowed set."""
    with pytest.raises(ValueError) as excinfo:
        define_capability(
            server_prefix=prefix,
            action="get_forecast",
            name="Get Weather Forecast",
            description="Retrieve weather forecast for a location.",
            risk_level=RiskLevel.READ_ONLY,
        )
    message = str(excinfo.value)
    assert prefix in message, f"the refusal does not name the offending prefix: {message}"
    assert "is not an AEGIS server" in message
    listed = _listed_prefixes(message)
    assert listed == _ROSTER_PREFIXES, (
        f"the refusal lists {listed!r}, but the roster declares {_ROSTER_PREFIXES!r}. An omitted "
        "prefix sends the caller to a spelling that still fails; an *added* one sends them to a "
        "spelling the SDK would refuse just the same. Compare the parsed set, not substrings — a "
        "substring check cannot tell 'room' from 'room-server' (B-14)."
    )


def test_the_listed_prefixes_parser_reads_the_message_not_a_constant() -> None:
    """Guard the guard: a parser that answered ``_ROSTER_PREFIXES`` regardless is a tautology.

    Both sides of the equality above derive from ``PREFIXES_BY_TYPE_WITH_RETIRED``, so the check
    only means anything if the parser really reads the *message*. Feed it a message listing a
    different set and it must answer with that set — and refuse to answer one that lists none.
    """
    assert _listed_prefixes(
        "the prefix must be one of ('room', 'pc'); use the segments after the first"
    ) == ("room", "pc")
    with pytest.raises(AssertionError):
        _listed_prefixes("the prefix must be one of nothing in particular")


def test_the_refusal_is_the_sdks_own_not_pydantics() -> None:
    """``ValidationError`` subclasses ``ValueError``, so ``pytest.raises`` alone proves nothing.

    The old failure was a raw pydantic error naming ``server_type`` the caller never chose.
    """
    with pytest.raises(ValueError) as excinfo:
        define_capability(
            server_prefix="weather",
            action="get_forecast",
            name="W",
            description="d",
            risk_level=RiskLevel.READ_ONLY,
        )
    assert type(excinfo.value) is ValueError, (
        f"the refusal is {type(excinfo.value).__name__}, not the SDK's own ValueError — the id "
        "check is being left to pydantic again"
    )
    assert "server_type" not in str(excinfo.value), (
        "the refusal names a server_type the caller never chose, which is the old symptom"
    )


# ── 3. server_type is derived, not defaulted to a deleted server ─────────────


@pytest.mark.parametrize("prefix", _ROSTER_PREFIXES)
def test_default_arguments_build_for_every_roster_prefix(prefix: str) -> None:
    """Used to hold for ``dev`` alone — i.e. only for the server deleted in Phase 9."""
    cap = define_capability(
        server_prefix=prefix,
        action="thing",
        name="Thing",
        description="Built with default arguments only.",
        risk_level=RiskLevel.READ_ONLY,
    )
    assert cap.id == f"{prefix}.thing"
    assert cap.server_type is SERVER_TYPE_BY_PREFIX[prefix]


def test_the_derived_server_type_is_the_one_the_prefix_names() -> None:
    """The summary form of the test above, so the whole mapping is asserted by equality."""
    derived = {
        prefix: SERVER_TYPE_BY_PREFIX[prefix]
        for prefix in _ROSTER_PREFIXES
    }
    assert derived["pc"] is ServerType.PC
    assert derived["pc-server"] is ServerType.PC
    assert derived["room-server"] is ServerType.ROOM
    assert derived["ai"] is ServerType.AI


def test_a_server_type_the_prefix_does_not_name_is_refused() -> None:
    """``server_type`` is still an override, so a contradictory one must be caught, not honoured."""
    with pytest.raises(ValueError) as excinfo:
        define_capability(
            server_prefix="pc",
            action="screenshot",
            name="Screenshot",
            description="Take a screenshot.",
            risk_level=RiskLevel.READ_ONLY,
            server_type=ServerType.ROOM,
        )
    assert "names server_type PC" in str(excinfo.value)


# ── 4. The artefacts that drifted, executed rather than described ────────────


def test_the_docstring_example_builds() -> None:
    """``capability.py``'s own usage example is executed, not eyeballed."""
    source = _docstring_call_source()
    node = ast.parse(source, mode="eval")
    namespace = {"define_capability": define_capability, "RiskLevel": RiskLevel}
    cap = eval(compile(node, "<capability.py docstring>", "eval"), namespace)
    assert re.match(CAPABILITY_ID_PATTERN, cap.id), f"the documented example builds {cap.id!r}"
    assert cap.server_type is SERVER_TYPE_BY_PREFIX[cap.id.split(".")[0]]


def test_the_shipped_example_server_runs_end_to_end() -> None:
    """``examples/example-weather-server`` could not even be imported, and nothing imported it."""
    assert _EXAMPLE.is_file(), f"the shipped example moved or was deleted: {_EXAMPLE}"
    module = _load_module(_EXAMPLE, "_b14_example_server")

    ids = sorted(cap.id for cap in module.ALL_CAPABILITIES)
    assert ids == ["room-server.weather.get_current", "room-server.weather.get_forecast"]

    core = MockAEGISCore()
    server = module.WeatherServer()
    assert server.register(core.registry) is True
    assert core.registry.get_capability("room-server.weather.get_forecast") is not None

    forecast = server.get_forecast("Tokyo")
    assert forecast["temp_c"] == 22.5
    assert server.publish_weather_update(core.event_bus, "tokyo", 22.5) is True


def test_the_scaffold_generates_a_server_that_builds(tmp_path: Path) -> None:
    """Every generated server used to raise at import unless ``--name`` was a roster prefix."""
    scaffold = _load_module(_SCAFFOLD, "_b14_scaffold")
    created = scaffold.create_server_scaffold("weather", "room", 50060, str(tmp_path))
    assert len(created) == 3

    module = _load_module(tmp_path / "weather_server.py", "_b14_generated_server")
    ids = [cap.id for cap in module.ALL_CAPABILITIES]
    assert ids == ["room-server.weather.example"], (
        "the scaffold used the app name as the capability prefix again"
    )

    core = MockAEGISCore()
    assert module.WeatherServer().register(core.registry) is True
    assert core.registry.get_capability("room-server.weather.example") is not None


@pytest.mark.parametrize("server_type", ["room", "room-server", "pc-server", "ai"])
def test_the_scaffold_accepts_every_roster_spelling(server_type: str) -> None:
    """``--type room-server`` must not be upper-cased into the non-existent ``ROOM-SERVER``."""
    scaffold = _load_module(_SCAFFOLD, "_b14_scaffold_spellings")
    prefix, member = scaffold._host_for_type(server_type)
    assert prefix in _ROSTER_PREFIXES
    assert member in {m.name for m in ServerType}


def test_the_scaffold_refuses_a_type_that_is_not_a_server() -> None:
    """Better a refusal than a file that will not import — the old failure mode."""
    scaffold = _load_module(_SCAFFOLD, "_b14_scaffold_refusal")
    with pytest.raises(SystemExit) as excinfo:
        scaffold._host_for_type("weather")
    assert "unknown --type" in str(excinfo.value)


def test_the_documented_scaffold_command_can_actually_run(tmp_path: Path) -> None:
    """The Usage line was a command nobody ran, and it could not run (bug class 11).

    ``create_server.py`` derives the capability prefix from ``aegis_schema.roster``, so the shared
    schema must be importable — but the documented invocation never said so, and the generator
    exits with a ``SystemExit`` explaining the omission. Run the documented invocation in a
    subprocess with the inherited ``PYTHONPATH`` **removed**, so the only thing putting the schema
    on the path is the instruction the docstring itself gives. The instruction is the claim; this
    is the run.

    The argument list is exercised by the scaffold tests above — what this one adds is the
    *environment* the docstring documents.
    """
    docstring = ast.get_docstring(ast.parse(_SCAFFOLD.read_text(encoding="utf-8", newline="")))
    assert docstring, "create_server.py no longer has a module docstring to check"
    documented = re.search(r"PYTHONPATH=(\S+)", docstring)
    assert documented is not None, (
        "the scaffold's Usage line does not say how to make aegis_schema importable, so the "
        "command it documents fails with a SystemExit (B-14 residue)"
    )

    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    env["PYTHONPATH"] = documented.group(1)
    result = subprocess.run(
        [
            sys.executable,
            str(_SCAFFOLD),
            "--name",
            "weather",
            "--type",
            "room",
            "--port",
            "50060",
            "--output",
            str(tmp_path),
        ],
        cwd=_REPO,
        env=env,
        capture_output=True,
        check=False,
    )
    stderr = result.stderr.decode("utf-8", errors="replace")
    assert result.returncode == 0, f"the documented command failed:\n{stderr}"
    assert (tmp_path / "weather_server.py").is_file(), (
        f"the documented command reported success but wrote nothing:\n{stderr}"
    )
