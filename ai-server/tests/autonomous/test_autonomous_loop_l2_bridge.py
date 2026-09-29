from __future__ import annotations

from aegis_ai.autonomous.autonomous_loop import AutonomousLoop


def test_evaluate_event_uses_l2_event_handler_before_queueing() -> None:
    loop = AutonomousLoop()
    loop.set_l2_reasoning_handler(
        None,
        event_handler=lambda event_type, detail: {
            "handled": True,
            "action_type": "task",
            "reason": f"L2 handled {event_type}",
        },
    )

    result = loop.evaluate_event("social.inbox.received", {"safe_message": "reply needed"})

    assert result["queued"] is False
    assert result["decision"] == "task"
    assert "L2 handled" in result["reason"]
    assert loop._pending_actionable_observations == []
