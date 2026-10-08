"""Every route named in a documented route table must actually be registered.

Why this file exists
--------------------
``docs/approval-ui.md`` and ``docs/feature-catalog.md`` publish route tables — a **claim**
about the HTTP surface. Nothing compared them to the app, so a table could name an endpoint
that does not exist, and every test would stay green. That is the "two artefacts describe the
same thing — assert they agree" shape, applied to the API docs.

Scope: the **tables only**, never prose. The docs also *quote* refuted routes in prose —
``POST /api/chat/stream`` appears as a correction record ("there is no such route") — so a
naive "every path in the file must exist" scan would fail on the correction itself. That is
precisely the shape that makes a hand-maintained exclusion list a defect, so the rule here is
structural instead: **a table row is an assertion; a sentence quoting a mistake is not.**

Direction: documented ⇒ registered. The converse is deliberately **not** asserted. Measured
2026-10-03 with this file's own ``_app`` (production, ``AEGIS_UI_VERSION=v2``): the app registers
**190 rules / 200 (method, path) pairs**, and under the matching rule *"the client contains the
rule's literal path, or its static prefix up to the first ``<``"* **96 of the 200 are referenced
by no client source** (125 if only the literal path counts). The client set is stated so the figure
is re-derivable: every text-ish file under ``web-ui/src``, ``pc-server``, ``browser-server``,
``room-server``, ``android-server`` and ``packages`` — **excluding ``ai-server/src``**, where a
route's own definition would otherwise count as a reference.

⚠️ **Both counts moved on the same day, and the direction is the point.** The two shadowed legacy
routes were deleted (``DELEGATION.md`` §4 item 28), so pairs fell **202 → 200** and the
unreferenced count fell **98 → 96**. The **distinct** pair count was always 200 and the distinct
unreferenced set was always 96: the duplicates were two *extra registrations*, so removing them
made the multiplicity count **converge on** the distinct one. The breakdown of the 96 is
GET 56 / POST 35 / DELETE 3 / PATCH 2.

⚠️ A third variant was recorded as "75 if only the first two segments do" and is **not reproduced**
here (a re-implementation of that rule gives 69), so **do not quote it**: the rule is
under-specified, which is the same defect as the "86 of 189" below.

Those figures **replace a recorded "86 of 189"**, which reproduces under **none** of the matching
rules tried nor any count of the surface, over either client set. The likely explanation is that it
was quoted from an earlier state or a different method — but the durable lesson is that **a count
quoted without its method cannot be re-derived**, which is how it survived: nobody could tell
whether a later measurement disagreed with it.
The **conclusion is unchanged** — most are public APIs for operators, Android or the display
surface, so "no client" is a **candidate, not a verdict**. Each would need its own two-ended check
(the chat SSE route was dead only because its own registry was inert as well; it has since been
deleted — `DELEGATION.md` § 4 item 23).
"""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from test_dashboard_routes import _runtime

from aegis_ai.web import dashboard_routes

_REPO = Path(__file__).resolve().parents[2]

#: The two documents that publish route tables.
_DOCS = (
    _REPO / "docs" / "approval-ui.md",
    _REPO / "docs" / "feature-catalog.md",
)

#: Two table layouts are in use. ``| GET | `/api/x` | ...`` and ``| `GET /api/x` | ...``.
_ROW_FORMS = (
    re.compile(r"^\|\s*(?P<method>GET|POST|PUT|PATCH|DELETE)\s*\|\s*`(?P<path>/[^`]*)`"),
    re.compile(r"^\|\s*`(?P<method>GET|POST|PUT|PATCH|DELETE)\s+(?P<path>/[^`]*)`"),
)

#: The exact documented set, measured 2026-10-03. **Equality, not a floor**: this table has
#: only 12 rows, so a floor of 11 would let a reformatted row vanish silently — which is
#: exactly what a first attempt did (mutation M3 survived a floor; it cannot survive this).
_RECORDED_DOCUMENTED = frozenset({
    ("GET", "/api/approvals"),
    ("GET", "/api/approvals/pending"),
    ("GET", "/api/approvals/<id>"),
    ("GET", "/api/approvals/events"),
    ("POST", "/api/approvals/<id>/approve"),
    ("POST", "/api/approvals/<id>/modify-and-approve"),
    ("POST", "/api/approvals/<id>/reject"),
    ("POST", "/api/approvals/<id>/cancel"),
    ("GET", "/api/chat/history"),
    ("POST", "/api/chat/send"),
    ("POST", "/api/chat/respond"),
    ("POST", "/api/chat/clear"),
})

#: Dummy values for Flask converters, so a documented template can be matched.
_DUMMY = {
    "int": "1",
    "float": "1.0",
    "path": "x",
    "uuid": "00000000-0000-0000-0000-000000000000",
    "any": "x",
    "string": "x",
}


def _documented() -> set[tuple[str, str]]:
    """Every ``(method, path)`` asserted by a route table."""
    found: set[tuple[str, str]] = set()
    for doc in _DOCS:
        text = doc.read_text(encoding="utf-8")
        for line in text.splitlines():
            for pattern in _ROW_FORMS:
                match = pattern.match(line)
                if match:
                    found.add((match.group("method"), match.group("path")))
                    break
    return found


def _concretise(template: str) -> str:
    def replace(match: re.Match[str]) -> str:
        inner = match.group(1)
        converter = inner.split(":", 1)[0] if ":" in inner else "string"
        return _DUMMY.get(converter, "x")

    return re.sub(r"<([^>]+)>", replace, template)


def _app(tmp_path: Any, monkeypatch: Any) -> Any:
    """The real dashboard app, built the way ``test_dashboard_routes_are_protected_or_recorded``
    builds it, so the route surface measured here is the one operators actually run."""
    monkeypatch.setenv("AEGIS_RUNTIME_MODE", "production")
    monkeypatch.setenv("AEGIS_SESSION_SECRET", "x" * 64)
    monkeypatch.setenv("AEGIS_UI_VERSION", "v2")
    for name in (
        "AEGIS_AUTH_MODE",
        "AEGIS_DASHBOARD_ACCESS_TOKEN",
        "AEGIS_DISPLAY_TOKEN",
        "AEGIS_DISPLAY_READ_TOKEN",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(dashboard_routes, "_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(dashboard_routes.DashboardApp, "_start_autonomous_loop", lambda self: None)
    runtime = _runtime(tmp_path)
    runtime.presentation_manager = SimpleNamespace(
        list_active=lambda limit=20: [], get_status=lambda: {}
    )
    app = dashboard_routes.DashboardApp(runtime=runtime).app
    app.config.update(TESTING=True)
    return app


# ── Non-vacuity: the tables are still being read ──────────────────────────────


def test_the_route_tables_are_still_parsed() -> None:
    documented = _documented()
    assert documented == _RECORDED_DOCUMENTED, (
        "the documented route set changed.\n"
        f"  added:   {sorted(documented - _RECORDED_DOCUMENTED)}\n"
        f"  removed: {sorted(_RECORDED_DOCUMENTED - documented)}\n"
        "A *removed* row is usually a reformat that silently stopped matching _ROW_FORMS — the "
        "pin would otherwise go vacuous. A *added* row is a new claim: record it here, and the "
        "test below will check it against the app."
    )


# ── The invariant ─────────────────────────────────────────────────────────────


def test_every_documented_route_is_registered(tmp_path: Any, monkeypatch: Any) -> None:
    app = _app(tmp_path, monkeypatch)
    adapter = app.url_map.bind("localhost")

    missing: list[str] = []
    for method, path in sorted(_documented()):
        try:
            adapter.match(_concretise(path), method=method)
        except Exception as exc:  # noqa: BLE001 — the failure text is the point
            missing.append(f"{method} {path}  ({exc})")

    assert missing == [], (
        "these routes are published in a doc's route table but are not registered:\n  "
        + "\n  ".join(missing)
        + "\nEither the doc is stale (fix it) or the route was lost (restore it). Do not "
        "weaken the table's scope to make this pass."
    )
