"""The compose files must be internally coherent — and the coherence is checkable without Docker.

Measured 2026-10-03 with the real CLI (Docker 29.7.2 / Compose v5.5.0):

* `docker compose -f docker-compose.yml config --quiet` → **rc=0**.
* `docker compose -f docker-compose.yml -f docker-compose.production.yml config --quiet` → **rc=1**,
  failing with ``required variable AEGIS_SESSION_SECRET is missing a value`` — the production overlay
  deliberately has **no default** for the session secret (``${AEGIS_SESSION_SECRET:?...}``), so an
  unconfigured production start dies at parse time instead of booting with an empty secret.
* the same command **with** the variable set → **rc=0**.
* services: base **6**, production **5** (``room-server`` carries ``profiles: [room]``), production
  with ``--profile room`` **6**.

The pin below does **not** shell out to `docker`: CI runs pytest on a host with no daemon, and the
project's rule is not to pin a check that needs a tool CI lacks. Everything asserted here is a
property of the **text** of the compose files and the Dockerfiles they name, so it is deterministic
and free. What the CLI run above adds is the interpolation pass; the one interpolation fact worth
pinning (the secret has no default) is asserted directly on the source.

The point is the **multi-service** half that `test_dockerfiles_are_owned.py` does not cover: that file
checks every Dockerfile is referenced or recorded. This one checks that the references actually
*compose* — that no service depends on a name nobody defines, that no port is claimed twice, that the
volume set is exactly used, and that the two places the production overlay expresses "no room server"
agree with each other.
"""

from __future__ import annotations

import json
import posixpath
import re
from pathlib import Path
from typing import Any

import yaml

_REPO = Path(__file__).resolve().parents[2]

_BASE = _REPO / "docker-compose.yml"
_PROD = _REPO / "docker-compose.production.yml"

#: The three services compose builds from source; the other three are third-party images.
_BUILT_SERVICES = frozenset({"ai-server", "browser-server", "room-server"})
#: Images compose pulls rather than builds — their environment keys are *their* configuration.
_FOREIGN_SERVICES = frozenset({"jaeger", "temporal", "temporal-postgresql"})

_INTERPOLATION = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::([-?])([^{}]*))?\}")


class _RequiredVariableMissing(Exception):
    """Raised for ``${VAR:?message}`` when ``VAR`` is unset — compose's own fail-fast form."""


def _load(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _services(path: Path) -> dict[str, Any]:
    return _load(path).get("services") or {}


def _interpolate(text: str, env: dict[str, str]) -> str:
    """Resolve compose's ``${VAR}`` / ``${VAR:-default}`` / ``${VAR:?message}`` forms.

    Iterated so nested defaults (``${A:-${B:-c}}``) resolve inside-out. ``env`` is passed explicitly
    rather than read from ``os.environ``: the assertion must not change with the operator's shell.
    """
    previous = None
    while previous != text:
        previous = text

        def _replace(match: re.Match[str]) -> str:
            name, op, argument = match.group(1), match.group(2), match.group(3)
            if env.get(name):
                return env[name]
            if op == "-":
                return argument
            if op == "?":
                raise _RequiredVariableMissing(argument)
            return ""

        text = _INTERPOLATION.sub(_replace, text)

    return text


def _host_port(spec: str, env: dict[str, str] | None = None) -> str:
    """The host-side port of a compose ``ports`` entry, after interpolation."""
    resolved = _interpolate(spec, env or {})
    parts = resolved.split(":")
    return parts[-2] if len(parts) >= 2 else parts[0]


def test_the_compose_files_are_the_ones_we_think_they_are() -> None:
    """Non-vacuity: every assertion below reads these two files, so they must exist and parse."""
    for path in (_BASE, _PROD):
        assert path.is_file(), f"{path.name} is missing — the scan below would pass vacuously"
    assert set(_services(_BASE)) == _BUILT_SERVICES | _FOREIGN_SERVICES, (
        "the base compose's service set changed; the other tests name services by hand:\n"
        f"  observed {sorted(_services(_BASE))}\n"
        f"  expected {sorted(_BUILT_SERVICES | _FOREIGN_SERVICES)}"
    )


def test_every_depends_on_target_is_a_declared_service() -> None:
    """A `depends_on` naming an undefined service is a parse error at `compose up`, not a warning."""
    for path in (_BASE, _PROD):
        services = _services(path)
        dangling = [
            f"{path.name}: {name} -> {target}"
            for name, service in services.items()
            for target in ((service or {}).get("depends_on") or {})
            if target not in services
        ]
        assert not dangling, (
            "a service depends on a name no compose file defines — `docker compose up` fails on "
            "this before any container starts:\n  " + "\n  ".join(dangling)
        )

    edges = sum(
        len((service or {}).get("depends_on") or {}) for service in _services(_BASE).values()
    )
    assert edges >= 2, f"only {edges} depends_on edges found — the scan is not reading the file"


def test_named_volumes_are_declared_and_every_declared_volume_is_used() -> None:
    """Equality in **both** directions: a used-but-undeclared volume is an error, an unused one is debt."""
    declared = set((_load(_BASE).get("volumes") or {}).keys())
    assert declared, "the base compose declares no volumes — the scan is not reading the file"

    used: set[str] = set()
    for name, service in _services(_BASE).items():
        for volume in (service or {}).get("volumes", []):
            if isinstance(volume, dict):
                source, kind = volume.get("source", ""), volume.get("type", "volume")
            else:
                source = volume.split(":")[0]
                kind = "bind" if source.startswith((".", "/")) else "volume"
            if kind == "volume":
                used.add(source)

    assert used == declared, (
        "the named-volume set is no longer exactly what the services mount.\n"
        f"  used but not declared (a `compose up` error): {sorted(used - declared)}\n"
        f"  declared but never used (dead volume): {sorted(declared - used)}"
    )


def test_published_host_ports_are_distinct() -> None:
    """Two services publishing the same host port is a runtime bind failure, not a config warning."""
    claimed: dict[str, list[str]] = {}
    for name, service in _services(_BASE).items():
        for spec in (service or {}).get("ports", []):
            claimed.setdefault(_host_port(str(spec)), []).append(name)

    assert len(claimed) >= 5, (
        f"only {len(claimed)} published host ports found — the scan is not reading the file"
    )
    collisions = {port: names for port, names in claimed.items() if len(names) > 1}
    assert not collisions, (
        "two services claim the same host port; whichever starts second fails to bind:\n  "
        + "\n  ".join(f"{port}: {names}" for port, names in sorted(collisions.items()))
    )


def test_the_production_overlay_refuses_to_default_the_session_secret() -> None:
    """`${VAR:-…}` here would boot production with a predictable secret; only `:?` is acceptable.

    Measured 2026-10-03: the CLI confirms the difference — the overlay without the variable exits
    **rc=1** at interpolation, and **rc=0** once it is supplied.
    """
    environment = _services(_PROD)["ai-server"]["environment"]
    secret = environment["AEGIS_SESSION_SECRET"]

    assert ":?" in secret, (
        f"the production overlay sets AEGIS_SESSION_SECRET to {secret!r}; without the `:?` fail-fast "
        "an unconfigured production start boots with an empty session secret"
    )
    try:
        _interpolate(secret, {})
    except _RequiredVariableMissing:
        pass
    else:
        raise AssertionError(
            f"{secret!r} did not fail when the variable is unset — the fail-fast is inert"
        )

    assert _interpolate(secret, {"AEGIS_SESSION_SECRET": "s"}) == "s", (
        "the fail-fast form must still resolve when the variable *is* supplied"
    )


def test_room_server_is_profiled_and_disabled_together() -> None:
    """Two independent mechanisms express "no room server in production" — they must agree.

    `profiles: [room]` keeps the service out of a default `compose up`; `AEGIS_DISABLED_SERVERS`
    tells ai-server not to look for it. Either alone is a half-measure, and a drift between them
    (profile renamed, default changed) is invisible until deployment.
    """
    base_room = _services(_BASE)["room-server"]
    prod_room = _services(_PROD)["room-server"]

    assert not base_room.get("profiles"), (
        f"the base compose now profiles room-server ({base_room.get('profiles')}); the base file is "
        "meant to run everything, and the production overlay is where it is dropped"
    )
    assert prod_room.get("profiles") == ["room"], (
        f"the production overlay profiles room-server as {prod_room.get('profiles')!r}; expected "
        "['room'] — without it, production starts the room server"
    )

    disabled = _services(_PROD)["ai-server"]["environment"]["AEGIS_DISABLED_SERVERS"]
    resolved = _interpolate(disabled, {})
    assert resolved == "room-server", (
        f"AEGIS_DISABLED_SERVERS defaults to {resolved!r} while the profile keeps room-server out "
        "of a default start — the two halves of 'no room server' disagree"
    )


def test_the_web_ui_copy_source_matches_the_npm_out_dir() -> None:
    """The build stage's `COPY --from` path is derived, not guessed — assert the two agree.

    A `COPY --from=<stage> /ai-server/...` in a stage whose WORKDIR is `/web-ui` looks wrong, and
    was measured 2026-10-03 rather than assumed: `web-ui/package.json` builds with
    ``--outDir ../ai-server/src/aegis_ai/web/static/ui-v2``, which from `/web-ui` resolves to exactly
    the path the Dockerfile copies. Change one side and the image build breaks with a missing-file
    error, so the pair is pinned together.
    """
    dockerfile = (_REPO / "infra/docker/ai-server.Dockerfile").read_text(encoding="utf-8")

    stage_workdirs: dict[str, str] = {}
    current: str | None = None
    for line in dockerfile.splitlines():
        from_match = re.match(r"\s*FROM\s+\S+\s+AS\s+(\S+)", line)
        if from_match:
            current = from_match.group(1)
            continue
        workdir_match = re.match(r"\s*WORKDIR\s+(\S+)", line)
        if workdir_match and current:
            stage_workdirs[current] = workdir_match.group(1)

    copies = re.findall(r"COPY\s+--from=(\S+)\s+(\S+)\s+(\S+)", dockerfile)
    assert copies, "the ai-server Dockerfile no longer copies from a build stage"

    build_script = json.loads((_REPO / "web-ui/package.json").read_text(encoding="utf-8"))["scripts"][
        "build"
    ]
    out_dir_match = re.search(r"--outDir\s+(\S+)", build_script)
    assert out_dir_match, f"the web-ui build script no longer passes --outDir: {build_script!r}"

    stage, source, _target = copies[0]
    assert stage in stage_workdirs, (
        f"COPY --from={stage} names a stage the Dockerfile never defines; defined: "
        f"{sorted(stage_workdirs)}"
    )
    resolved = posixpath.normpath(posixpath.join(stage_workdirs[stage], out_dir_match.group(1)))
    assert source == resolved, (
        "the Dockerfile copies the web-ui build from a different path than npm writes it to.\n"
        f"  COPY --from={stage} {source}\n"
        f"  npm --outDir, from WORKDIR {stage_workdirs[stage]}: {resolved}\n"
        "One of the two moved; the image build now fails with a missing source path."
    )


def _declares_healthcheck(text: str) -> bool:
    """Whether a Dockerfile really *declares* a healthcheck.

    A substring search is not enough: the mutation that replaces the instruction with
    ``# HEALTHCHECK removed`` still contains the word, so it would pass — "a mention is not an
    invocation", the same defect this pin exists to catch. `HEALTHCHECK NONE` is a declaration that
    there is **no** healthcheck, so it does not count either.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("HEALTHCHECK") and not stripped.upper().startswith("HEALTHCHECK NONE"):
            return True
    return False


def test_the_healthcheck_gap_is_recorded() -> None:
    """Every built image defines a HEALTHCHECK and **nothing gates on it** — recorded, not assumed.

    Measured 2026-10-03: all three referenced Dockerfiles declare one, and neither compose file
    declares a `healthcheck:` at all, so every `depends_on` uses `condition: service_started` —
    "the process started", not "the process is healthy". Gating on `service_healthy` is a behaviour
    change (a decision, `DELEGATION.md` §4), so this pin records the current shape and will fail the
    moment it changes, which is the point.
    """
    for path in (_BASE, _PROD):
        declared = sorted(
            name for name, service in _services(path).items() if (service or {}).get("healthcheck")
        )
        assert declared == [], (
            f"{path.name} now declares a healthcheck for {declared}. If that is the intended change, "
            "update this pin and the §4 record together — the gate and the record must not drift."
        )

    conditions = {
        condition.get("condition", "service_started")
        for service in _services(_BASE).values()
        for condition in ((service or {}).get("depends_on") or {}).values()
    }
    assert conditions == {"service_started"}, (
        f"depends_on conditions are now {sorted(conditions)}; the record below assumes none of them "
        "waits for health"
    )

    with_healthcheck = {
        rel
        for rel in ("infra/docker/ai-server.Dockerfile", "infra/docker/browser-server.Dockerfile",
                    "infra/docker/room-server.Dockerfile")
        if _declares_healthcheck((_REPO / rel).read_text(encoding="utf-8"))
    }
    assert with_healthcheck == {
        "infra/docker/ai-server.Dockerfile",
        "infra/docker/browser-server.Dockerfile",
        "infra/docker/room-server.Dockerfile",
    }, (
        "the healthchecks the gap is *about* are gone — this pin would otherwise pass because "
        f"nothing defines one anywhere: {sorted(with_healthcheck)}"
    )
