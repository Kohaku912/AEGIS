"""Mind Layer — AEGIS's structured personality model.

Not sentient — persistent state that guides decision-making.
Does NOT override PolicyEngine safety decisions.

Components:
- Identity: who AEGIS is, values, policies
- Emotion: urgency, confidence, fatigue proxies
- Goals: short-term, long-term, recurring goals with progress

`Desire` and `Priorities` were deleted 2026-10-08 (`DELEGATION.md` §4 item 39):
nothing constructed them, and outside this file nothing imported them either.
"""

from aegis_ai.mind.emotion import Emotion  # noqa: F401
from aegis_ai.mind.goals import Goal, GoalManager, GoalStatus, GoalType  # noqa: F401
from aegis_ai.mind.identity import Identity  # noqa: F401
