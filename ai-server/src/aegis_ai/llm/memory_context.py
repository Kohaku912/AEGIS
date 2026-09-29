"""Shared memory context assembly for LLM decision and summary tasks."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("aegis_ai.llm.memory_context")


@dataclass
class MemoryContextResult:
    """Shared memory context plus audit-friendly metadata."""

    profile: str
    text: str
    source_counts: dict[str, int] = field(default_factory=dict)
    section_names: list[str] = field(default_factory=list)

    def audit_detail(self) -> dict[str, Any]:
        memory_tokens = max(0, (len(self.text) + 3) // 4)
        return {
            "memory_profile": self.profile,
            "memory_sources": dict(self.source_counts),
            "memory_sections": list(self.section_names),
            "memory_context_chars": len(self.text),
            "memory_budget_tokens": memory_tokens,
            "memory_top_k": sum(self.source_counts.values()),
            "memory_reason": f"shared memory context for {self.profile}",
            "context_tokens": {"memory": memory_tokens},
        }


def _strip_system_reminders(text: str) -> str:
    return re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.DOTALL).strip()


def _truncate(text: str, limit: int = 220) -> str:
    compact = " ".join(text.replace("\r\n", "\n").replace("\r", "\n").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def _load_jsonl_records(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    if limit is None:
        limit = 50
    try:
        from aegis_ai.jsonl_tail import read_jsonl_tail

        return read_jsonl_tail(path, limit)
    except Exception as exc:
        logger.debug("Failed to load JSONL %s: %s", path, exc)
        return []


def _personal_data_lines(data_dir: Path, limit: int = 8) -> tuple[list[str], int]:
    """Read recent PDC titles/facts without constructing PersonalDataCore."""
    db = data_dir / "personal_data" / "core.db"
    if not db.exists():
        return [], 0
    try:
        import sqlite3

        conn = sqlite3.connect(str(db), check_same_thread=False)
        try:
            facts = conn.execute(
                "SELECT statement FROM facts ORDER BY timestamp_ms DESC LIMIT 5"
            ).fetchall()
            events = conn.execute(
                "SELECT event_type, title FROM events ORDER BY timestamp_ms DESC LIMIT ?",
                (limit,),
            ).fetchall()
        finally:
            conn.close()
    except Exception as exc:
        logger.debug("Personal data context failed: %s", exc)
        return [], 0
    lines = ["RECENT PERSONAL DATA:"]
    for row in facts:
        statement = str(row[0] or "").strip()
        if statement:
            lines.append(f"- fact: {_truncate(statement, 160)}")
    for event_type, title in events:
        lines.append(f"- {event_type}: {_truncate(str(title or ''), 140)}")
    count = len(facts) + len(events)
    if count == 0:
        return [], 0
    return lines, count


def _recent_execution_lines(data_dir: Path, limit: int = 6) -> tuple[list[str], int, list[str]]:
    entries = _load_jsonl_records(data_dir / "autonomous" / "execution_log.jsonl", limit=limit)
    lines: list[str] = []
    failure_fingerprints: list[str] = []
    for entry in reversed(entries):
        tasks = entry.get("tasks", [])
        results = entry.get("results", [])
        for idx, task in enumerate(tasks):
            result = results[idx] if idx < len(results) else {}
            action = task.get("action", "")
            cap_id = task.get("capability_id", "")
            success = result.get("success", False)
            result_text = _truncate(str(result.get("result", "")), 120)
            status = "ok" if success else "failed"
            lines.append(f"- [{status}] {action or cap_id}: {result_text}")
            if not success:
                fingerprint = cap_id or action
                if fingerprint:
                    failure_fingerprints.append(fingerprint)
    counts: dict[str, int] = {}
    for fingerprint in failure_fingerprints:
        counts[fingerprint] = counts.get(fingerprint, 0) + 1
    repeated = [f"{fp} x{count}" for fp, count in counts.items() if count >= 2]
    return lines[:limit], len(lines), repeated[:5]


def _action_trace_lines(data_dir: Path, limit: int = 3) -> tuple[list[str], int]:
    try:
        from aegis_ai.memory.action_trace import ActionTraceMemory

        memory = ActionTraceMemory(path=str(data_dir / "memory" / "action_traces.jsonl"))
        failed = memory.get_failed(count=limit)
        successful = memory.get_successful(count=limit)
    except Exception as exc:
        logger.debug("ActionTrace load failed: %s", exc)
        return [], 0

    lines: list[str] = []
    for trace in failed:
        lines.append(f"- [failed] {trace.goal}: {_truncate(trace.failure_reason or trace.result_summary, 140)}")
    for trace in successful[: max(0, limit - len(lines))]:
        lines.append(f"- [ok] {trace.goal}: {_truncate(trace.result_summary, 140)}")
    return lines, len(failed) + len(successful)


def _resolve_memory_store(data_dir: Path) -> Any:
    expected_dir = (data_dir / "memory_store").resolve()
    try:
        from aegis_ai.runtime import peek_runtime

        runtime = peek_runtime()
        manager = getattr(runtime, "memory_manager", None) if runtime is not None else None
        store = manager.get_backend("store") if manager is not None and hasattr(manager, "get_backend") else None
        runtime_dir = Path(getattr(store, "_data_dir", "")) if store is not None else None
        if store is not None and runtime_dir is not None:
            try:
                if runtime_dir.resolve() == expected_dir:
                    return store
            except OSError:
                logger.debug("MemoryStore runtime path resolution failed", exc_info=True)
        if store is not None and not getattr(store, "_data_dir", None):
            return store
    except Exception as exc:
        logger.debug("Runtime MemoryStore lookup failed: %s", exc)
    from aegis_ai.memory.memory_store import MemoryStore

    return MemoryStore(data_dir=str(expected_dir))


def _resolve_skill_memory(data_dir: Path) -> Any:
    """Prefer the MemoryManager-owned SkillMemory; fall back to a direct reader.

    Architecture invariant: memory backends are accessed through
    ``runtime.memory_manager.get_backend()``. Only when the runtime is absent
    (or points at a different data directory) do we open the JSONL directly.
    """
    expected_path = (data_dir / "memory" / "skills.jsonl").resolve()
    try:
        from aegis_ai.runtime import peek_runtime

        runtime = peek_runtime()
        manager = getattr(runtime, "memory_manager", None) if runtime is not None else None
        backend = manager.get_backend("skill") if manager is not None and hasattr(manager, "get_backend") else None
        if backend is not None:
            backend_path = getattr(backend, "_path", None)
            if backend_path is None:
                return backend
            try:
                if Path(backend_path).resolve() == expected_path:
                    return backend
            except OSError:
                logger.debug("Skill memory runtime path resolution failed", exc_info=True)
    except Exception as exc:
        logger.debug("Runtime SkillMemory lookup failed: %s", exc)

    from aegis_ai.memory.skill_memory import SkillMemory

    return SkillMemory(path=str(expected_path))


def _memory_store_lines(data_dir: Path, query: str, profile: str) -> tuple[list[str], dict[str, int]]:
    try:
        store = _resolve_memory_store(data_dir)
    except Exception as exc:
        logger.debug("MemoryStore load failed: %s", exc)
        return [], {}

    lines: list[str] = []
    counts: dict[str, int] = {}

    def _append_records(title: str, memory_type: str, limit: int, min_importance: float = 0.0) -> None:
        records = store.search_memories(
            query=query,
            memory_type=memory_type,
            min_importance=min_importance,
            limit=limit,
        )
        if not records and query:
            records = store.search_memories(
                memory_type=memory_type,
                min_importance=min_importance,
                limit=limit,
            )
        if not records:
            return
        counts[memory_type] = len(records)
        lines.append(title)
        for record in records:
            lines.append(f"- {record.to_context_string(180)}")

    _append_records("Failure lessons:", "failure_lesson", 3, min_importance=0.4)
    _append_records("Approval lessons:", "approval_lesson", 2, min_importance=0.4)
    _append_records("Desire lessons:", "desire_lesson", 4, min_importance=0.3)
    if profile == "decision":
        _append_records("User preferences:", "user_preference", 3)
    return lines, counts


def _user_understanding_lines(data_dir: Path, query: str) -> tuple[list[str], int]:
    try:
        from aegis_ai.runtime import peek_runtime
        from aegis_ai.user_understanding import UserUnderstandingStore

        runtime = peek_runtime()
        snapshot: dict[str, Any] = {}
        service = getattr(runtime, "user_understanding_service", None) if runtime is not None else None
        if service is not None and hasattr(service, "build_snapshot"):
            built = service.build_snapshot(query)
            if hasattr(built, "to_dict"):
                snapshot = built.to_dict()
            elif isinstance(built, dict):
                snapshot = dict(built)
        if not snapshot:
            snapshot = UserUnderstandingStore(data_dir / "user_understanding").load()
    except Exception as exc:
        logger.debug("User understanding context failed: %s", exc)
        return [], 0
    if not snapshot:
        return [], 0
    lines = ["USER UNDERSTANDING:"]
    if snapshot.get("summary"):
        lines.append(f"- summary: {_truncate(str(snapshot.get('summary') or ''), 180)}")
    for item in list(snapshot.get("likely_next_actions") or [])[:3]:
        lines.append(
            f"- next: {_truncate(str(item.get('title') or ''), 80)} :: "
            f"{_truncate(str(item.get('summary') or ''), 100)}"
        )
    for item in list(snapshot.get("predicted_deficits") or [])[:3]:
        lines.append(
            f"- deficit: {_truncate(str(item.get('title') or ''), 80)} :: "
            f"{_truncate(str(item.get('summary') or ''), 100)}"
        )
    authority = snapshot.get("delegated_authority_state", {})
    if isinstance(authority, dict) and authority.get("summary"):
        lines.append(f"- authority: {_truncate(str(authority.get('summary') or ''), 120)}")
    count = len(lines) - 1
    return lines, count


def build_shared_memory_context(
    *,
    query: str,
    data_dir: str,
    profile: str = "decision",
    has_social_actions: bool = True,
) -> MemoryContextResult:
    """Build shared memory context for LLM decision or summary calls."""

    root = Path(data_dir)
    normalized_query = query.strip()
    sections: list[str] = []
    source_counts: dict[str, int] = {}
    section_names: list[str] = []

    def add_section(name: str, content: str, count: int) -> None:
        content = content.strip()
        if not content:
            return
        sections.append(content)
        section_names.append(name)
        source_counts[name] = count

    try:
        from aegis_ai.desire.desire_system import DesireSystem

        desire_system = DesireSystem(data_dir=str(root / "desires"))
        desire_context = desire_system.to_context_string() if profile == "summary" else desire_system.get_context()
        if desire_context:
            add_section("desires", desire_context, 1)
    except Exception as exc:
        logger.debug("Desire context failed: %s", exc)

    try:
        from aegis_ai.user_state.manager import UserStateManager

        user_state = UserStateManager(data_dir=str(root / "user_state"))
        user_ctx = user_state.to_context_string()
        if user_ctx:
            add_section("user_state", f"USER SITUATION:\n{user_ctx}", 1)
    except Exception as exc:
        logger.debug("User state context failed: %s", exc)

    if profile == "decision":
        try:
            from aegis_ai.mind.affect_system import AffectSystem

            affect = AffectSystem(data_dir=str(root))
            affect_context = affect.to_context_string()
            if affect_context:
                add_section("affect", f"AFFECT STATE:\n{affect_context}", 1)
        except Exception as exc:
            logger.debug("Affect context failed: %s", exc)

    try:
        from aegis_ai.memory.advanced import AdvancedMemory

        memory = AdvancedMemory(data_dir=str(root / "memory"))
        if normalized_query:
            advanced_context = memory.get_context(normalized_query)
        else:
            # Still provide short-term + durable long-term even without a query.
            advanced_context = memory.get_context("")
        if advanced_context:
            add_section("advanced_memory", "MEMORY CONTEXT:\n" + _strip_system_reminders(advanced_context), 1)
    except Exception as exc:
        logger.debug("Advanced memory context failed: %s", exc)

    try:
        from aegis_ai.memory.experiential import ExperientialMemory

        experiential = ExperientialMemory(data_dir=str(root / "memory"))
        exp_recent = experiential.recall_recent(3 if profile == "summary" else 5)
        if exp_recent:
            lines = ["EXPERIENTIAL MEMORY:"]
            for exp in reversed(exp_recent):
                lines.append(f"- {exp.action}: {_truncate(exp.observation or exp.learning, 140)}")
            add_section("experiential", "\n".join(lines), len(exp_recent))
    except Exception as exc:
        logger.debug("Experiential memory failed: %s", exc)

    if profile == "decision":
        try:
            from aegis_ai.memory.person_memory import PersonMemory

            person_memory = PersonMemory(path=str(root / "memory" / "persons.jsonl"))
            person_context = person_memory.get_context_string(max_chars=300)
            if person_context:
                add_section(
                    "people",
                    "PEOPLE:\n" + _strip_system_reminders(person_context),
                    len(person_memory.get_all()),
                )
        except Exception as exc:
            logger.debug("Person memory failed: %s", exc)

    try:
        from aegis_ai.memory.semantic_memory import SemanticMemory

        semantic = SemanticMemory(path=str(root / "memory" / "semantic.jsonl"))
        sem_context = semantic.get_context_string(max_chars=250 if profile == "summary" else 400)
        if sem_context:
            add_section(
                "semantic",
                "KNOWLEDGE:\n" + _strip_system_reminders(sem_context),
                semantic.get_stats().get("total_entries", 0),
            )
    except Exception as exc:
        logger.debug("Semantic memory failed: %s", exc)

    if profile == "decision":
        try:
            skill_memory = _resolve_skill_memory(root)
            skill_context = skill_memory.get_context_string(max_chars=300)
            if skill_context:
                add_section("skills", "SKILLS:\n" + skill_context, skill_memory.get_stats().get("total", 0))
        except Exception as exc:
            logger.debug("Skill memory failed: %s", exc)

    pdc_lines, pdc_count = _personal_data_lines(root)
    if pdc_lines:
        add_section("personal_data", "\n".join(pdc_lines), pdc_count)

    execution_lines, execution_count, repeated_failures = _recent_execution_lines(root)
    if execution_lines:
        lines = ["RECENT AUTONOMOUS EXECUTIONS:"] + execution_lines
        if repeated_failures and profile == "decision":
            lines.append("Repeated recent failures:")
            lines.extend(f"- {item}" for item in repeated_failures)
        add_section("recent_executions", "\n".join(lines), execution_count)

    trace_lines, trace_count = _action_trace_lines(root)
    if trace_lines and profile == "decision":
        add_section("action_traces", "ACTION TRACE HINTS:\n" + "\n".join(trace_lines), trace_count)

    memory_store_lines, memory_store_counts = _memory_store_lines(root, normalized_query, profile)
    if memory_store_lines:
        add_section("memory_store", "\n".join(memory_store_lines), sum(memory_store_counts.values()))
        source_counts.update(memory_store_counts)

    understanding_lines, understanding_count = _user_understanding_lines(root, normalized_query)
    if understanding_lines and profile == "decision":
        add_section("user_understanding", "\n".join(understanding_lines), understanding_count)

    if profile == "summary":
        max_chars = 2200
    else:
        max_chars = 4200

    combined = "\n\n".join(sections)
    if len(combined) > max_chars:
        combined = combined[: max_chars - 3].rstrip() + "..."

    return MemoryContextResult(
        profile=profile,
        text=combined,
        source_counts=source_counts,
        section_names=section_names,
    )
