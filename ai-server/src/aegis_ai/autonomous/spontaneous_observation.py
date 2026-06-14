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
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._last_observations: list[Observation] = []
        self._observation_history: list[dict[str, Any]] = []

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
        except Exception:
            pass

        # Check recent errors in logs
        try:
            log_dir = self._data_dir.parent / "logs"
            if log_dir.exists():
                for log_file in log_dir.glob("*.log"):
                    try:
                        content = log_file.read_text(encoding="utf-8", errors="ignore")
                        error_count = content.lower().count("error")
                        if error_count > 10:
                            obs.append(Observation(
                                observation_id=f"obs_{os.urandom(4).hex()}",
                                timestamp_ms=int(time.time() * 1000),
                                observation_type="warning", source="system",
                                description=f"High error count in {log_file.name}: {error_count} errors",
                                importance=0.7, novelty=0.4,
                                tags=["logs", "errors"],
                            ))
                    except Exception:
                        pass
        except Exception:
            pass

        # Check data directory size
        try:
            data_size = sum(f.stat().st_size for f in self._data_dir.rglob("*") if f.is_file())
            if data_size > 100 * 1024 * 1024:  # > 100MB
                obs.append(Observation(
                    observation_id=f"obs_{os.urandom(4).hex()}",
                    timestamp_ms=int(time.time() * 1000),
                    observation_type="warning", source="system",
                    description=f"Data directory large: {data_size // (1024*1024)}MB",
                    importance=0.4, novelty=0.2,
                    tags=["storage"],
                ))
        except Exception:
            pass

        return obs

    def _observe_memory_patterns(self) -> list[Observation]:
        """Observe patterns in memory systems."""
        obs: list[Observation] = []

        # Check for recent failures in action traces
        if self._action_trace:
            try:
                recent_failed = self._action_trace.get_failed(count=10)
                if len(recent_failed) >= 3:
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
            except Exception:
                pass

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
            except Exception:
                pass

        return obs

    def _observe_desires(self) -> list[Observation]:
        """Observe desire state changes."""
        obs: list[Observation] = []
        if not self._desire:
            return obs

        try:
            for name, desire in self._desire.get_all_desires().items():
                frustration = max(0, desire.expected_value - desire.value)
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
        except Exception:
            pass

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
        except Exception:
            pass

        return obs

    def _observe_capabilities(self) -> list[Observation]:
        """Observe capability availability."""
        obs: list[Observation] = []
        if not self._broker:
            return obs

        try:
            from tool_broker import ToolExecutionRequest, ExecutionSource
            # Check PC server
            request = ToolExecutionRequest(
                capability_id="pc-server.system.get_os_info", arguments={},
                source=ExecutionSource.SYSTEM, reason="Health check",
            )
            result = self._broker.execute(request)
            if not result.success:
                obs.append(Observation(
                    observation_id=f"obs_{os.urandom(4).hex()}",
                    timestamp_ms=int(time.time() * 1000),
                    observation_type="warning", source="capability",
                    description=f"PC Server capability unavailable: {result.error[:80]}",
                    importance=0.7, novelty=0.3,
                    tags=["capability", "pc_server"],
                ))
        except Exception:
            pass

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
                                tags=["task", "stuck"],
                            ))
            except Exception:
                pass

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
        except Exception:
            pass
