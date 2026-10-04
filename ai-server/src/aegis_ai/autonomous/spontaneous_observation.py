"""Spontaneous Observation System — Self-initiated environmental awareness.

AEGIS periodically observes its environment without being asked:
- System state changes (new files, processes, errors)
- Unfinished tasks and pending items
- Memory patterns (recent failures, unresolved questions)
- Emotional state shifts
- Desire fluctuations
- Capability availability changes
- Interesting anomalies

Detects: important changes, oddities, unresolved problems, interesting targets.

Safety: Observations are read-only. Any action requiring side effects
goes through PolicyEngine and approval flow.

Usage:
    sos = SpontaneousObservationSystem(llm=llm, broker=broker, ...)
    observations = sos.observe()
    # → [Observation(type="anomaly", description="...", importance=0.8)]
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.autonomous.spontaneous_observation")


@dataclass
class Observation:
    """A single observation."""
    observation_id: str = ""
    timestamp_ms: int = 0
    observation_type: str = "general"  # anomaly, change, unresolved, interesting, warning
    source: str = ""                    # system, memory, desire, emotion, capability, task
    description: str = ""
    importance: float = 0.5            # 0.0 (trivial) to 1.0 (critical)
    novelty: float = 0.5              # 0.0 (routine) to 1.0 (never seen before)
    actionable: bool = False           # Whether this requires action
    suggested_action: str = ""
    related_desire: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "timestamp_ms": self.timestamp_ms,
            "observation_type": self.observation_type,
            "source": self.source, "description": self.description,
            "importance": self.importance, "novelty": self.novelty,
            "actionable": self.actionable, "suggested_action": self.suggested_action,
            "related_desire": self.related_desire, "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Observation:
        return cls(
            observation_id=data.get("observation_id", ""),
            timestamp_ms=int(data.get("timestamp_ms", 0)),
            observation_type=data.get("observation_type", "general"),
            source=data.get("source", ""), description=data.get("description", ""),
            importance=float(data.get("importance", 0.5)),
            novelty=float(data.get("novelty", 0.5)),
            actionable=bool(data.get("actionable", False)),
            suggested_action=data.get("suggested_action", ""),
            related_desire=data.get("related_desire", ""),
            tags=data.get("tags", []),
        )


class SpontaneousObservationSystem:
    """Self-initiated environmental awareness for AEGIS.

    Periodically observes:
    1. System state (disk, memory, processes, errors)
    2. Unfinished tasks and pending items
    3. Memory patterns (recent failures, unresolved questions)
    4. Emotional state shifts
    5. Desire fluctuations
    6. Capability availability
    7. Anomalies and interesting patterns

    All observations are read-only. Actions go through PolicyEngine.
    """

    def __init__(
        self,
        llm: Any = None,
        broker: Any = None,
        desire_system: Any = None,
        affect_system: Any = None,
        episodic_memory: Any = None,
        semantic_memory: Any = None,
        person_memory: Any = None,
        action_trace: Any = None,
        status_manager: Any = None,
        task_manager: Any = None,
        agent_state: Any = None,
        user_state_manager: Any = None,
        data_dir: str = "data/autonomous",
    ) -> None:
        self._llm = llm
        self._broker = broker
        self._desire = desire_system
        self._affect = affect_system
        self._episodic = episodic_memory
        self._semantic = semantic_memory
        self._person = person_memory
        self._action_trace = action_trace
        self._status_manager = status_manager
        self._task_manager = task_manager
        self._agent_state = agent_state
        self._user_state_manager = user_state_manager
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._last_observations: list[Observation] = []
        self._observation_history: list[dict[str, Any]] = []
        self._observed_server_states: dict[str, str] = {}
        self._observed_desire_bands: dict[str, str] = {}
        self._observed_failure_signature: tuple[str, ...] | None = None
        self._last_data_size_check_ms = 0
        self._last_data_size_bytes: int | None = None

    def observe(self) -> list[Observation]:
        """Run a full observation cycle.

        Returns list of observations sorted by importance.
        """
        observations: list[Observation] = []

        # 1. System state observations
        observations.extend(self._observe_system_state())

        # 2. Memory pattern observations
        observations.extend(self._observe_memory_patterns())

        # 3. Desire state observations
        observations.extend(self._observe_desires())

        # 4. Emotional state observations
        observations.extend(self._observe_emotions())

        # 5. Capability observations
        observations.extend(self._observe_capabilities())

        # 6. Unfinished task observations
        observations.extend(self._observe_unfinished_tasks())

        # 7. Manager work queues (approvals, obligations, waiting tasks)
        observations.extend(self._observe_manager_work())

        # Sort by importance
        observations.sort(key=lambda o: o.importance, reverse=True)

        self._last_observations = observations
        self._log_observations(observations)

        logger.info("Observation cycle: %d observations", len(observations))
        return observations

    def _observe_system_state(self) -> list[Observation]:
        """Observe system state changes."""
        obs: list[Observation] = []

        # Check disk usage
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_pct = free / total
            if free_pct < 0.1:
                obs.append(Observation(
                    observation_id=f"obs_{os.urandom(4).hex()}",
                    timestamp_ms=int(time.time() * 1000),
                    observation_type="warning", source="system",
                    description=f"Disk space low: {free_pct:.0%} free ({free // (1024**3)}GB)",
                    importance=0.9, novelty=0.3, actionable=True,
                    suggested_action="Clean up old logs and temporary files",
                    tags=["disk", "warning"],
                ))
            elif free_pct < 0.2:
                obs.append(Observation(
                    observation_id=f"obs_{os.urandom(4).hex()}",
                    timestamp_ms=int(time.time() * 1000),
                    observation_type="warning", source="system",
                    description=f"Disk space moderate: {free_pct:.0%} free",
                    importance=0.5, novelty=0.2,
                    tags=["disk"],
                ))
        except Exception as exc:
            logger.warning(
                "Could not read disk usage (%s: %s); no disk-space observation is "
                "produced, so an unreadable disk looks like a healthy one.",
                type(exc).__name__, exc,
            )

        # Storage is a change signal, not a reason to rescan and re-emit the
        # same warning every minute. HealthAlertManager owns absolute limits.
        now_ms = int(time.time() * 1000)
        if now_ms - self._last_data_size_check_ms >= 15 * 60 * 1000:
            self._last_data_size_check_ms = now_ms
            try:
                data_size = sum(
                    item.stat().st_size
                    for item in self._data_dir.rglob("*")
                    if item.is_file()
                )
                previous_size = self._last_data_size_bytes
                self._last_data_size_bytes = data_size
                growth_threshold = max(
                    100 * 1024 * 1024,
                    int((previous_size or 0) * 0.1),
                )
                if (
                    previous_size is not None
                    and data_size - previous_size >= growth_threshold
                ):
                    obs.append(
                        Observation(
                            observation_id=f"obs_{os.urandom(4).hex()}",
                            timestamp_ms=now_ms,
                            observation_type="change",
                            source="system",
                            description=(
                                "Autonomous data grew by "
                                f"{(data_size - previous_size) // (1024 * 1024)}MB"
                            ),
                            importance=0.7,
                            novelty=0.8,
                            actionable=True,
                            suggested_action="Inspect the growth source and bound retention.",
                            tags=["storage", "growth"],
                        )
                    )
            except Exception as exc:
                logger.warning(
                    "Could not measure autonomous data growth (%s: %s); no growth "
                    "observation is produced, so unreadable storage looks unchanged. "
                    "The 15-minute check window was already consumed, so growth stays "
                    "unchecked until the next window.",
                    type(exc).__name__, exc,
                )

        return obs

    def _observe_memory_patterns(self) -> list[Observation]:
        """Observe patterns in memory systems."""
        obs: list[Observation] = []

        # Check for recent failures in action traces
        if self._action_trace:
            try:
                recent_failed = self._action_trace.get_failed(count=10)
                failure_signature = tuple(
                    str(trace.trace_id)
                    for trace in recent_failed
                    if getattr(trace, "trace_id", "")
                )
                previous_signature = self._observed_failure_signature
                self._observed_failure_signature = failure_signature
                if (
                    len(recent_failed) >= 3
                    and previous_signature != failure_signature
                ):
                    goals = [t.goal[:40] for t in recent_failed[:3]]
                    obs.append(Observation(
                        observation_id=f"obs_{os.urandom(4).hex()}",
                        timestamp_ms=int(time.time() * 1000),
                        observation_type="unresolved", source="memory",
                        description=f"Pattern of failures detected: {', '.join(goals)}",
                        importance=0.8, novelty=0.6, actionable=True,
                        suggested_action="Analyze failure patterns and adjust approach",
                        tags=["failure_pattern", "learning"],
                    ))
            except Exception as exc:
                logger.warning(
                    "Could not read failed action traces (%s: %s); no failure-pattern "
                    "observation is produced, so an unreadable trace store looks like a "
                    "system with no failures.",
                    type(exc).__name__, exc,
                )

        # Check episodic memory for unresolved episodes
        if self._episodic:
            try:
                recent = self._episodic.recall_recent(20)
                negative = [ep for ep in recent if ep.valence < -0.3 and not ep.lesson]
                if negative:
                    obs.append(Observation(
                        observation_id=f"obs_{os.urandom(4).hex()}",
                        timestamp_ms=int(time.time() * 1000),
                        observation_type="unresolved", source="memory",
                        description=f"{len(negative)} negative episodes without lessons extracted",
                        importance=0.6, novelty=0.4, actionable=True,
                        suggested_action="Extract lessons from negative episodes",
                        tags=["memory", "lessons"],
                    ))
            except Exception as exc:
                logger.warning(
                    "Could not recall recent episodes (%s: %s); no unresolved-episode "
                    "observation is produced, so an unreadable episodic store looks like "
                    "a store with nothing unresolved.",
                    type(exc).__name__, exc,
                )

        return obs

    def _observe_desires(self) -> list[Observation]:
        """Observe desire state changes."""
        obs: list[Observation] = []
        if not self._desire:
            return obs

        try:
            for name, desire in self._desire.get_all_desires().items():
                frustration = max(0, desire.expected_value - desire.value)
                band = "high" if frustration > 4.0 else "normal"
                previous_band = self._observed_desire_bands.get(name)
                self._observed_desire_bands[name] = band
                if previous_band == band:
                    continue
                if frustration > 4.0:
                    obs.append(Observation(
                        observation_id=f"obs_{os.urandom(4).hex()}",
                        timestamp_ms=int(time.time() * 1000),
                        observation_type="warning", source="desire",
                        description=f"High frustration: {name}={desire.value:.1f} (expected {desire.expected_value:.1f}, gap={frustration:.1f})",
                        importance=min(1.0, frustration / 5.0), novelty=0.3,
                        actionable=True, related_desire=name,
                        suggested_action=f"Take action to fulfill {name} desire",
                        tags=["desire", "frustration"],
                    ))
        except Exception as exc:
            logger.warning(
                "Could not read desires (%s: %s); no frustration observation is "
                "produced, so an unreadable desire system looks like a system with no "
                "unmet desires.",
                type(exc).__name__, exc,
            )

        return obs

    def _observe_emotions(self) -> list[Observation]:
        """Observe emotional state."""
        obs: list[Observation] = []
        if not self._affect:
            return obs

        try:
            mood = self._affect.mood
            if mood.valence < -0.5:
                obs.append(Observation(
                    observation_id=f"obs_{os.urandom(4).hex()}",
                    timestamp_ms=int(time.time() * 1000),
                    observation_type="warning", source="emotion",
                    description=f"Negative mood detected: {mood.label} (valence={mood.valence:.2f})",
                    importance=0.6, novelty=0.3,
                    tags=["mood", "negative"],
                ))

            dominant = self._affect.emotion.get_dominant_emotion()
            if dominant and dominant.current_intensity > 0.7:
                obs.append(Observation(
                    observation_id=f"obs_{os.urandom(4).hex()}",
                    timestamp_ms=int(time.time() * 1000),
                    observation_type="interesting", source="emotion",
                    description=f"Strong emotion: {dominant.emotion_type.value} ({dominant.current_intensity:.2f}) - {dominant.trigger[:60]}",
                    importance=0.5, novelty=0.5,
                    tags=["emotion", "intense"],
                ))
        except Exception as exc:
            logger.warning(
                "Could not read the affect state (%s: %s); no mood or emotion "
                "observation is produced, so an unreadable affect system looks like a "
                "calm one.",
                type(exc).__name__, exc,
            )

        return obs

    def _observe_capabilities(self) -> list[Observation]:
        obs: list[Observation] = []
        if self._status_manager is None:
            return obs
        try:
            snapshot = self._status_manager.get_snapshot()
        except Exception as exc:
            logger.warning(
                "Could not read the shared server status (%s: %s); no capability "
                "observation is produced and no server state is recorded, so an "
                "unreadable status manager looks like a fleet with no status changes.",
                type(exc).__name__, exc,
            )
            return obs
        for server_id, state in snapshot.items():
            status = str(state.get("status") or "unknown").lower()
            previous_status = self._observed_server_states.get(server_id)
            self._observed_server_states[server_id] = status
            if (
                previous_status is None
                or previous_status == status
                or status not in {"offline", "degraded"}
            ):
                continue
            obs.append(
                Observation(
                    observation_id=f"obs_{os.urandom(4).hex()}",
                    timestamp_ms=int(time.time() * 1000),
                    observation_type="warning",
                    source="capability",
                    description=f"{server_id} status changed to {status}",
                    importance=0.8,
                    novelty=0.8,
                    actionable=True,
                    suggested_action="Inspect the shared server status and repair the connection.",
                    tags=["capability", server_id, status],
                )
            )

        return obs

    def _observe_unfinished_tasks(self) -> list[Observation]:
        """Observe unfinished tasks."""
        obs: list[Observation] = []

        # Check for active action traces
        if self._action_trace:
            try:
                active = [t for t in self._action_trace._active.values()]
                if active:
                    for trace in active[:3]:
                        age_min = (time.time() * 1000 - trace.started_at_ms) / 60000
                        if age_min > 10:
                            obs.append(Observation(
                                observation_id=f"obs_{os.urandom(4).hex()}",
                                timestamp_ms=int(time.time() * 1000),
                                observation_type="unresolved", source="task",
                                description=f"Long-running task ({age_min:.0f}min): {trace.goal[:60]}",
                                importance=0.6, novelty=0.3,
                                actionable=True,
                                suggested_action="Inspect or resume the stuck task",
                                tags=["task", "stuck", "incident"],
                            ))
            except Exception as exc:
                logger.warning(
                    "Could not read active action traces (%s: %s); no stuck-task "
                    "observation is produced, so an unreadable trace store looks like a "
                    "system with no stuck tasks.",
                    type(exc).__name__, exc,
                )

        return obs

    def _observe_manager_work(self) -> list[Observation]:
        """Emit bounded observations from live managers every cycle (not only on change)."""
        obs: list[Observation] = []
        now_ms = int(time.time() * 1000)

        if self._agent_state is not None:
            try:
                obligations = self._agent_state.snapshot("observation").obligations
                if obligations:
                    first = obligations[0]
                    summary = getattr(first, "summary", None) or str(first)
                    obs.append(
                        Observation(
                            observation_id=f"obs_{os.urandom(4).hex()}",
                            timestamp_ms=now_ms,
                            observation_type="unresolved",
                            source="obligation",
                            description=f"{len(obligations)} open obligation(s): {str(summary)[:120]}",
                            importance=0.9,
                            novelty=0.3,
                            actionable=True,
                            suggested_action="Resolve the highest-priority open obligation",
                            related_desire="user_support",
                            tags=["obligation", "incident"],
                        )
                    )
            except Exception:
                logger.debug("Obligation observation failed", exc_info=True)

        if self._task_manager is not None:
            try:
                waiting = []
                if hasattr(self._task_manager, "list_tasks"):
                    waiting = [
                        t
                        for t in (self._task_manager.list_tasks() or [])
                        if str(getattr(t, "status", getattr(t, "state", "")) or "").lower()
                        # "waiting_approval" / "wait_for_approval" were removed together
                        # with the approval flow (2026-09-27). No task can hold those
                        # statuses any more, so matching on them could never succeed.
                        in {"paused", "waiting"}
                    ][:5]
                elif hasattr(self._task_manager, "get_waiting"):
                    waiting = list(self._task_manager.get_waiting() or [])[:5]
                if waiting:
                    obs.append(
                        Observation(
                            observation_id=f"obs_{os.urandom(4).hex()}",
                            timestamp_ms=now_ms,
                            observation_type="unresolved",
                            source="task",
                            description=f"{len(waiting)} task(s) waiting to resume",
                            importance=0.8,
                            novelty=0.2,
                            actionable=True,
                            suggested_action="Digest waiting tasks for the user",
                            related_desire="user_support",
                            tags=["task", "approval", "incident"],
                        )
                    )
            except Exception:
                logger.debug("Task manager observation failed", exc_info=True)

        if self._user_state_manager is not None:
            try:
                ctx = ""
                if hasattr(self._user_state_manager, "to_context_string"):
                    ctx = str(self._user_state_manager.to_context_string() or "")
                label = ""
                if hasattr(self._user_state_manager, "get_current_user_state"):
                    state = self._user_state_manager.get_current_user_state() or {}
                    activity = state.get("activity") if isinstance(state.get("activity"), dict) else {}
                    label = str(activity.get("label") or "")
                if ctx and "unknown" not in ctx.lower():
                    sleeping = label == "sleeping"
                    focused = label in {"gaming", "watching_video", "focused"}
                    interruptible = not sleeping and not focused and label != "away"
                    tags = ["user_state"]
                    if interruptible:
                        tags.append("event")
                    obs.append(
                        Observation(
                            observation_id=f"obs_{os.urandom(4).hex()}",
                            timestamp_ms=now_ms,
                            observation_type="interesting",
                            source="user_state",
                            description=f"User situation: {ctx[:160]}",
                            importance=0.45 if sleeping else (0.72 if focused else 0.78),
                            novelty=0.15,
                            actionable=not sleeping,
                            suggested_action=(
                                "Stay quiet unless something important needs the user."
                                if sleeping or focused
                                else "Act on the current situation with a concrete capability."
                            ),
                            related_desire="user_support",
                            tags=tags,
                        )
                    )
                    if interruptible and self._desire is not None and hasattr(self._desire, "accumulate_pressure"):
                        self._desire.accumulate_pressure("user_support", 0.5, "user_situation")
            except Exception:
                logger.debug("User state observation failed", exc_info=True)

        # Room unconfigured: surface as attention, not pressure driver.
        for server_id, env_flag in (
            ("room-server", "ROOM_SERVER_ENABLED"),
        ):
            raw = os.environ.get(env_flag, "true").strip().lower()
            if raw in {"0", "false", "no", "off", "disabled", "unconfigured"}:
                obs.append(
                    Observation(
                        observation_id=f"obs_{os.urandom(4).hex()}",
                        timestamp_ms=now_ms,
                        observation_type="interesting",
                        source="health",
                        description=f"{server_id} is unconfigured/disabled — not a failure",
                        importance=0.2,
                        novelty=0.0,
                        actionable=False,
                        tags=["health", "unconfigured", server_id],
                    )
                )

        return obs

    def get_last_observations(self) -> list[Observation]:
        return self._last_observations

    def get_actionable_observations(self) -> list[Observation]:
        return [o for o in self._last_observations if o.actionable]

    def _log_observations(self, observations: list[Observation]) -> None:
        log_path = self._data_dir / "observation_log.jsonl"
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                entry = {
                    "timestamp_ms": int(time.time() * 1000),
                    "count": len(observations),
                    "observations": [o.to_dict() for o in observations[:10]],
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as exc:
            logger.warning(
                "Could not append to the observation log at %s (%s: %s); the run leaves "
                "no record on disk, so an unwritable log looks like a system that never "
                "observes.",
                log_path, type(exc).__name__, exc,
            )
