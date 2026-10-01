"""§3.1 hole 3 — the burden metric — cannot be computed from the existing decision log.

`DECISION_DRAFTS.md` §B-5 answers hole 3 with *"derive it from the existing decision log; no new
instrumentation is needed"*, because P1-6 made the log carry the `net = benefit x P(receptive) - cost`
breakdown. Measured 2026-10-01, **that premise holds for one of the three proposed sub-metrics and
fails for the other two**:

1. **Interruptions per day — computable.** `AuditEntry.timestamp_ms` exists and
   `InterruptionController.before_send` audits every decision under `action="interruption_decision"`,
   so the series is a `SELECT ... GROUP BY day`.
2. **The fraction the user responded to — NOT computable.** The response lives in
   `NotificationManager._notifications` (an in-memory dict keyed by `notification_id`), written by
   `mark_read` / `dismiss` / `expire`. `notification_manager.py` makes **no audit call at all**, so the
   response is never persisted and cannot be joined to the decision log after a restart. Worse, the
   method that would carry it cannot distinguish its callers: `dismiss(notification_id)` is called both
   from the user's web route (`web/manager_routes.py`) and **by the system**
   (`PresentationManager.dismiss` -> `notification_manager.dismiss(...)`), with no marker argument — so
   counting dismissals as user responses would also count the system's own.
3. **Median cost of accepted interruptions — computable only over a subset.** `utility` (and therefore
   `cost`) is attached at **1 of the 5** `_decision(...)` return paths. The four hard gates —
   `emergency_stop`, the exception-category/critical `send_now`, quiet-hours `batch_later`, and the
   `UserModel` `suppress` — return a decision **with no breakdown**. So "accepted" mixes cost-bearing
   records with cost-less ones, and the median silently depends on which gate fired.

This is a **measurement, not a decision**: which sub-metrics to accept, and whether to persist the
user's response, are the owner's calls (`DELEGATION.md` §3 and §4 item 8; `DECISION_DRAFTS.md` §B-5
carries the answer this refutes in part). The pin fixes the structural facts so that changing any of
them is deliberate rather than silent — if the response starts being persisted, or a gate starts
carrying a breakdown, these assertions fire and the register row must be revisited.
"""

from __future__ import annotations

import ast
from functools import lru_cache
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SRC = _REPO / "ai-server" / "src"

_INTERRUPTION = _SRC / "aegis_ai" / "personal_ai" / "interruption.py"
_NOTIFICATION_MANAGER = _SRC / "aegis_ai" / "notification" / "notification_manager.py"
_PRESENTATION_MANAGER = _SRC / "aegis_ai" / "presentation" / "manager.py"

# Every `_decision(...)` return path in `InterruptionController`, and whether it attaches the utility
# breakdown. Pinned by equality so that adding a path (or starting to report a breakdown from a hard
# gate) is a deliberate edit rather than a silent change to what the burden metric can be computed on.
_RECORDED_DECISION_PATHS: dict[str, bool] = {
    "emergency_stop": False,
    "send_now": False,
    "batch_later": False,
    "suppress": False,
    "expected_utility": True,
}

# Modules that define a method named `dismiss`. Two different managers own the same name, which is
# why a purely syntactic scan cannot tell `NotificationManager.dismiss` from
# `PresentationManager.dismiss` — and why the burden metric cannot either.
_RECORDED_DISMISS_DEFINERS: frozenset[str] = frozenset(
    {
        "ai-server/src/aegis_ai/notification/notification_manager.py",
        "ai-server/src/aegis_ai/presentation/manager.py",
    }
)

# A non-vacuity floor must sit strictly *below* the recorded count, or it answers for the equality
# instead of for the scan and answers wrongly: with the floor at the recorded 5, removing one
# `_decision(...)` path fires "the scan is not reading the file" — a confident lie about a genuine
# content change, and it suppresses the equality's own (accurate) message. One is the value a blinded
# scan cannot reach, so one is the floor.
_MIN_DECISION_PATHS = 1

# The upstream floor for the `dismiss` scan: put the floor on the quantity the reader walks, not on
# the set the equality compares. `len(defining) >= 2` would fire on a *rename* — exactly the content
# change this pin exists to surface — with a message blaming the scanner. Measured 2026-10-01: 407.
_MIN_SRC_FILES = 300


def _rel(path: Path) -> str:
    return path.resolve().relative_to(_REPO).as_posix()


@lru_cache(maxsize=1)
def _src_files() -> tuple[Path, ...]:
    return tuple(sorted(_SRC.rglob("*.py")))


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _decision_paths() -> dict[str, bool]:
    """Map each `_decision(...)` return path to whether it attaches a `utility` breakdown.

    The path is keyed by the verdict literal (the first positional argument); the expected-utility
    path passes its verdict through a variable, so it is keyed by its keyword instead.
    """
    paths: dict[str, bool] = {}
    for node in ast.walk(_parse(_INTERRUPTION)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "_decision"):
            continue
        carries = any(kw.arg == "utility" for kw in node.keywords)
        first = node.args[0] if node.args else None
        key = first.value if isinstance(first, ast.Constant) and isinstance(first.value, str) else "expected_utility"
        paths[key] = carries
    return paths


def _audit_calls(path: Path) -> list[int]:
    """Line numbers of calls that look like an audit write.

    Deliberately syntactic: `log_decision` / `log_approval` / anything named `*audit*`. The point is
    not to be exhaustive but to be able to *see* one when it is there — see the positive control.
    """
    out: list[int] = []
    for node in ast.walk(_parse(path)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else (func.id if isinstance(func, ast.Name) else "")
        if name.startswith("log_") or "audit" in name.lower():
            out.append(node.lineno)
    return out


def test_the_decision_log_can_count_interruptions_per_day() -> None:
    """Sub-metric 1 is computable — the log has a timestamp and one action per decision."""
    entry = ast.parse((_SRC / "aegis_ai" / "audit" / "audit_log.py").read_text(encoding="utf-8"))
    fields = {
        node.target.id
        for node in ast.walk(entry)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    assert "timestamp_ms" in fields, (
        "`AuditEntry` has no `timestamp_ms`, so interruptions cannot be counted per day — "
        "sub-metric 1 of §3.1 hole 3 is no longer computable"
    )

    text = _INTERRUPTION.read_text(encoding="utf-8")
    assert '"interruption_decision"' in text, (
        "the controller no longer audits under `interruption_decision`, so the decision series this "
        "metric aggregates does not exist"
    )


def test_the_utility_breakdown_covers_one_of_the_return_paths() -> None:
    """Sub-metric 3's denominator: only one path reports a cost."""
    paths = _decision_paths()
    assert len(paths) >= _MIN_DECISION_PATHS, (
        f"found no `_decision(...)` call in {_rel(_INTERRUPTION)} — the scan is not reading the file"
    )
    assert paths == _RECORDED_DECISION_PATHS, (
        "the set of `_decision(...)` return paths, or which of them reports a utility breakdown, "
        "changed.\n"
        f"  recorded: {_RECORDED_DECISION_PATHS}\n"
        f"  observed: {paths}\n"
        "If a hard gate now reports a breakdown, the median-cost metric covers more records than the "
        "register says — revisit `DELEGATION.md` §3 and §4 item 8."
    )


def test_the_users_response_to_a_notification_is_never_persisted() -> None:
    """Sub-metric 2's missing instrument, with a positive control that the scan can see an audit call."""
    control = _audit_calls(_PRESENTATION_MANAGER)
    assert control, (
        f"the scan found no audit call in {_rel(_PRESENTATION_MANAGER)}, which does audit — so the "
        "detector is blind and the assertion below would pass vacuously"
    )

    observed = _audit_calls(_NOTIFICATION_MANAGER)
    assert not observed, (
        f"{_rel(_NOTIFICATION_MANAGER)} now writes an audit record at lines {observed}. The user's "
        "response to a notification is becoming persisted — if that is deliberate, §3.1 hole 3's "
        "second sub-metric is now computable and the register row must say so."
    )


def test_the_notification_dismiss_cannot_tell_the_user_from_the_system() -> None:
    """Why sub-metric 2 would be wrong even if it were persisted."""
    files = _src_files()
    assert len(files) >= _MIN_SRC_FILES, (
        f"the scan found only {len(files)} Python files under ai-server/src — it is not reading the "
        "tree, so the equality below would pass vacuously"
    )
    defining = {
        _rel(path)
        for path in files
        if any(
            isinstance(node, ast.FunctionDef) and node.name == "dismiss"
            for node in ast.walk(_parse(path))
        )
    }
    assert defining == _RECORDED_DISMISS_DEFINERS, (
        "the set of modules defining `dismiss` changed.\n"
        f"  recorded: {sorted(_RECORDED_DISMISS_DEFINERS)}\n"
        f"  observed: {sorted(defining)}\n"
        "Two managers sharing one method name is the reason a call-site scan cannot attribute a "
        "dismissal to the notification manager without resolving the receiver's type."
    )

    dismiss = next(
        node
        for node in ast.walk(_parse(_NOTIFICATION_MANAGER))
        if isinstance(node, ast.FunctionDef) and node.name == "dismiss"
    )
    params = [a.arg for a in dismiss.args.args]
    assert params == ["self", "notification_id"], (
        f"`NotificationManager.dismiss` now takes {params} — if a caller/source argument was added, "
        "the system's own dismissal can finally be told apart from the user's, which is the fix this "
        "measurement implies"
    )

    system_calls = [
        node.lineno
        for node in ast.walk(_parse(_PRESENTATION_MANAGER))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"dismiss_notification", "dismiss"}
    ]
    assert system_calls, (
        f"{_rel(_PRESENTATION_MANAGER)} no longer dismisses the notification that belongs to the "
        "presentation it is tearing down — so a dismissal would again be attributable to the user "
        "alone, and sub-metric 2 could be computed"
    )
