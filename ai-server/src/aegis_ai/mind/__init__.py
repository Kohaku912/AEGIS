"""Mind Layer — AEGIS's structured personality model.

Not sentient — persistent state that guides decision-making.
Does NOT override PolicyEngine safety decisions.

Components:
- Identity: who AEGIS is, values, policies
- Mood / Personality / LayeredEmotion / AffectSystem: the affect chain, live through
  `AffectSystem` (`runtime.py`, `llm/memory_context.py`) — not re-exported here

`Desire`, `Priorities`, `SocialIntelligence`, `Emotion` and `Goals` were deleted
2026-10-08 (`DELEGATION.md` §4 item 39): nothing constructed them, and outside this
package nothing imported them either.
"""

from aegis_ai.mind.identity import Identity  # noqa: F401
