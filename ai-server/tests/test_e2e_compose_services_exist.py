r"""Every service a script asks `docker compose` for must exist, or be recorded here.

Measured 2026-10-03, with the real CLI (`docker compose config`, no daemon needed):

* `docker compose -f docker-compose.yml -f docker-compose.production.yml config --services`
  resolves `ai-server`, `browser-server`, `jaeger`, `temporal`, `temporal-postgresql`
  (`room-server` is behind the `room` profile).
* `... config --profiles` prints **`room`** and nothing else.
* `... --profile dev config --services | grep -c dev-server` -> **0**.

So `scripts/e2e/run-dev-real.ps1:15`'s `--profile dev up -d dev-server` names a service **no compose
file defines** and a profile **no compose file declares**. The dev server was deleted in Phase 9:
`scripts/e2e/run-docker-core.ps1` had its `-IncludeDev` switch removed at the time (its own comment
says so), and `scripts/e2e/run-dev-real.ps1` was **missed by that sweep** — the same shape as the
Dockerfile drift recorded in `test_dockerfiles_are_owned.py`.

The consequence is not hypothetical: `run-dev-real.ps1:19` records the failure into its report and
exits 1, and `run-all-real.ps1:25` runs that step **unconditionally** with `-ManageDocker`, so
`run-all-real.ps1` can never exit 0.

**Scope, and the blind spots it counts rather than hides.** The scan is a static read of
`scripts/**/*.ps1` **and `scripts/**/*.sh`** — the `.sh` half is not optional: `scripts/ubuntu/start.sh`
and `scripts/ubuntu/healthcheck.sh` invoke compose with service operands, so a `.ps1`-only scan reports
a clean tree while **seven** invocations go unread (measured: this pin was written `.ps1`-only first;
widening it changed nothing about the defect, but added 5 service names to the record).

1. A `docker compose ...` occurrence **inside a string literal is a mention, not an invocation** —
   six lines in this tree are exactly that (`throw "docker compose up failed"`,
   `Add-Check "... docker compose restart"` ×3, `throw "docker compose build failed"`, and
   `run-dev-real.ps1:19`'s own evidence string, which quotes `docker compose --profile dev up`).
   Quoted spans become a **placeholder token**, not nothing, so a value flag still eats the value it
   was given instead of the next real operand (`build --build-arg "$REV" ai-server` lost `ai-server`
   when quotes vanished to nothing). A naive substring scan reports six phantom invocations and two
   phantom `dev` profiles.
2. **Splatting and variable operands** carry the argv in variables, so no operand is readable from the
   line: PowerShell `docker @compose up -d @services` (4 lines) and shell
   `docker compose "${COMPOSE_ARGS[@]}" up -d browser-server`. Those tokens are counted and pinned, so
   "only literals are read" is a measurement rather than a promise.
3. **Line continuations** are folded for `.sh` only: `healthcheck.sh` splits one invocation over four
   physical lines, so a line-based read sees `docker compose \` and never reaches `exec -T ai-server`.
   The backtick (PowerShell's marker) is **deliberately not honoured** — it is ambiguous in this tree
   (`start-docker-real.ps1:6` is a comment ending with an inline-code backtick, `build-portable.ps1:30`
   a bare markdown fence) and no `.ps1` compose invocation here spans lines. A future one would surface
   as an unrecorded subcommand rather than as a silent miss.

Recorded, not deleted — the owner call is `DELEGATION.md` §4 item 17 (2).

**Why `scripts/` is the whole surface, not just a convenient directory.** Measured 2026-10-03 by
walking every non-vendored file (`scripts/`, `infra/`, `.github/`, any `Makefile`) for a compose
command: **all 29 invocation lines live under `scripts/`** and there is no CI workflow, Makefile or
infra script that invokes compose. So the directory is the surface, and a future invocation outside it
is the one thing this pin cannot see — recorded here rather than left implied.
"""

from __future__ import annotations

import collections
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import NamedTuple

import yaml

_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"

_SKIP_DIRS = frozenset({".git", ".venv", "node_modules", "__pycache__", ".workbuddy-ai"})

# A script may name a service that no compose file defines only if it is recorded here.
# Measured 2026-10-03 — dev-server was deleted in Phase 9; this caller was missed.
_RECORDED_UNRESOLVABLE_SERVICES: frozenset[tuple[str, str]] = frozenset(
    {
        ("scripts/e2e/run-dev-real.ps1", "dev-server"),
    }
)

# Likewise for profiles: `--profile dev` names a profile no compose file declares.
_RECORDED_UNDECLARED_PROFILES: frozenset[tuple[str, str]] = frozenset(
    {
        ("scripts/e2e/run-dev-real.ps1", "dev"),
    }
)

# Subcommands observed in this tree (measured, not guessed) — an equality, so a new subcommand
# forces a decision about whether it takes service operands instead of silently joining a bucket.
_RECORDED_SUBCOMMANDS: frozenset[str] = frozenset(
    {"build", "config", "cp", "exec", "logs", "ps", "restart", "stop", "up", "version"}
)

# How many times each service name was extracted, across every invocation (measured 2026-10-03,
# across both the `.ps1` and the `.sh` halves). An equality rather than a floor, because a floor
# cannot see the reader losing one *valid* name: dropping the `)` terminator alone silently lost
# `ai-server` three times (the `ps -q ai-server)` shape) while every other assertion here stayed green.
_RECORDED_SERVICE_MULTISET: dict[str, int] = {
    "ai-server": 19,
    "browser-server": 7,
    "dev-server": 2,
    "room-server": 5,
}

# The `.sh` half alone, as a positive control: if the file walk regresses to `.ps1`-only these seven
# invocations vanish and nothing else in this file notices.
_RECORDED_SH_INVOCATIONS = 7

# Subcommands whose bare operands are all service names (`up -d a b c`).
_MULTI_SERVICE_SUBS = frozenset(
    {"up", "build", "pull", "create", "start", "stop", "restart", "kill", "rm", "logs", "ps", "top", "wait"}
)

# Subcommands whose *first* bare operand is the service and whose remaining operands are a command
# line (`exec -T ai-server python /tmp/probe.py`), so only the first may be read as a service.
_FIRST_OPERAND_SUBS = frozenset({"exec", "run", "cp", "port"})

# Flags that consume the following token, so it must not be read as a subcommand or a service.
# `--profile` MUST be in here as well as in `_PROFILE_FLAGS`: membership here is what eats the
# value, and dropping it made `dev` fall through to the subcommand position (measured: the whole
# invocation then read as `sub='dev'` with no services at all).
_VALUE_FLAGS = frozenset(
    {
        "-f", "--file", "-p", "--project-name", "--env-file", "--ansi", "--progress",
        "--project-directory", "-c", "--context", "--log-level", "--profile", "--build-arg",
        "--env", "-e", "--label", "-l", "--scale", "--index", "--user", "-u", "--workdir", "-w",
    }
)

# Of those, only `--profile` *declares* a profile. `-p` is `--project-name` — a different axis, and
# recording it as a profile reports a project name as an undeclared profile.
_PROFILE_FLAGS = frozenset({"--profile"})

# What a quoted span becomes. It must be a *token* (so a value flag can still eat it and not swallow
# the next real operand — `build --build-arg "$X" ai-server` lost `ai-server` when quotes vanished
# to nothing) yet must not look like a service or a subcommand.
_QUOTED = "\x01"
_QUOTED_LABEL = "<quoted>"

_LITERAL = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_INVOCATION = re.compile(r"\bdocker\s+(compose|@[A-Za-z_][A-Za-z0-9_]*)")

# The v1 spelling. This tree does not use it, so it is pinned as *absent* rather than supported
# blind: an untested branch is not coverage.
_V1_COMMAND = re.compile(r"(^|\s)docker-compose\s")

# An invocation's argv ends at a pipeline, a statement separator, a closing brace or a closing
# paren: `... up -d dev-server | Out-Null`, `try { ... } finally { Pop-Location }` and
# `(docker compose ps -q ai-server)` must not contribute `Out-Null`, `finally`, `Pop-Location` or
# `ai-server)` as service names.
_ARGV_END = re.compile(r"[|;})]")

# Line continuations, per language. A shell uses a trailing `\`; PowerShell uses a trailing backtick
# — and the backtick is **ambiguous** in this tree: `start-docker-real.ps1:6` is a comment ending
# with an inline-code backtick (``passed to `docker compose build/up` ``) and `build-portable.ps1:30`
# is a bare markdown fence, both of which a naive "ends with a backtick" test joins across. Measured:
# **no `.ps1` compose invocation here spans lines** (the four that do are all in `.sh`), so `.ps1`
# is deliberately not joined — and a future multi-line `.ps1` invocation surfaces as an *unrecorded
# subcommand* rather than as a silent miss.
_CONTINUATION = {".sh": "\\"}

_SCRIPT_SUFFIXES = (".ps1", ".sh")


class _Invocation(NamedTuple):
    script: str
    line: int
    sub: str
    profiles: tuple[str, ...]
    services: tuple[str, ...]
    splat: bool
    skipped: tuple[str, ...]


def _rel(path: Path) -> str:
    return path.resolve().relative_to(_REPO).as_posix()


@lru_cache(maxsize=1)
def _script_files() -> tuple[Path, ...]:
    """Every `.ps1` and `.sh` under `scripts/`, minus the skipped trees.

    The `.sh` half is not optional: `scripts/ubuntu/start.sh` and `scripts/ubuntu/healthcheck.sh`
    both invoke `docker compose` with service operands, and a `.ps1`-only scan would report a clean
    tree while seven more invocations went unread.
    """
    out: list[Path] = []
    for root, dirs, files in os.walk(_SCRIPTS):
        dirs[:] = sorted(d for d in dirs if d not in _SKIP_DIRS)
        out.extend(
            Path(root) / name for name in sorted(files) if name.endswith(_SCRIPT_SUFFIXES)
        )
    return tuple(out)


def _logical_lines(path: Path) -> list[tuple[int, str]]:
    """(first physical line number, joined text) — line continuations folded in.

    A trailing `\\` (sh) or backtick (PowerShell) joins the next physical line. Without this,
    `healthcheck.sh`'s four-line `docker compose \\ / -f … / exec -T ai-server` yields a bogus
    subcommand (`\\`) and loses the service.
    """
    marker = _CONTINUATION.get(path.suffix)
    if marker is None:
        text = path.read_text(encoding="utf-8", errors="replace")
        return list(enumerate(text.splitlines(), 1))
    out: list[tuple[int, str]] = []
    buffer = ""
    start = 0
    for lineno, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not buffer:
            start = lineno
        if raw.rstrip().endswith(marker):
            buffer += raw.rstrip()[: -len(marker)] + " "
            continue
        out.append((start, buffer + raw))
        buffer = ""
    if buffer:
        out.append((start, buffer))
    return out


def _strip_quoted(line: str) -> str:
    """Replace single- and double-quoted spans with a placeholder token.

    Both languages have no escape worth modelling here: every string in this tree is on one line and
    unescaped. The replacement is a **token**, not nothing — see `_QUOTED`.
    """
    return re.sub(r"'[^']*'|\"[^\"]*\"", f" {_QUOTED} ", line)


def _strip_comment(line: str) -> str:
    """Drop a trailing `#` comment; the caller has already removed quoted spans."""
    return line.split("#", 1)[0]


@lru_cache(maxsize=1)
def _invocations() -> tuple[_Invocation, ...]:
    found: list[_Invocation] = []
    for path in _script_files():
        for lineno, raw in _logical_lines(path):
            line = _strip_comment(_strip_quoted(raw))
            match = _INVOCATION.search(line)
            if not match:
                continue
            rel = _rel(path)
            if match.group(1) != "compose":
                found.append(_Invocation(rel, lineno, "", (), (), True, ()))
                continue

            tokens = _ARGV_END.split(line[match.end():], 1)[0].split()
            profiles: list[str] = []
            services: list[str] = []
            skipped: list[str] = []
            sub = ""
            index = 0
            while index < len(tokens):
                token = tokens[index]
                if token in _VALUE_FLAGS:
                    if token in _PROFILE_FLAGS and index + 1 < len(tokens):
                        profiles.append(tokens[index + 1])
                    index += 2
                    continue
                if token.startswith("-"):
                    index += 1
                    continue
                if not sub:
                    if token != _QUOTED:
                        sub = token
                elif sub in _MULTI_SERVICE_SUBS or sub in _FIRST_OPERAND_SUBS:
                    if _LITERAL.match(token):
                        services.append(token)
                    else:
                        skipped.append(_QUOTED_LABEL if token == _QUOTED else token)
                    if sub in _FIRST_OPERAND_SUBS:
                        index = len(tokens)  # the rest is a command line, not services
                        continue
                index += 1
            found.append(_Invocation(rel, lineno, sub, tuple(profiles), tuple(services), False, tuple(skipped)))
    return tuple(found)


@lru_cache(maxsize=1)
def _compose_definition() -> tuple[frozenset[str], frozenset[str]]:
    """(service names, profile names) declared by the shipped compose files.

    `docker-compose.yml.archive` is excluded **structurally** — its suffix is `.archive`, not
    `.yml`/`.yaml` — because it is a frozen rollback artefact that still names the deleted
    `dev-server`. Same rule as `test_dockerfiles_are_owned.py`, so the archive needs no entry on
    any exclusion list.
    """
    services: set[str] = set()
    profiles: set[str] = set()
    for path in sorted(_REPO.glob("docker-compose*")):
        if path.suffix not in {".yml", ".yaml"}:
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for name, service in (data.get("services") or {}).items():
            services.add(name)
            for profile in (service or {}).get("profiles") or []:
                profiles.add(str(profile))
    return frozenset(services), frozenset(profiles)


def _observed_unresolvable() -> set[tuple[str, str]]:
    defined, _ = _compose_definition()
    return {
        (entry.script, service)
        for entry in _invocations()
        for service in entry.services
        if service not in defined
    }


def _observed_undeclared_profiles() -> set[tuple[str, str]]:
    _, declared = _compose_definition()
    return {
        (entry.script, profile)
        for entry in _invocations()
        for profile in entry.profiles
        if profile not in declared
    }


def test_the_scan_reaches_the_script_tree() -> None:
    """Non-vacuity floors on the quantities the reader walks, never on the sets it compares."""
    scripts = _script_files()
    invocations = _invocations()
    literals = [service for entry in invocations for service in entry.services]
    assert len(scripts) >= 30, (
        f"walked only {len(scripts)} .ps1/.sh files under scripts/ — the scan is not reading the "
        "tree, so every equality below would pass vacuously"
    )
    assert len(invocations) >= 20, (
        f"found only {len(invocations)} `docker ...` invocation lines in {len(scripts)} scripts — "
        "the extractor is blind"
    )
    assert len(literals) >= 20, (
        f"extracted only {len(literals)} literal service names — the operand reader is blind"
    )
    shell = [entry for entry in invocations if entry.script.endswith(".sh")]
    assert len(shell) == _RECORDED_SH_INVOCATIONS, (
        f"read {len(shell)} invocations from the .sh half, expected {_RECORDED_SH_INVOCATIONS}.\n"
        "If the walk regressed to .ps1-only, the tree looks clean while `scripts/ubuntu/start.sh` "
        "and `healthcheck.sh` go unread; if a shell script genuinely gained or lost one, update the "
        "record. A `.ps1`-only scan is exactly the defect this pin was written against."
    )
    subcommands = {entry.sub for entry in invocations if not entry.splat}
    assert subcommands == _RECORDED_SUBCOMMANDS, (
        "the set of compose subcommands used by the scripts changed, so the bucket each operand "
        "falls into is no longer known.\n"
        f"  new: {sorted(subcommands - _RECORDED_SUBCOMMANDS)}\n"
        f"  gone: {sorted(_RECORDED_SUBCOMMANDS - subcommands)}\n"
        "Decide whether the new subcommand takes service operands, teach the extractor, and record "
        "it here — do not leave it unclassified, because an unclassified operand is silently "
        "treated as a service."
    )
    # Positive controls for the two counted blind spots: both forms are *present* in this tree, so
    # recording them is a measurement rather than an assumption about code that may not exist.
    assert [entry for entry in invocations if entry.splat], (
        "no `docker @var` splat line found — the recorded blind spot would be fictional"
    )
    assert [entry for entry in invocations if entry.skipped], (
        "no non-literal operand found — the recorded blind spot would be fictional"
    )


def test_the_extracted_service_names_match_the_recorded_multiset() -> None:
    """Fix the reader's own yield, so a blinded reader cannot pass as a clean tree."""
    observed = collections.Counter(service for entry in _invocations() for service in entry.services)
    assert dict(observed) == _RECORDED_SERVICE_MULTISET, (
        "the multiset of service names the extractor reads changed. If a script genuinely gained or "
        "lost an invocation, update the record; if not, the reader was blinded.\n"
        f"  newly read: {sorted((observed - collections.Counter(_RECORDED_SERVICE_MULTISET)).items())}\n"
        f"  no longer read: "
        f"{sorted((collections.Counter(_RECORDED_SERVICE_MULTISET) - observed).items())}\n"
        "This is an equality rather than a floor on purpose: losing a *valid* name (`ai-server`, "
        "three times, from the `(docker compose ps -q ai-server)` shape) leaves every other "
        "assertion in this file green."
    )


def test_the_v1_command_spelling_is_absent() -> None:
    """`docker-compose` (v1) is not supported — it is pinned as *absent*, not read blind.

    An untested branch is not coverage, so rather than teach the extractor a spelling this tree never
    uses, fix the fact: if someone introduces it, this fails and forces the decision.
    """
    users = sorted(
        f"{_rel(path)}:{lineno}"
        for path in _script_files()
        for lineno, raw in _logical_lines(path)
        if _V1_COMMAND.search(_strip_comment(_strip_quoted(raw)))
    )
    assert users == [], (
        f"`docker-compose` (v1) is now invoked as a command in {users}.\n"
        "The extractor reads `docker compose` (v2) only. Teach it the v1 spelling and record the "
        "subcommands it introduces — do not leave it unread, because a v1 invocation names services "
        "the same way and would be invisible to every other assertion in this file."
    )


def test_every_named_service_is_defined_by_a_compose_file() -> None:
    defined, _ = _compose_definition()
    assert len(defined) >= 5, (
        f"parsed only {len(defined)} services from the compose files — the loader is not reading them"
    )
    observed = _observed_unresolvable()
    assert observed == _RECORDED_UNRESOLVABLE_SERVICES, (
        "the set of services named by a script but defined by no compose file changed.\n"
        "  newly unresolvable (compose fails with `no such service`, the script always exits 1): "
        f"{sorted(observed - _RECORDED_UNRESOLVABLE_SERVICES)}\n"
        "  no longer unresolvable (fixed or deleted): "
        f"{sorted(_RECORDED_UNRESOLVABLE_SERVICES - observed)}\n"
        "Either define the service in a compose file, stop naming it, or record it above with the "
        "reason. A service that no compose file defines cannot be started by any profile flag."
    )


def test_every_named_profile_is_declared() -> None:
    _, declared = _compose_definition()
    assert declared, "no profiles parsed from the compose files — the loader is not reading them"
    observed = _observed_undeclared_profiles()
    assert observed == _RECORDED_UNDECLARED_PROFILES, (
        "the set of profiles a script passes but no compose file declares changed.\n"
        f"  newly undeclared: {sorted(observed - _RECORDED_UNDECLARED_PROFILES)}\n"
        f"  no longer undeclared: {sorted(_RECORDED_UNDECLARED_PROFILES - observed)}\n"
        "`--profile X` with no matching service is a no-op at best; when the operand is a service "
        "that also does not exist, the invocation can only fail."
    )


def test_the_recorded_residue_is_still_wired_into_the_orchestrator() -> None:
    """Pin both ends: the dead step must not become an orphan, nor silently disappear."""
    target = "scripts/e2e/run-dev-real.ps1"
    callers: set[str] = set()
    for path in _script_files():
        if _rel(path) == target:
            continue
        if re.search(r"run-dev-real\.ps1", path.read_text(encoding="utf-8", errors="replace")):
            callers.add(_rel(path))
    assert callers == {"scripts/e2e/run-all-real.ps1"}, (
        "the caller set of the one script with an unresolvable compose service changed.\n"
        f"  observed: {sorted(callers)}\n"
        "If the step was removed (the recorded remedy), update `_RECORDED_UNRESOLVABLE_SERVICES` "
        "and this set together — deleting the script while this pin still names it, or deleting the "
        "call while the script stays, both leave a half-done change."
    )
    orchestrator = (_SCRIPTS / "e2e" / "run-all-real.ps1").read_text(encoding="utf-8")
    assert re.search(r'"dev"\s+"scripts/e2e/run-dev-real\.ps1"[^\n]*-ManageDocker', orchestrator), (
        "run-all-real.ps1 no longer passes -ManageDocker to the dev step. That flag is what makes "
        "the step reach the compose invocation this pin measures; without it the step fails for a "
        "different reason and the recorded defect above would be unreachable, i.e. already dead."
    )
