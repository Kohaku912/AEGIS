"""L1 runs inline on the publisher's thread while L2 was moved off it
(DELEGATION.md section 4 item 48).

Measured 2026-10-05:
  - `runtime.py` defines `_submit_background_l2` (line 732) and uses it on the
    immediate path (line 1629); there is **no** `_submit_background_l1`;
  - `_evaluate_immediate_event` calls `_run_l1_pipeline_for_event` directly
    (line 1562), and that awaits `router.observe(...)` -- the L1 LLM round-trip;
  - `EventBus._notify_subscribers` (`src/event_bus.py:234`) calls handlers
    synchronously on the publisher's thread, and the gRPC `PushEvent` handler
    (`grpc_server.py:169` -> `publish` at `:191`) is one publisher.

So a remote push blocks for the whole L1 call. L2 does not have this problem: it
was moved onto a dedicated single worker (E-2), and `_submit_background_l2`'s own
docstring records why.

The pin measures the *asymmetry* by AST rather than describing it: the L2
submitter exists, the L1 submitter does not, and the immediate handler calls the
pipeline inline (no `submit`). Giving L1 a background path is the recorded fix
(item 48 option (1)) -- it turns this pin red so the record moves with the code.
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
_RUNTIME = SRC / "aegis_ai" / "runtime.py"

_IMMEDIATE_HANDLER = "_evaluate_immediate_event"
_L1_PIPELINE = "_run_l1_pipeline_for_event"


def _functions() -> dict[str, ast.AST]:
    tree = ast.parse(_RUNTIME.read_text(encoding="utf-8"), filename=str(_RUNTIME))
    return {
        n.name: n
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _called_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            names.add(f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", ""))
    return names


def test_l2_has_a_background_submitter() -> None:
    """Control: the scan sees the submitter that does exist."""
    assert "_submit_background_l2" in _functions()


def test_l1_has_no_background_submitter() -> None:
    functions = _functions()
    assert "_submit_background_l1" not in functions, (
        "L1 now has a background submitter -- if that is deliberate, update "
        "DELEGATION.md section 4 item 48 (L1 no longer runs inline)"
    )


def test_the_immediate_handler_calls_the_l1_pipeline_inline() -> None:
    functions = _functions()
    assert _IMMEDIATE_HANDLER in functions, (
        f"{_IMMEDIATE_HANDLER} is gone from runtime.py -- the immediate path was renamed "
        "or moved; update DELEGATION.md section 4 item 48"
    )
    called = _called_names(functions[_IMMEDIATE_HANDLER])
    assert _L1_PIPELINE in called, (
        f"{_IMMEDIATE_HANDLER} no longer calls {_L1_PIPELINE} directly -- the L1 call "
        "shape changed; update DELEGATION.md section 4 item 48"
    )
    assert "submit" not in called, (
        f"{_IMMEDIATE_HANDLER} now submits work to an executor -- if L1 is off the "
        "publisher's thread, update DELEGATION.md section 4 item 48"
    )
