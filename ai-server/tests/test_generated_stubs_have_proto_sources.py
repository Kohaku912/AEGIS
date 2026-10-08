"""The wire-contract chain has three links; only the middle one is unchecked.

`protos/aegis/` is the declared **single source of truth** for the shared service contract
(`docs/architecture.md`: "the `protos/aegis/` directory is the single source of truth"), and
`scripts/generate_protos.{sh,ps1}` is the only thing that turns it into the `*_pb2*.py` stubs the
servers actually import. So the chain is `.proto` -> generated stubs -> runtime, and measured
2026-10-01:

* **`.proto` -> models is pinned; `.proto` -> stubs is not.**
  `tests/test_schema_mirrors_the_protobuf_schema.py` reads the `.proto` **text** and compares it to
  the pydantic models. Nothing compared the `.proto` to the generated stubs — the artefacts the
  servers import.
* **One orphan exists.** `ai-server/src/generated/aegis/dev_server_pb2.pyi` is a generated stub whose
  source `protos/aegis/dev_server.proto` was deleted with the Dev Server. Nothing under
  `ai-server/src/` references it: the only assertion about it lived in
  `tests/agents/test_tool_bridges.py`, which pinned that the bridges must **not** reference it.
  That module and the `tools/bridges/` package it tested were deleted 2026-10-08 (`DELEGATION.md`
  §4 item 53), so the stub is now referenced by no module under `src/` at all — only by prose and by
  `scripts/e2e/dev-real-probe.py`. It is recorded below rather than deleted — removal is an owner
  call (`DELEGATION.md` §4 item 19).
* **The generator's own `[3/3] Verification` step cannot detect any of this.** It counts `*_pb2*.py`
  files and passes when the count is non-zero (`scripts/generate_protos.sh`), which is equally true
  of stale, orphaned and correct stubs. Both defects above existed while it printed a checkmark.
* **Three protos are duplicated into the Android module** — `android-server/app/src/main/proto/aegis/`
  carries its own `ai_server.proto`, `android_server.proto` and `common.proto`, which Gradle compiles
  for the Kotlin client. They agree **today** (byte-identical, measured 2026-10-01), but nothing
  asserted it, so the canonical contract and the client's copy could drift apart silently and only
  fail at runtime. Both directions are pinned here.
* **The room server must not receive stubs it does not import.** The script narrows its set
  deliberately — compiling the full set "dropped ai_server/android_server stubs into the room server,
  which uses neither" — so the narrowing is pinned too, or it can silently regress.

**What this file deliberately does not do: regenerate the stubs and compare bytes.** That needs
`grpcio-tools`, which is a declared dev dependency of `ai-server` but is **absent from CI's `.venv`**
(measured 2026-10-01), so such a check would skip in exactly the place it is needed and would add an
environment-dependent skip to a count the register records as a single number. The staleness half is
recorded instead (`DELEGATION.md` §4 item 19). It is not hypothetical: regenerating on 2026-10-01
showed `ai_server_pb2_grpc.py` was **not** reproducible — three `═`+newline pairs had become `╁E`
inside a docstring, which is invisible at runtime and therefore survived. Running the project's own
script repaired it, and the current script reproduces cleanly, so that corruption was historical.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_PROTO_DIR = _REPO / "protos" / "aegis"
_AI_GENERATED = _REPO / "ai-server" / "src" / "generated" / "aegis"
_ROOM_GENERATED = _REPO / "room-server" / "src" / "generated" / "aegis"
_ANDROID_PROTO_DIR = _REPO / "android-server" / "app" / "src" / "main" / "proto" / "aegis"

# Generated stubs whose `.proto` source no longer exists. `dev_server.proto` was deleted with the
# Dev Server; the generated `.pyi` was left behind. Recorded, not deleted — DELEGATION.md §4 item 19.
_RECORDED_ORPHANS: frozenset[str] = frozenset({"dev_server_pb2.pyi"})

# `scripts/generate_protos.sh` -> ROOM_SERVER_PROTOS. Narrowed on purpose: a server must not receive
# stubs it does not import.
_RECORDED_ROOM_PROTOS: frozenset[str] = frozenset({"common", "room_server"})

# The Android module keeps its own compilable copy of the shared contract (Gradle builds it).
_RECORDED_ANDROID_PROTOS: frozenset[str] = frozenset(
    {"ai_server.proto", "android_server.proto", "common.proto"}
)

_MIN_GENERATED = 12
_MIN_PROTOS = 4
_MIN_ROOM_GENERATED = 4

_SUFFIXES = ("_pb2.py", "_pb2.pyi", "_pb2_grpc.py")


def _generated_files(directory: Path) -> tuple[Path, ...]:
    """`*_pb2.py`, `*_pb2.pyi`, `*_pb2_grpc.py` — never a name that merely contains `_pb2`."""
    return tuple(sorted(path for path in directory.glob("*_pb2*") if path.is_file()))


def _stem(path: Path) -> str:
    """`ai_server_pb2_grpc.py` -> `ai_server`; `common_pb2.pyi` -> `common`."""
    for suffix in _SUFFIXES:
        if path.name.endswith(suffix):
            return path.name[: -len(suffix)]
    raise AssertionError(f"{path.name!r} is not a generated stub name")


def _proto_stems() -> frozenset[str]:
    return frozenset(path.stem for path in _PROTO_DIR.glob("*.proto"))


def _read(path: Path) -> str:
    """Read as text with line endings normalised.

    `protos/aegis/common.proto` is checked out with CRLF while `git ls-files --eol` reports the
    index as LF (`.gitattributes` sets `text=auto` for protos, `eol=lf` for tests), so a byte
    comparison would report a difference that `git` itself does not have.
    """
    return path.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


@lru_cache(maxsize=1)
def _android_proto_names() -> frozenset[str]:
    return frozenset(path.name for path in _ANDROID_PROTO_DIR.glob("*.proto"))


def test_every_generated_stub_has_a_proto_source() -> None:
    """A generated stub with no `.proto` is residue of a deleted contract."""
    generated = _generated_files(_AI_GENERATED)
    assert len(generated) >= _MIN_GENERATED, (
        f"found only {len(generated)} generated stubs under {_AI_GENERATED} — the scan is not "
        "reading the tree, so the orphan assertion below would pass vacuously"
    )
    protos = _proto_stems()
    assert len(protos) >= _MIN_PROTOS, f"found only {len(protos)} protos under {_PROTO_DIR}"

    orphans = frozenset(path.name for path in generated if _stem(path) not in protos)
    assert orphans == _RECORDED_ORPHANS, (
        "the set of generated stubs with no `.proto` source changed.\n"
        f"  recorded: {sorted(_RECORDED_ORPHANS)}\n"
        f"  observed: {sorted(orphans)}\n"
        "A new orphan means a `.proto` was deleted or renamed without regenerating — delete the "
        "stub too, or record it here with its reason. A *missing* recorded orphan means it was "
        "cleaned up, so drop it from the record."
    )


def test_every_proto_is_generated_into_the_ai_server() -> None:
    """The servers import the stubs, not the protos: a proto with no stub is unusable."""
    protos = _proto_stems()
    assert len(protos) >= _MIN_PROTOS, f"found only {len(protos)} protos under {_PROTO_DIR}"

    generated = frozenset(_stem(path) for path in _generated_files(_AI_GENERATED))
    assert generated, f"no generated stubs found under {_AI_GENERATED}"
    missing = sorted(protos - generated)
    assert not missing, (
        f"protos with no generated stub in ai-server: {missing} — regenerate with "
        "`scripts/generate_protos.sh python`, or the contract is compiled but unreachable"
    )


def test_the_room_server_carries_only_the_protos_it_uses() -> None:
    generated = _generated_files(_ROOM_GENERATED)
    assert len(generated) >= _MIN_ROOM_GENERATED, (
        f"found only {len(generated)} generated stubs under {_ROOM_GENERATED} — the scan is not "
        "reading the tree, so the equality below would pass vacuously"
    )
    observed = frozenset(_stem(path) for path in generated)
    assert observed == _RECORDED_ROOM_PROTOS, (
        "the room server's generated set changed.\n"
        f"  recorded: {sorted(_RECORDED_ROOM_PROTOS)}\n"
        f"  observed: {sorted(observed)}\n"
        "`scripts/generate_protos.sh` narrows this set deliberately: compiling the full set dropped "
        "ai_server/android_server stubs into the room server, which imports neither."
    )


def test_the_android_copy_of_the_shared_protos_agrees_with_the_canonical_one() -> None:
    """The Android module compiles its own copy; the two must not drift."""
    android = _android_proto_names()
    assert len(android) >= 3, (
        f"found only {len(android)} protos under {_ANDROID_PROTO_DIR} — the scan is not reading the "
        "tree, so the agreement check below would pass vacuously"
    )
    assert android == _RECORDED_ANDROID_PROTOS, (
        "the Android module's proto set changed.\n"
        f"  recorded: {sorted(_RECORDED_ANDROID_PROTOS)}\n"
        f"  observed: {sorted(android)}\n"
        "Add or remove the entry here when the client's contract genuinely changes."
    )

    drifted = sorted(
        name
        for name in android
        if _read(_ANDROID_PROTO_DIR / name) != _read(_PROTO_DIR / name)
    )
    assert not drifted, (
        f"the Android copies disagree with `protos/aegis/`: {drifted} — the Kotlin client would "
        "compile against a different wire contract than the Python servers. Copy the canonical file "
        "over the Android one (the canonical directory is the source of truth)."
    )


def test_the_agreement_check_compares_real_text() -> None:
    """Guard against the comparison above going vacuous.

    `drifted` is computed by comparing two strings, so a reader that returns a constant — an empty
    string, or a fixed sentinel — makes every pair equal and the assertion above **always** passes.
    A floor on the number of *files* does not cover this: the files are still there, only their
    content is not being read. So the content itself carries the floor.
    """
    android = _android_proto_names()
    assert len(android) >= 3, f"found only {len(android)} Android protos"

    canonical = {name: _read(_PROTO_DIR / name) for name in sorted(android)}
    client = {name: _read(_ANDROID_PROTO_DIR / name) for name in sorted(android)}
    empty = sorted(
        f"{side}:{name}"
        for side, texts in (("canonical", canonical), ("android", client))
        for name, text in texts.items()
        if len(text) < 100
    )
    assert not empty, (
        f"a proto read back as (near-)empty: {empty} — the agreement check would compare nothing "
        "and pass. The smallest shipped proto is thousands of bytes."
    )
