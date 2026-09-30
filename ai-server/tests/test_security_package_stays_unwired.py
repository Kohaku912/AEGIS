"""The whole ``aegis_ai.security`` package is unwired — nothing outside it imports it.

``docs/security.md`` documents six classes — ``LocalTokenAuth``, ``TokenStore``,
``CSRFProtection``, ``RateLimiter``, ``OriginChecker``, ``TLSConfig`` — each with a usage
example. Measured 2026-10-01 across ``ai-server/src``, ``ai-server/tests`` and every sibling
server (pc / browser / room / android / sdk / scripts / web-ui):

* **No file outside ``aegis_ai/security/`` imports the package.** The only non-self references
  anywhere are ``logging.getLogger("aegis_ai.security.…")`` strings inside it, its own
  ``__init__.py`` re-exports, and the documentation.
* None of the six class names is *named* outside the package either — no call site, no test.
* The live auth system is ``aegis_ai/auth/`` (passkey + its own ``csrf.py``), imported by
  ``web/auth.py``. ``security/`` is a **superseded** package, not a missing one.

So the docs describe a security layer that does not exist in the running system. This module
pins the measurement so the prose cannot quietly re-acquire a claim the code does not support,
and so that *wiring* or *deleting* the package is a deliberate change rather than an accident.

**Recorded, not wired, not deleted** — deliberately. Wiring it would re-introduce a *second*
auth/CSRF implementation alongside the live ``aegis_ai/auth/``; deleting a whole documented
package is an owner judgement, not a code cleanup. ``DELEGATION.md`` §4 carries the decision.
"""

from __future__ import annotations

import ast
from pathlib import Path

_SERVER = Path(__file__).resolve().parents[1]
_SRC = _SERVER / "src"
_TESTS = _SERVER / "tests"

_PACKAGE = "aegis_ai.security"
_PACKAGE_DIR = _SRC / "aegis_ai" / "security"

#: The public surface ``docs/security.md`` claims. None of these may be named outside the package.
_DOCUMENTED_NAMES: tuple[str, ...] = (
    "LocalTokenAuth",
    "TokenStore",
    "CSRFProtection",
    "RateLimiter",
    "OriginChecker",
    "TLSConfig",
    "generate_token",
    "hash_token",
    "generate_self_signed_cert",
)

#: The live replacement. Its presence is the control that proves the importer scan works.
_LIVE_AUTH_PACKAGE = "aegis_ai.auth"

#: The only bodies that build gRPC server credentials. Both live in code with no caller.
_DEAD_CREDENTIAL_BUILDERS = {"get_grpc_credentials", "configure_server"}


def _py_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)


def _parsed(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8", errors="replace"))


def _is_inside_package(path: Path) -> bool:
    return _PACKAGE_DIR in path.resolve().parents


def _import_targets() -> list[tuple[str, str]]:
    """Every module name named by an ``import`` / ``from … import``, with its file."""
    out: list[tuple[str, str]] = []
    for path in (*_py_files(_SRC), *_py_files(_TESTS)):
        for node in ast.walk(_parsed(path)):
            if isinstance(node, ast.Import):
                out.extend((str(path), alias.name) for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    out.append((str(path), node.module))
                # Relative imports: ``from . import tls_config`` carries the name in the alias.
                out.extend((str(path), alias.name) for alias in node.names)
    return out


def _names_referenced_outside_the_package(name: str) -> set[str]:
    """Files outside ``aegis_ai/security/`` that *use* ``name`` as code (not in a docstring).

    Matches ``Name`` and ``Attribute`` nodes, so a string in a docstring or a log message is not
    a use. Definitions inside the package are skipped by path.
    """
    hits: set[str] = set()
    for path in (*_py_files(_SRC), *_py_files(_TESTS)):
        if _is_inside_package(path):
            continue
        for node in ast.walk(_parsed(path)):
            if isinstance(node, ast.Name) and node.id == name:
                hits.add(str(path))
            elif isinstance(node, ast.Attribute) and node.attr == name:
                hits.add(str(path))
    return hits


def _callers_of(name: str) -> set[str]:
    """Enclosing functions that call ``name`` — as ``.name(...)`` or a bare ``name(...)``.

    The **enclosing function** is what matters: counting call sites would let a forwarder
    (``configure_server`` calling ``ssl_server_credentials``) look like a live caller, when the
    forwarder itself has no caller.
    """
    self_path = Path(__file__).resolve()
    found: set[str] = set()

    def walk(node: ast.AST, enclosing: str | None) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                walk(child, child.name)
                continue
            if isinstance(child, ast.Call):
                func = child.func
                called = getattr(func, "attr", None) or getattr(func, "id", None)
                if called == name:
                    found.add(enclosing or "<module>")
            walk(child, enclosing)

    for path in (*_py_files(_SRC), *_py_files(_TESTS)):
        if path.resolve() == self_path:
            continue
        walk(_parsed(path), None)
    return found


def _defines_class(module_path: Path, class_name: str) -> bool:
    return any(
        isinstance(node, ast.ClassDef) and node.name == class_name
        for node in ast.walk(_parsed(module_path))
    )


def test_the_security_package_is_imported_by_nothing_outside_itself() -> None:
    """``aegis_ai.security`` has no importer outside the package — measured 2026-10-01."""
    offenders = sorted(
        f"{path}: {target}"
        for path, target in _import_targets()
        if (target == _PACKAGE or target.startswith(_PACKAGE + "."))
        and not _is_inside_package(Path(path))
    )
    assert offenders == [], (
        "aegis_ai.security gained an importer outside its own package:\n  "
        + "\n  ".join(offenders)
        + "\nThe dead security package is live again — update this record."
    )
    # Positive control: the *live* auth package is imported (by web/auth.py), so an empty result
    # above is a fact about aegis_ai.security rather than a broken import scan.
    assert any(
        target == _LIVE_AUTH_PACKAGE or target.startswith(_LIVE_AUTH_PACKAGE + ".")
        for _, target in _import_targets()
    ), (
        f"the import scan cannot see {_LIVE_AUTH_PACKAGE}, which web/auth.py imports, so its "
        "result for aegis_ai.security is unusable"
    )


def test_the_documented_security_names_are_unused_outside_the_package() -> None:
    """None of the six documented classes (or their helpers) is named outside the package."""
    for name in _DOCUMENTED_NAMES:
        users = _names_referenced_outside_the_package(name)
        assert users == set(), (
            f"{name} is now used outside aegis_ai.security: {sorted(users)}. The documented "
            "security surface is live again — update this record."
        )
    # Positive control: a live class in the sibling auth package *is* named outside its package,
    # so the empty results above are facts rather than a broken name scan.
    assert _names_referenced_outside_the_package("PasskeyService"), (
        "the name scan cannot see PasskeyService outside aegis_ai.auth, so its empty results "
        "above are unusable"
    )


def test_the_two_tls_config_classes_are_recorded() -> None:
    """Both TLS modules define ``TLSConfig`` — the fork is deliberate to record, not to fix."""
    assert _defines_class(_PACKAGE_DIR / "tls.py", "TLSConfig")
    assert _defines_class(_PACKAGE_DIR / "tls_config.py", "TLSConfig")


def test_tls_credentials_are_only_built_inside_dead_code() -> None:
    """Nothing live builds gRPC server credentials."""
    builders = _callers_of("ssl_server_credentials")
    assert builders == _DEAD_CREDENTIAL_BUILDERS, (
        f"gRPC server credentials are now built from {sorted(builders)} — expected only the dead "
        f"{sorted(_DEAD_CREDENTIAL_BUILDERS)}. TLS may have been wired: update this record."
    )


def test_no_live_server_binds_a_secure_port() -> None:
    """``add_secure_port`` is reached only from the unimported package; live servers stay plaintext."""
    secure = _callers_of("add_secure_port")
    assert secure == {"configure_server"}, (
        f"add_secure_port is now called from {sorted(secure)} — expected only the dead "
        "configure_server. A live server may have gained TLS: update this record."
    )
    # Positive control: the live servers *do* bind a port — insecure. If the scan cannot see that,
    # its result for add_secure_port would prove nothing.
    assert _callers_of("add_insecure_port"), (
        "the caller scan found no add_insecure_port call, though grpc_server.serve and "
        "room-server.server.serve both bind one, so its result for add_secure_port is unusable"
    )
