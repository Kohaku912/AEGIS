"""The background L2 pipeline runs off the request thread — and the event bus is why it must.

``docs/improvement-review.md`` §E-2: the gRPC server runs on
``ThreadPoolExecutor(max_workers=config.max_workers)`` (default **10**, ``config.py``), while an
outbound call can take up to 30 s (``agents/backends/openhands/workspace._default_http_post``).
The survey's consequence — "10 slow outbound calls and the AI Server accepts nothing new" — rests
on a *mechanism*: **the outbound call runs on a request thread**.

The mechanism is real, and the first test **measures** it instead of inferring it from reading:
``EventBus._notify_subscribers`` calls each handler inline, so a subscriber runs on whichever thread
called ``publish`` — and one such caller is the gRPC ``PushEvent`` handler.

That is why the second test pins the fix: the *background* subscriber hands the L2 pipeline to a
dedicated worker rather than running it on the caller. On that path the L2 result is discarded (only
its side effects matter), so only timing changes.

The third test pins the wiring, because the helper only helps if the subscriber actually calls it.

**What this file does not claim.** It pins a *structure*, not a *capacity*: there is no load test
here, so it says nothing about how many concurrent outbound calls actually occur. §E-2's own note
("性能は測っていない") still stands for that half.
"""

from __future__ import annotations

import ast
import threading
import time
from pathlib import Path
from typing import Any

import aegis_ai.runtime as runtime_module
from aegis_schema.models import Event, EventPriority, ServerType
from event_bus import EventBus

_PROBE_TIMEOUT_S = 5.0


def _event() -> Event:
    return Event(
        event_id="evt-probe",
        event_type="probe.thread_affinity",
        source_server_type=ServerType.ANDROID,
        source_server_id="probe-server",
        timestamp_ms=1,
        payload_json="{}",
        priority=EventPriority.NORMAL,
    )


def test_the_event_bus_notifies_subscribers_on_the_publishers_thread() -> None:
    """E-2's premise, measured: ``publish`` runs handlers inline, not on a worker of its own."""
    bus = EventBus()
    seen: dict[str, Any] = {}

    def handler(event: Event) -> None:
        seen["thread_name"] = threading.current_thread().name
        seen["event"] = event

    bus.subscribe(handler)

    publisher = threading.Thread(target=lambda: bus.publish(_event()), name="publisher-probe")
    publisher.start()
    publisher.join(timeout=_PROBE_TIMEOUT_S)

    # Wait for delivery separately from the publisher's lifetime. If dispatch ever became
    # asynchronous, joining the publisher would return first and the floor below would fire
    # instead of the assertion that actually names the defect.
    deadline = time.monotonic() + _PROBE_TIMEOUT_S
    while "event" not in seen and time.monotonic() < deadline:
        time.sleep(0.01)

    # Non-vacuity floor: strictly weaker than the assertion below, so it cannot mask its message.
    assert seen.get("event") is not None, "the subscriber never ran — the probe is vacuous"
    assert seen["thread_name"] == "publisher-probe", (
        "EventBus must notify subscribers on the publisher's thread; "
        f"observed {seen['thread_name']!r}. If dispatch became asynchronous, §E-2 is resolved and "
        "both this file and the survey entry must be updated."
    )


def test_the_background_l2_helper_runs_the_pipeline_off_the_calling_thread(monkeypatch) -> None:
    """The fix: the helper must not execute L2 on the thread that submitted it."""
    calls: list[str] = []

    def fake_run_l2(runtime: Any, *, trigger: str, detail: dict[str, Any]) -> dict[str, Any]:
        calls.append(threading.current_thread().name)
        return {"handled": False, "action_type": "noop"}

    monkeypatch.setattr(runtime_module, "_run_l2_pipeline", fake_run_l2)

    class _FakeRuntime:
        """Bare object — the helper only needs somewhere to hang its executor."""

    runtime = _FakeRuntime()
    caller_thread = threading.current_thread().name
    runtime_module._submit_background_l2(runtime, trigger="probe", detail={})

    deadline = time.monotonic() + _PROBE_TIMEOUT_S
    while not calls and time.monotonic() < deadline:
        time.sleep(0.01)

    executor = getattr(runtime, "_background_l2_executor", None)
    try:
        # Non-vacuity floor: weaker than the assertions below.
        assert calls, "the pipeline never ran — the probe is vacuous"
        assert calls[0] != caller_thread, (
            "background L2 ran on the caller's thread; the offload is ineffective (§E-2)"
        )
        assert calls[0].startswith("aegis-background-l2"), (
            f"background L2 ran on an unexpected thread: {calls[0]!r}"
        )
    finally:
        if executor is not None:
            executor.shutdown(wait=False)


def test_the_background_subscriber_submits_l2_instead_of_calling_it_inline() -> None:
    """Wiring: the helper is only reached if the subscriber calls it."""
    source = Path(runtime_module.__file__).read_text(encoding="utf-8")
    handlers = [
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef) and node.name == "_handle_background_l1_event"
    ]

    assert len(handlers) == 1, (
        f"expected exactly one background L1 subscriber, found {len(handlers)}"
    )

    called = {
        node.func.id
        for node in ast.walk(handlers[0])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert "_submit_background_l2" in called, (
        "the background subscriber must hand the L2 pipeline to the off-thread helper (§E-2)"
    )
    assert "_run_l2_pipeline" not in called, (
        "the background subscriber must not run the L2 pipeline inline on the request thread (§E-2)"
    )
