"""The burden metric — how much lighter AEGIS made the user's life over a window.

**Owner definition (2026-10-03, ``DELEGATION.md`` §4 item 8).** The metric is **judged by
the judgment LLM** — ``profile="decision"``, the same profile the autonomous loop already
uses for its own judgements — from the period's activity, and the user is **asked to
confirm or correct it periodically**. The LLM's number is the *machine's* view; the user's
answer is the ground truth. The two are kept apart on purpose and neither overwrites the
other.

**Why it is a judgement and not a formula.** §3.1 hole 3 was the last north-star hole, and
``DECISION_DRAFTS.md`` §B-5 answered it with *"derive it from the existing decision log; no
new instrumentation is needed"*. Measured 2026-10-01, that premise holds for **one of the
three** proposed sub-metrics and fails for the other two:

1. interruptions per day — **computable** (``AuditEntry.timestamp_ms`` plus the
   ``interruption_decision`` action);
2. **the fraction the user responded to — not computable**: the response lives in
   ``NotificationManager._notifications`` (an in-memory dict), nothing persists it, and
   ``dismiss(notification_id)`` cannot tell the user's dismissal from the system's own;
3. median cost of accepted interruptions — computable only over the subset whose
   ``_decision(...)`` path carries a ``utility`` breakdown (**1 of 5**).

Those structural facts are still pinned by ``tests/test_burden_metric_has_no_instrument.py``
— that file is a measurement, and it is still true. What changed is the *conclusion*: rather
than persist a response and instrument four hard gates, the owner put the judgement where
AEGIS already puts judgements — the LLM — and made the user the check on it.

**What this module deliberately does not do.** It never reads the audit log, and it holds
no reference to ``aegis_ai.confirmation``. The caller assembles the period's activity and
passes it in, so there is no arithmetic over the decision log here to go stale; and the ask
is raised by the *asker* (``CoreCapabilities``, the only caller of
``ConfirmationStore.request``), never by this module — so this cannot become a second
approval surface. Both absences are pinned.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from typing import Any

logger = logging.getLogger("aegis_ai.burden.metric")

#: The judgment LLM. ``config/llm.yaml`` declares this profile, and the autonomous loop
#: already passes it at its own decision call sites — so the burden metric is judged by
#: the same mind that decides what AEGIS should do, rather than by a second, private one.
JUDGMENT_PROFILE = "decision"

#: How often the user is asked. The north star is *not* asking too much (C-1: "the cadence
#: bound is what keeps the burden from growing"), so this is a **floor** on how often, not
#: a target. A week is long enough that the answer is about a period rather than a moment,
#: and short enough that a wrong judgement cannot stand for a month.
DEFAULT_ASK_INTERVAL_MS = 7 * 24 * 60 * 60 * 1000

#: The capability id the ask is filed under, so the dashboard can group these questions
#: apart from action confirmations.
BURDEN_CHECK_CAPABILITY_ID = "burden_check"

#: The user's answer to a judgement. ``unasked`` is the state every fresh assessment is in.
VERDICT_UNASKED = "unasked"
VERDICT_CONFIRMED = "confirmed"
VERDICT_CORRECTED = "corrected"

_SYSTEM_PROMPT = (
    "You judge how much burden AEGIS removed from the user's life over a period.\n"
    "Return JSON only, with exactly these keys:\n"
    '  "score": number from 0.0 (removed nothing the user would have had to do) to 1.0\n'
    '           (removed essentially all of it),\n'
    '  "summary": one sentence the user will read,\n'
    '  "evidence": array of short strings, each naming one concrete thing AEGIS did and\n'
    "              the burden it stood in for.\n"
    "Judge only from the activity given. Do not invent work. If the activity is too thin\n"
    'to judge, say so in "summary" and return a score of 0.0 with an empty "evidence".'
)

_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


@dataclass
class BurdenAssessment:
    """One judgement of the burden removed over a window, plus the user's answer to it."""

    window_start_ms: int
    window_end_ms: int
    #: 0.0 .. 1.0, or ``None`` when the judgement failed outright.
    score: float | None = None
    summary: str = ""
    evidence: list[str] = field(default_factory=list)
    #: The **requested** profile …
    judged_by_profile: str = JUDGMENT_PROFILE
    #: … and the **resolved** provider and model. A label names the request, not the
    #: resolution: under the shipped allowlist (``api.typesafe.ai`` only) a
    #: ``decision``-profile call is denied by the gate and degrades to Mock, and the
    #: "judgement" is then not a judgement at all. These two fields are how that is
    #: visible instead of silent — see :meth:`is_trustworthy`.
    judged_by_provider: str = ""
    judged_by_model: str = ""
    error: str = ""
    #: The user's answer. Never overwrites ``score``; it is a separate verdict on it.
    user_verdict: str = VERDICT_UNASKED
    user_note: str = ""

    @property
    def is_trustworthy(self) -> bool:
        """False when the judgement did not come from a real provider.

        A Mock provider returns canned text, so an assessment it produced says nothing
        about the user's life. Callers should not ask the user about one.
        """
        return not self.error and self.judged_by_provider not in ("", "mock")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BurdenMetric:
    """Judges the burden AEGIS removed, and builds the question that checks the judgement.

    Deliberately not a `Protocol` implementation and not wired into the runtime by
    construction: the caller owns the cadence and the activity, so the same object can be
    driven by the autonomous loop, by a test, or by a one-off backfill.
    """

    def __init__(self, llm: Any, *, ask_interval_ms: int = DEFAULT_ASK_INTERVAL_MS) -> None:
        self._llm = llm
        self._ask_interval_ms = int(ask_interval_ms)

    @property
    def ask_interval_ms(self) -> int:
        return self._ask_interval_ms

    # ── the judgement ─────────────────────────────────────────────────────────

    @staticmethod
    def build_prompt(
        *,
        window_start_ms: int,
        window_end_ms: int,
        activity: list[str],
    ) -> str:
        """The user-turn prompt. Activity is *given*, never gathered here."""
        lines = [
            f"Period: {window_start_ms} to {window_end_ms} (epoch milliseconds).",
            "",
            "What AEGIS did in that period:",
        ]
        if activity:
            lines.extend(f"- {item}" for item in activity)
        else:
            lines.append("- (nothing recorded)")
        return "\n".join(lines)

    def assess(
        self,
        *,
        window_start_ms: int,
        window_end_ms: int,
        activity: list[str],
    ) -> BurdenAssessment:
        """Ask the judgment LLM how much burden was removed over the window.

        Never raises for an LLM failure: a failed judgement is recorded as one (``error``
        set, ``score`` ``None``), because a metric that throws is a metric nobody can
        aggregate.
        """
        prompt = self.build_prompt(
            window_start_ms=window_start_ms,
            window_end_ms=window_end_ms,
            activity=activity,
        )
        try:
            response = self._llm.generate(
                prompt=prompt,
                system_prompt=_SYSTEM_PROMPT,
                json_mode=True,
                temperature=0.0,
                profile=JUDGMENT_PROFILE,
            )
        except Exception as exc:  # a provider that raises is a failed judgement, not a crash
            logger.warning("Burden judgement failed: %s", exc)
            return BurdenAssessment(
                window_start_ms=window_start_ms,
                window_end_ms=window_end_ms,
                error=f"{type(exc).__name__}: {exc}",
            )

        assessment = BurdenAssessment(
            window_start_ms=window_start_ms,
            window_end_ms=window_end_ms,
            # the *resolved* values, not the requested profile
            judged_by_provider=str(getattr(response, "provider_used", "") or ""),
            judged_by_model=str(getattr(response, "model_used", "") or ""),
        )

        if not getattr(response, "success", True):
            assessment.error = str(getattr(response, "error", "") or "provider reported failure")
            return assessment

        parsed = self._parse(getattr(response, "content", "") or "")
        if parsed is None:
            assessment.error = "the judgement was not JSON"
            return assessment

        assessment.summary = str(parsed.get("summary") or "")
        assessment.evidence = [str(item) for item in (parsed.get("evidence") or [])]
        try:
            assessment.score = min(1.0, max(0.0, float(parsed.get("score"))))
        except (TypeError, ValueError):
            assessment.error = "the judgement carried no numeric score"
        return assessment

    @staticmethod
    def _parse(content: str) -> dict[str, Any] | None:
        """Tolerant JSON extraction — models wrap JSON in prose or fences."""
        try:
            loaded = json.loads(content)
            return loaded if isinstance(loaded, dict) else None
        except (TypeError, ValueError):
            pass
        match = _JSON_OBJECT.search(content)
        if not match:
            return None
        try:
            loaded = json.loads(match.group(0))
        except ValueError:
            return None
        return loaded if isinstance(loaded, dict) else None

    # ── the periodic check on the judgement ───────────────────────────────────

    def due_for_user_check(self, *, last_ask_ms: int | None, now_ms: int) -> bool:
        """Whether the user should be asked to confirm the latest judgement.

        ``last_ask_ms`` is ``None`` on a first run, which is *not* due — the first
        judgement should exist before the user is asked about one.
        """
        if last_ask_ms is None:
            return False
        return now_ms - int(last_ask_ms) >= self._ask_interval_ms

    @staticmethod
    def build_user_question(assessment: BurdenAssessment) -> dict[str, Any]:
        """The fields the **asker** hands to ``ConfirmationStore.request``.

        Returned as a plain dict and not raised here: raising a confirmation is the
        asker's job (``CoreCapabilities``), and this module must not become a second
        approval surface. ``test_burden_metric_is_judged.py`` asserts every key is one
        ``ConfirmationRequest`` actually declares, so the two cannot drift apart.
        """
        return {
            "capability_id": BURDEN_CHECK_CAPABILITY_ID,
            "summary": "Did AEGIS make this period lighter for you?",
            "reason": assessment.summary
            or "AEGIS judged how much burden it removed and wants you to check that.",
            "preview": json.dumps(assessment.to_dict(), ensure_ascii=False),
            "expected_effect": "Your answer becomes the ground truth for the burden metric.",
            "side_effects": [],
        }

    @staticmethod
    def apply_user_verdict(
        assessment: BurdenAssessment,
        *,
        verdict: str,
        note: str = "",
    ) -> BurdenAssessment:
        """Record the user's answer *beside* the judgement, never over it.

        The LLM's ``score`` is kept even when the user corrects it: the gap between the
        two is the thing worth watching, and overwriting one with the other would destroy
        exactly that signal.
        """
        if verdict not in (VERDICT_CONFIRMED, VERDICT_CORRECTED):
            raise ValueError(f"unknown verdict {verdict!r}")
        assessment.user_verdict = verdict
        assessment.user_note = note
        return assessment
