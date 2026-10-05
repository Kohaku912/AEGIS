"""Notification interruption control.

Whether to speak now is a decision under uncertainty, so it is computed as an
**expected utility** rather than read off a ladder of `if` statements (proposal
P1-14, after Horvitz's models of interruption)::

    net = benefit × P(receptive) − cost
    speak if net > 0

* ``benefit``      — what delivering this notification now is worth. Grounded in the
                     severity vocabulary the rest of the system already uses.
* ``P(receptive)`` — the probability the user welcomes an interruption *at this
                     moment*, from the situation's ``interruptibility``, discounted by
                     how absorbed the current activity says they are.
* ``cost``         — the price of breaking in, from occupancy alone.

Two axes on purpose. Receptivity and occupancy are correlated, so folding them into
one number would hide which signal moved the decision. Every term is returned in the
decision under ``utility``, so a reader of the log can recompute the sign;
``tests/test_interruption_utility.py`` asserts that recomputation, which is what keeps
this from being a ladder wearing a utility costume.

What is *not* here, deliberately:

* **Learning.** Proposal P1-14 says start from a hand-designed expected utility and
  move to a learned one once there is data. There is no data yet. The parameters below
  are the hand-designed ones, and they are module constants rather than settings
  fields — a settings flag would need a reader and an owner decision, and this surface
  already carries too much unowned config.
* **HandRaiser-style chunked interruption.** That is a multi-agent turn-taking
  mechanism, not a human-facing one (P1-14's own stated risk).

**Hard gates stay hard.** An emergency stop, an exception category, a critical
severity, quiet hours and the user's proactive preference are not trade-offs to be
weighed — they are rules the user declared, and they short-circuit the model. Only the
judgement *between* those rules is arithmetic now.

Calibration note: ``interruptibility == "unknown"`` resolves to ``P(receptive) = 0.50``
with half occupancy, which nets positive for an ``info`` notification — i.e. a system
with no situation model keeps delivering what it used to deliver. That is a deliberate
choice to hold behaviour constant, not an accident of the numbers, and
``test_an_unknown_situation_keeps_delivering_info`` pins it so a parameter change that
flips it fails loudly.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, ClassVar

from aegis_ai.personal_ai.storage import JsonStateFile, now_ms

logger = logging.getLogger("aegis_ai.personal_ai.interruption")

#: How much delivering a notification of this severity is worth.
#:
#: ``error`` and ``critical`` are **unreachable here by design** — the hard bypass in
#: :meth:`InterruptionController.decide` returns before the model is consulted. They are
#: listed anyway so the table stays complete if that bypass ever moves, and
#: ``test_the_bypass_makes_the_top_severities_unreachable`` records the coupling so the
#: entries are visibly intentional rather than silently dead.
_SEVERITY_VALUE: dict[str, float] = {
    "info": 0.30,
    "warning": 0.60,
    "error": 0.85,
    "critical": 1.00,
}

#: P(the user welcomes an interruption now | the situation's ``interruptibility``).
#:
#: The keys are exactly the values ``SituationModel`` can emit; a test discovers that
#: set from ``situation.py`` and asserts equality, so a new interruptibility value
#: cannot silently fall through to a default.
#:
#: ``unknown`` sits at 0.50 — a coin flip, not a licence. Treating "we do not know" as
#: "go ahead" is the ghost-field bug class: the honest value has to be its own entry
#: rather than a fallback that happens to read as permission.
_RECEPTIVITY: dict[str, float] = {
    "interruptible": 0.90,
    "important_only": 0.35,
    "batch_later": 0.20,
    "suppress": 0.05,
    "unknown": 0.50,
}

#: How absorbed the user is, 0 (idle) … 1 (fully occupied). Keys are the activity
#: labels ``SituationModel`` produces, including both spellings it uses for gaming
#: (``game`` from structured observations, ``gaming`` from a user-state payload).
_OCCUPANCY: dict[str, float] = {
    "sleeping": 1.00,
    "away": 0.90,
    "focused": 1.00,
    "meeting": 1.00,
    "presentation": 1.00,
    "gaming": 0.90,
    "game": 0.90,
    "watching_video": 0.80,
    "chatting": 0.50,
    "working": 0.30,
    "error_handling": 0.20,
}

#: Occupancy assumed when the activity label is one we have never seen. Half-occupied
#: is the neutral reading; it is not a safety default in either direction.
_DEFAULT_OCCUPANCY = 0.50

#: Scales occupancy into a cost. Calibrated so that an unknown situation still clears
#: the bar for an ``info`` notification (see the module docstring) while a focused user
#: does not. Changing it moves the deliver/defer line for every notification, so the
#: calibration test will fail and ask you to re-justify it.
_INTERRUPTION_COST_SCALE = 0.20

#: Discount applied when the attention signal says a device is actively in use. A
#: multiplier rather than a separate term: it qualifies receptivity, it does not stand
#: on its own.
_ATTENTION_PENALTY = 0.80


class InterruptionController:
    """Decides when notifications should be delivered or batched."""

    EXCEPTION_CATEGORIES: ClassVar[set[str]] = {"approval_required", "safety_warning", "deadline", "commitment_due", "recovery_needs_user"}

    def __init__(
        self,
        data_dir: str = "data/personal_ai",
        situation_model: Any = None,
        user_model_store: Any = None,
        commitment_manager: Any = None,
        audit_manager: Any = None,
    ) -> None:
        self._state_file = JsonStateFile(Path(data_dir) / "interruption.json", {"batched": [], "emergency_stop": False})
        self._situation_model = situation_model
        self._user_model_store = user_model_store
        self._commitment_manager = commitment_manager
        self._audit_manager = audit_manager
        self._state = self._state_file.load()

    def decide(self, notification: dict[str, Any]) -> dict[str, Any]:
        """Return the interruption decision for ``notification``.

        Hard gates first, then the expected-utility model. See the module docstring for
        why those two groups are not treated the same way.
        """
        # ── Hard gates: declared rules, not trade-offs ────────────────────────────
        if self._state.get("emergency_stop"):
            return self._decision("emergency_stop", "Emergency stop is active.")
        category = str(notification.get("category") or "general")
        severity = str(notification.get("severity") or "info")
        if category in self.EXCEPTION_CATEGORIES or severity in {"critical", "error"}:
            return self._decision("send_now", "Important notification bypasses suppression.")
        model = self._user_model_store.get() if self._user_model_store is not None and hasattr(self._user_model_store, "get") else None
        if model is not None:
            try:
                import time

                if model.is_quiet_now(time.localtime().tm_hour):
                    return self._decision("batch_later", "Quiet hours are active.")
                if not model.allows_proactive(category):
                    return self._decision("suppress", "UserModel does not allow this proactive category.")
            except Exception:
                # An unreadable user model means the quiet-hours check did not run.
                logger.debug("Failed to consult the user model", exc_info=True)

        # ── Expected utility of speaking now ─────────────────────────────────────
        situation = self._situation_model.get_state() if self._situation_model is not None else {}
        if not isinstance(situation, dict):
            situation = {}
        utility = self._expected_utility(severity, situation)

        verdict = "send_now" if utility["net"] > 0 else "batch_later"
        where = f"interruptibility={utility['interruptibility']}, activity={utility['activity']}"
        return self._decision(
            verdict,
            f"Expected utility {utility['net']:+.3f} ({'>' if verdict == 'send_now' else '<='} 0) "
            f"for {where}: benefit {utility['benefit']:.2f} x P(receptive) {utility['p_receptive']:.2f} "
            f"- cost {utility['cost']:.2f}.",
            utility=utility,
        )

    def _expected_utility(self, severity: str, situation: dict[str, Any]) -> dict[str, Any]:
        """Return the utility breakdown for interrupting now.

        ``net`` is the number the decision is the sign of. The other entries are the
        terms it was computed from, reported so the decision can be audited rather than
        taken on trust.
        """
        activity = situation.get("activity") if isinstance(situation.get("activity"), dict) else {}
        attention = situation.get("attention") if isinstance(situation.get("attention"), dict) else {}
        activity_label = str(activity.get("label") or situation.get("state") or "unknown")
        attention_label = str(attention.get("label") or "")
        mode = str(situation.get("interruptibility") or "unknown")

        benefit = _SEVERITY_VALUE.get(str(severity), _SEVERITY_VALUE["info"])

        occupancy = _OCCUPANCY.get(activity_label, _DEFAULT_OCCUPANCY)
        p_receptive = _RECEPTIVITY.get(mode, _RECEPTIVITY["unknown"]) * (1.0 - 0.5 * occupancy)
        if attention_label.endswith("_active"):
            p_receptive *= _ATTENTION_PENALTY

        cost = _INTERRUPTION_COST_SCALE * occupancy
        return {
            "benefit": benefit,
            "p_receptive": p_receptive,
            "cost": cost,
            "net": benefit * p_receptive - cost,
            "severity": str(severity),
            "interruptibility": mode,
            "activity": activity_label,
            "attention": attention_label,
            "occupancy": occupancy,
        }

    @staticmethod
    def _decision(decision: str, reason: str, utility: dict[str, Any] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"decision": decision, "reason": reason}
        if utility is not None:
            payload["utility"] = utility
        return payload

    def before_send(self, notification: dict[str, Any]) -> dict[str, Any]:
        decision = self.decide(notification)
        if decision["decision"] in {"batch_later", "suppress"}:
            self._state.setdefault("batched", []).append({"notification": notification, "decision": decision, "batched_at": now_ms()})
            self._save()
        self._audit("interruption_decision", {"notification_id": notification.get("notification_id"), **decision})
        return decision

    def flush_batch(self) -> list[dict[str, Any]]:
        items = list(self._state.get("batched", []))
        self._state["batched"] = []
        self._save()
        return items

    def set_emergency_stop(self, active: bool) -> dict[str, Any]:
        self._state["emergency_stop"] = bool(active)
        self._state["updated_at"] = now_ms()
        self._save()
        return self.get_status()

    def get_status(self) -> dict[str, Any]:
        return {
            "emergency_stop": bool(self._state.get("emergency_stop", False)),
            "batched_count": len(self._state.get("batched", [])),
            "batched": list(self._state.get("batched", []))[-20:],
        }

    def _save(self) -> None:
        self._state_file.save(self._state)

    def _audit(self, action: str, detail: dict[str, Any]) -> None:
        if self._audit_manager is None:
            return
        try:
            self._audit_manager.log_decision(action=action, actor="interruption_controller", decision="success", reason=action, detail=detail)
        except Exception:
            logger.debug("Failed to audit interruption decision %r", action, exc_info=True)
