"""Cycle 57 pin: an ``OSError`` a bare discard swallows is named.

Measured 2026-10-06 (cycle 57)
------------------------------
Twelve handlers under ``ai-server/src`` catch ``OSError`` (or a tuple containing it) and
discard it with exactly ``pass`` / ``continue``. Eleven hid a *consequence*:

- ``capability_catalog.CapabilityCatalog._dir_mtime`` -- the mtime is a **cache key**.
  Skipping a manifest whose ``stat`` failed under-reports it, so a change to that file
  leaves the cached catalog looking up to date.
- ``core_capabilities.AegisCoreCapabilityClient._list_files`` -- the unstat-able entry
  vanishes from the listing, and a shorter list looks like a directory holding less.
- ``docker_entrypoint._source_revision`` -- "there is no ``/app/REVISION``" is normal in a
  dev tree, "there is an unreadable one" is not, and both collapse to ``"unknown"``.
- ``integrations.local_tts._run`` -- a ``finally`` cleanup: the temporary text file stays
  behind, invisibly, because the caller already has its result.
- ``net.endpoint_resolver._resolve_hostnames`` -- the literal name is appended *before* the
  lookup, so an unresolvable candidate passes through looking like a resolved one.
- ``personal_data.room_media`` ``encode_opus`` / ``encode_h265`` (3 handlers) -- the same
  ``finally`` shape: a leaked temporary file, or a leaked temporary directory.
- ``social.inbox.SocialInboxStore._load`` -- the quarantine rename failed, so the corrupt
  file is still in place and the store comes back **empty** -- indistinguishable from a
  fresh inbox.
- ``social.manager._parse_timestamp`` -- an unparseable timestamp becomes *now*.
- ``web.dashboard_legacy`` ``/health`` -- the same shape as ``_source_revision``.

One site is **excluded by reason**, and the exclusion is pinned so it cannot rot:

- ``net.endpoint_resolver._ping_lan_prefix`` -- a ``-> None`` best-effort ARP refresh that
  probes every address of a /24. A host with no LAN route can fail all 254, so a record
  *per address* would flood the log about the ordinary case ("that address is not there").
  The instrument this site actually wants is a *count*, which is a different change;
  naming the discard is not it. Cycle 44 excluded ``user_state``'s two ``continue``s the
  same way -- widening a unit means re-adjudicating, never bulk-naming.

⚠️ ``social.manager._parse_timestamp`` holds **two** bare discards, five lines apart:
``except ValueError: pass`` (control flow to the next parse strategy) and
``except (ValueError, OSError): pass`` (the silent default). Only the second is a defect,
and the first stays bare on purpose -- the cycle-53 twin, met again. A pin that "named
every ``pass``" would have changed control flow.

Convention
----------
This family follows the *normal* convention (cycles 54/55): the record carries
``exc_info=True``. The ``queue.Full`` family (cycle 56) is the inverted one.
"""

from __future__ import annotations

import ast
import importlib
import logging
import time
from datetime import datetime
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"

FAMILY_TYPE = "OSError"

# (path relative to src/, a unique fragment of the record) -> the handlers it names
_NAMED_SITES: dict[str, list[str]] = {
    "aegis_ai/capability_catalog.py": ["catalog mtime may be under-reported"],
    "aegis_ai/core_capabilities.py": ["missing from the listing"],
    "aegis_ai/docker_entrypoint.py": ["Could not read /app/REVISION"],
    "aegis_ai/integrations/local_tts.py": ["temporary text file"],
    "aegis_ai/net/endpoint_resolver.py": ["keeping the literal name"],
    "aegis_ai/personal_data/room_media.py": [
        "temporary opus file",
        "temporary h265 file",
        "temporary h265 directory",
    ],
    "aegis_ai/social/inbox.py": ["unreadable inbox"],
    "aegis_ai/social/manager.py": ["using the current time"],
    "aegis_ai/web/dashboard_legacy.py": ["health endpoint reports"],
}

# The logger each named module must resolve. ⚠️ Not every one is the module path:
# dashboard_legacy.py names its logger `aegis_ai.web.dashboard`, and social/inbox.py had
# no logger at all before this cycle.
_LOGGERS: dict[str, str] = {
    "aegis_ai/capability_catalog.py": "aegis_ai.capability_catalog",
    "aegis_ai/core_capabilities.py": "aegis_ai.core_capabilities",
    "aegis_ai/docker_entrypoint.py": "aegis_ai.docker_entrypoint",
    "aegis_ai/integrations/local_tts.py": "aegis_ai.integrations.local_tts",
    "aegis_ai/net/endpoint_resolver.py": "aegis_ai.net.endpoint_resolver",
    "aegis_ai/personal_data/room_media.py": "aegis_ai.personal_data.room_media",
    "aegis_ai/social/inbox.py": "aegis_ai.social.inbox",
    "aegis_ai/social/manager.py": "aegis_ai.social.manager",
    "aegis_ai/web/dashboard_legacy.py": "aegis_ai.web.dashboard",
}

# "<relpath>:<qualname>" -> the reason it stays bare. The pin asserts each entry is *still*
# a bare discard of the family type, so the exclusion cannot become a stale allow-list row.
_EXCLUDED: dict[str, str] = {
    "aegis_ai/net/endpoint_resolver.py:_ping_lan_prefix": (
        "a best-effort probe of every address in a /24; a record per address would flood the "
        "log about the ordinary case. The instrument it wants is a count, not a name."
    ),
}

# ── ast helpers ────────────────────────────────────────────────────────────


def _modules() -> list[Path]:
    return sorted(_SRC.rglob("*.py"))


def _handlers(tree: ast.AST) -> list[ast.ExceptHandler]:
    return [n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)]


def _type_names(node: ast.expr | None) -> set[str]:
    """Every name in the handler's except clause, flattened out of any tuple.

    Set membership, never a string compare: ``OSError`` also appears inside
    ``(ValueError, OSError)``, which a single-name compare would miss (cycle 55).
    """
    if node is None:
        return set()
    if isinstance(node, ast.Tuple):
        names: set[str] = set()
        for element in node.elts:
            names |= _type_names(element)
        return names
    return {ast.unparse(node)}


def _discard_shape(handler: ast.ExceptHandler) -> str | None:
    if len(handler.body) != 1:
        return None
    statement = handler.body[0]
    if isinstance(statement, ast.Pass):
        return "pass"
    if isinstance(statement, ast.Continue):
        return "continue"
    if isinstance(statement, ast.Break):
        return "break"
    return None


def _in_family(handler: ast.ExceptHandler) -> bool:
    return _discard_shape(handler) is not None and FAMILY_TYPE in _type_names(handler.type)


def _body(handler: ast.ExceptHandler) -> str:
    return ast.unparse(ast.Module(body=handler.body, type_ignores=[]))


def _tree_of(rel: str) -> ast.AST:
    return ast.parse((_SRC / rel).read_text(encoding="utf-8"))


def _enclosing_functions(tree: ast.AST) -> dict[int, str]:
    """Map every line inside a function to its dotted qualname."""
    out: dict[int, str] = {}

    def walk(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qual = f"{prefix}{child.name}"
                for line in range(child.lineno, (child.end_lineno or child.lineno) + 1):
                    out[line] = qual
                walk(child, f"{qual}.")
            else:
                walk(child, prefix)

    walk(tree, "")
    return out


def _oserror_handlers(tree: ast.AST) -> list[ast.ExceptHandler]:
    return [h for h in _handlers(tree) if FAMILY_TYPE in _type_names(h.type)]


def _family_sites() -> list[str]:
    """Bare discards of the family, minus the recorded exclusion."""
    found: list[str] = []
    for path in _modules():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:  # pragma: no cover - not expected in src/
            continue
        rel = path.relative_to(_SRC).as_posix()
        qualnames = _enclosing_functions(tree)
        for handler in _handlers(tree):
            if not _in_family(handler):
                continue
            qual = qualnames.get(handler.lineno, "?")
            if f"{rel}:{qual}" in _EXCLUDED:
                continue
            found.append(f"{rel}:{handler.lineno} ({qual})")
    return found


# ── the family rule ────────────────────────────────────────────────────────


def test_no_handler_skips_an_oserror_in_silence() -> None:
    offenders = _family_sites()
    assert offenders == [], f"these handlers discard an OSError with a bare statement: {offenders}"


def test_the_census_is_not_vacuous() -> None:
    """Floors are measurements, not round numbers (measured 2026-10-06: 406 files / 1121 handlers)."""
    files = _modules()
    total = sum(len(_handlers(ast.parse(p.read_text(encoding="utf-8")))) for p in files)
    assert len(files) >= 400, f"only {len(files)} modules scanned; the walk is not reaching src/"
    assert total >= 1100, f"only {total} handlers scanned; the walk is not reaching the handlers"


def test_the_detector_sees_the_family_and_not_its_siblings() -> None:
    tree = ast.parse(
        "def f():\n"
        "    try:\n"
        "        pass\n"
        "    except OSError:\n"
        "        pass\n"
        "    try:\n"
        "        pass\n"
        "    except OSError:\n"
        "        continue\n"
        "    try:\n"
        "        pass\n"
        "    except OSError:\n"
        "        break\n"
    )
    assert [h.lineno for h in _handlers(tree) if _in_family(h)] == [4, 8, 12]


def test_the_detector_reads_a_tuple_and_ignores_a_sibling_type() -> None:
    """The two ways a census goes blind: a tuple spelling, and a *different* family."""
    tree = ast.parse(
        "def f():\n"
        "    try:\n"
        "        pass\n"
        "    except (ValueError, OSError):\n"
        "        pass\n"
        "    try:\n"
        "        pass\n"
        "    except (ValueError, TypeError):\n"
        "        pass\n"
        "    try:\n"
        "        pass\n"
        "    except OSError:\n"
        "        logger.debug('named', exc_info=True)\n"
    )
    in_family = [h.lineno for h in _handlers(tree) if _in_family(h)]
    assert in_family == [4], f"a tuple spelling or a sibling type leaked into the family: {in_family}"
    assert [h.lineno for h in _oserror_handlers(tree)] == [4, 12], (
        "the type census must see both the bare tuple site and the already-named one"
    )


# ── the recorded sites ─────────────────────────────────────────────────────


def test_the_site_map_is_not_vacuous() -> None:
    assert len(_NAMED_SITES) == 9, "the site map lost a module"
    assert sum(len(v) for v in _NAMED_SITES.values()) == 11, "the site map lost a handler"
    for rel, fragments in _NAMED_SITES.items():
        text = (_SRC / rel).read_text(encoding="utf-8")
        for fragment in fragments:
            assert fragment in text, f"{rel} does not contain the recorded fragment {fragment!r}"


def test_every_named_site_names_its_failure_at_debug() -> None:
    for rel, fragments in _NAMED_SITES.items():
        bodies = [_body(h) for h in _oserror_handlers(_tree_of(rel))]
        for fragment in fragments:
            matching = [b for b in bodies if fragment in b]
            assert matching, f"{rel}: no OSError handler names {fragment!r}"
            for body in matching:
                assert "logger.debug" in body, f"{rel}: {fragment!r} is not a debug record"


def test_every_named_site_attaches_a_traceback() -> None:
    """This family's convention is the *normal* one (cycles 54/55): name it with a traceback."""
    for rel, fragments in _NAMED_SITES.items():
        bodies = [_body(h) for h in _oserror_handlers(_tree_of(rel))]
        for fragment in fragments:
            for body in [b for b in bodies if fragment in b]:
                assert "exc_info=True" in body, f"{rel}: {fragment!r} was named without a traceback"


def test_the_excluded_site_is_still_a_bare_discard() -> None:
    """The exclusion is a claim about the code; if it stops being true, the entry must go."""
    for key, reason in _EXCLUDED.items():
        rel, _, qual = key.partition(":")
        tree = _tree_of(rel)
        qualnames = _enclosing_functions(tree)
        matches = [h for h in _handlers(tree) if qualnames.get(h.lineno) == qual and FAMILY_TYPE in _type_names(h.type)]
        assert len(matches) == 1, f"{key}: expected exactly one OSError handler in {qual}, found {len(matches)}"
        assert _discard_shape(matches[0]) == "pass", (
            f"{key} is no longer a bare discard -- delete the exclusion entry. Reason was: {reason}"
        )


def test_every_named_module_resolves_its_logger() -> None:
    for rel, expected in _LOGGERS.items():
        module_name = rel.removesuffix(".py").replace("/", ".")
        module = importlib.import_module(module_name)
        logger = getattr(module, "logger", None)
        assert logger is not None, f"{rel} has no module-level logger"
        assert logger.name == expected, f"{rel}: logger.name is {logger.name!r}, expected {expected!r}"


# ── behavioural: the sites that can be driven cheaply ──────────────────────


def test_source_revision_names_an_unreadable_revision_file(monkeypatch, caplog) -> None:
    from aegis_ai import docker_entrypoint

    def _boom(*_args, **_kwargs):
        raise OSError("permission denied")

    monkeypatch.delenv("AEGIS_SOURCE_REVISION", raising=False)
    monkeypatch.setattr(Path, "read_text", _boom)
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.docker_entrypoint"):
        revision = docker_entrypoint._source_revision()
    assert revision == "unknown", "the fallback value moved"
    assert any("Could not read /app/REVISION" in r.getMessage() for r in caplog.records)
    assert any(isinstance(r.exc_info, tuple) for r in caplog.records), "the traceback was not attached"


def test_source_revision_from_the_env_is_quiet(monkeypatch, caplog) -> None:
    """Control: a configured revision is not a failure."""
    from aegis_ai import docker_entrypoint

    monkeypatch.setenv("AEGIS_SOURCE_REVISION", "abc123")
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.docker_entrypoint"):
        assert docker_entrypoint._source_revision() == "abc123"
    assert [r for r in caplog.records if r.name == "aegis_ai.docker_entrypoint"] == []


def test_resolve_hostnames_names_an_unresolvable_candidate(monkeypatch, caplog) -> None:
    from aegis_ai.net import endpoint_resolver

    def _boom(*_args, **_kwargs):
        raise OSError("no such host")

    monkeypatch.setattr(endpoint_resolver.socket, "getaddrinfo", _boom)
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.net.endpoint_resolver"):
        out = endpoint_resolver._resolve_hostnames(["nope.invalid"])
    assert out == ["nope.invalid"], "the literal name must still be kept"
    assert any("Could not resolve" in r.getMessage() for r in caplog.records)
    assert any(isinstance(r.exc_info, tuple) for r in caplog.records)


def test_resolve_hostnames_keeps_a_resolved_address_quietly(monkeypatch, caplog) -> None:
    """Control: a candidate that resolves is not a failure."""
    from aegis_ai.net import endpoint_resolver

    monkeypatch.setattr(
        endpoint_resolver.socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(2, 1, 6, "", ("10.0.0.7", 0))],
    )
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.net.endpoint_resolver"):
        out = endpoint_resolver._resolve_hostnames(["host.example"])
    assert out == ["host.example", "10.0.0.7"]
    assert [r for r in caplog.records if r.name == "aegis_ai.net.endpoint_resolver"] == []


def test_parse_timestamp_names_an_unparseable_value(caplog) -> None:
    from aegis_ai.social import manager

    with caplog.at_level(logging.DEBUG, logger="aegis_ai.social.manager"):
        got = manager._parse_timestamp("not-a-date")
    assert abs(got - int(time.time() * 1000)) < 5_000, "the fallback is no longer 'now'"
    assert any("Could not parse" in r.getMessage() for r in caplog.records)
    assert any(isinstance(r.exc_info, tuple) for r in caplog.records)


def test_parse_timestamp_of_an_iso_string_is_quiet(caplog) -> None:
    """Control -- and proof the ISO branch still runs rather than the fallback."""
    from aegis_ai.social import manager

    iso = "2026-01-02T03:04:05+00:00"
    expected = int(datetime.fromisoformat(iso).timestamp() * 1000)
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.social.manager"):
        got = manager._parse_timestamp(iso)
    assert got == expected, "the ISO 8601 branch was skipped"
    assert [r for r in caplog.records if r.name == "aegis_ai.social.manager"] == []


def test_inbox_names_a_failed_quarantine(tmp_path, monkeypatch, caplog) -> None:
    from aegis_ai.social import inbox as inbox_mod

    data_dir = tmp_path / "social"
    data_dir.mkdir()
    (data_dir / "social_inbox.json").write_text("not json", encoding="utf-8")

    def _boom(*_args, **_kwargs):
        raise OSError("rename failed")

    monkeypatch.setattr(inbox_mod.os, "replace", _boom)
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.social.inbox"):
        store = inbox_mod.SocialInboxStore(data_dir=str(data_dir))
    assert store._items == {}, "a corrupt inbox still comes back empty (behaviour preserved)"
    assert any("unreadable inbox" in r.getMessage() for r in caplog.records)
    assert any(isinstance(r.exc_info, tuple) for r in caplog.records)


def test_inbox_quarantines_a_corrupt_file_quietly(tmp_path, caplog) -> None:
    """Control: the quarantine succeeds, so there is nothing to report."""
    from aegis_ai.social import inbox as inbox_mod

    data_dir = tmp_path / "social"
    data_dir.mkdir()
    (data_dir / "social_inbox.json").write_text("not json", encoding="utf-8")
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.social.inbox"):
        store = inbox_mod.SocialInboxStore(data_dir=str(data_dir))
    assert store._items == {}
    assert (data_dir / "social_inbox.corrupt.json").exists(), "the corrupt file was not quarantined"
    assert [r for r in caplog.records if r.name == "aegis_ai.social.inbox"] == []


class _Unstatable:
    def stat(self):
        raise OSError("stat failed")

    def is_dir(self):
        return False

    def is_file(self):
        return False


def test_dir_mtime_names_an_unstatable_manifest(monkeypatch, caplog, tmp_path) -> None:
    from aegis_ai import capability_catalog as cc

    catalog = cc.CapabilityCatalog(str(tmp_path))
    monkeypatch.setattr(Path, "rglob", lambda _self, _pattern: iter([_Unstatable()]))
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.capability_catalog"):
        mtime = catalog._dir_mtime()
    assert mtime == 0.0, "an unreadable manifest leaves the mtime at its floor (behaviour preserved)"
    assert any("under-reported" in r.getMessage() for r in caplog.records)
    assert any(isinstance(r.exc_info, tuple) for r in caplog.records)


def test_dir_mtime_of_an_empty_directory_is_quiet(monkeypatch, caplog, tmp_path) -> None:
    """Control: an empty capabilities directory is not a failure."""
    from aegis_ai import capability_catalog as cc

    catalog = cc.CapabilityCatalog(str(tmp_path))
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.capability_catalog"):
        assert catalog._dir_mtime() == 0.0
    assert [r for r in caplog.records if r.name == "aegis_ai.capability_catalog"] == []


def test_list_files_names_an_unstatable_entry(monkeypatch, caplog) -> None:
    from aegis_ai import core_capabilities as cc

    class _Root:
        def exists(self):
            return True

        def is_dir(self):
            return True

        def iterdir(self):
            return iter([_Unstatable()])

    client = object.__new__(cc.AegisCoreCapabilityClient)
    monkeypatch.setattr(client, "_resolve_file_path", lambda _p: _Root(), raising=False)
    monkeypatch.setattr(
        client,
        "_path_metadata",
        lambda _p: {"path": ".", "relative_path": ".", "path_scope": "workspace"},
        raising=False,
    )
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.core_capabilities"):
        out = client._list_files({"path": "."})
    assert out["ok"] is True
    assert out["files"] == [], "the unstat-able entry is dropped from the listing (behaviour preserved)"
    assert any("missing from the listing" in r.getMessage() for r in caplog.records)
    assert any(isinstance(r.exc_info, tuple) for r in caplog.records)


def test_list_files_without_an_entry_to_skip_is_quiet(monkeypatch, caplog) -> None:
    """Control: a directory with nothing in it is not a failure."""
    from aegis_ai import core_capabilities as cc

    class _Root:
        def exists(self):
            return True

        def is_dir(self):
            return True

        def iterdir(self):
            return iter([])

    client = object.__new__(cc.AegisCoreCapabilityClient)
    monkeypatch.setattr(client, "_resolve_file_path", lambda _p: _Root(), raising=False)
    monkeypatch.setattr(
        client,
        "_path_metadata",
        lambda _p: {"path": ".", "relative_path": ".", "path_scope": "workspace"},
        raising=False,
    )
    with caplog.at_level(logging.DEBUG, logger="aegis_ai.core_capabilities"):
        out = client._list_files({"path": "."})
    assert out["files"] == []
    assert [r for r in caplog.records if r.name == "aegis_ai.core_capabilities"] == []


@pytest.mark.parametrize(
    ("rel", "fragment"),
    [
        ("aegis_ai/integrations/local_tts.py", "temporary text file"),
        ("aegis_ai/personal_data/room_media.py", "temporary opus file"),
        ("aegis_ai/personal_data/room_media.py", "temporary h265 file"),
        ("aegis_ai/personal_data/room_media.py", "temporary h265 directory"),
    ],
)
def test_the_finally_cleanups_report_a_leak_without_a_traceback_shortcut(rel: str, fragment: str) -> None:
    """The four ``finally`` cleanups sit in code paths that need ffmpeg to drive.

    Their *shape* is what can be checked without a subprocess: a single ``logger.debug``
    naming the file or directory, with ``exc_info=True`` so the reason is recoverable.
    """
    bodies = [_body(h) for h in _oserror_handlers(_tree_of(rel))]
    matching = [b for b in bodies if fragment in b]
    assert len(matching) == 1, f"{rel}: expected one record naming {fragment!r}, found {len(matching)}"
    body = matching[0]
    assert body.startswith("logger.debug("), f"{rel}: the cleanup no longer *is* the record"
    assert "exc_info=True" in body, f"{rel}: {fragment!r} was named without a traceback"
