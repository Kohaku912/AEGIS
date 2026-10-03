"""Burden metric — how much lighter AEGIS made the user's life.

The metric is **judged by the judgment LLM** and **checked by the user periodically**;
the owner's definition is recorded in ``DELEGATION.md`` §4 item 8 and written out in
``docs/burden-metric.md``. See :mod:`aegis_ai.burden.metric` for why it is a judgement
rather than a formula over the decision log.
"""

from __future__ import annotations

from aegis_ai.burden.metric import (
    BURDEN_CHECK_CAPABILITY_ID,
    DEFAULT_ASK_INTERVAL_MS,
    JUDGMENT_PROFILE,
    VERDICT_CONFIRMED,
    VERDICT_CORRECTED,
    VERDICT_UNASKED,
    BurdenAssessment,
    BurdenMetric,
)

__all__ = [
    "BURDEN_CHECK_CAPABILITY_ID",
    "DEFAULT_ASK_INTERVAL_MS",
    "JUDGMENT_PROFILE",
    "VERDICT_CONFIRMED",
    "VERDICT_CORRECTED",
    "VERDICT_UNASKED",
    "BurdenAssessment",
    "BurdenMetric",
]
