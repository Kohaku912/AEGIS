"""Mind Layer — AEGIS's structured personality model.

Not sentient — persistent state that guides decision-making.
Does NOT override PolicyEngine safety decisions.

Components:
- Identity: who AEGIS is, values, policies
- Desire: priorities and motivations
- Emotion: urgency, confidence, fatigue proxies
- Goals: short-term, long-term, recurring goals with progress
- Priorities: dynamic priority calculation
"""

from aegis_ai.mind.desire import Desire  # noqa: F401
from aegis_ai.mind.emotion import Emotion  # noqa: F401
from aegis_ai.mind.goals import Goal, GoalManager, GoalStatus, GoalType  # noqa: F401
from aegis_ai.mind.identity import Identity  # noqa: F401
from aegis_ai.mind.priorities import PriorityEngine, PriorityScore  # noqa: F401
