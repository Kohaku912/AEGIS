"""Goal-alignment regression tests (BUG_REPORT §31–§37).

These lock in the fixes for code that did not conform to the AGENTS.md rules:

- G1: never detect categories/intent with keyword or substring matching
- G4: never hardcode capability IDs (the manifest is the source of truth)
- G6: memory backends are accessed through ``runtime.memory_manager``

Each test names the concrete failure it prevents so a future regression is
self-explanatory.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_SERVER = Path(__file__).resolve().parents[1]
AI_SRC = AI_SERVER / "src" / "aegis_ai"


# ═══════════════════════════════════════════════════════════════
# §32 — situation.py keyword classification duplicated the Rust logic
# ═══════════════════════════════════════════════════════════════


def test_chat_app_does_not_suppress_notifications(tmp_path) -> None:
    """`discord`/`steam`/`slack` must not be keyword-mapped to "game".

    Before the fix, ``any(term in app for term in ("steam","game","discord"))``
    set ``interruptibility`` to "important_only", silently suppressing
    notifications while the user was merely chatting. Rust classified the same
    app as "chat", so the two languages disagreed.
    """
    from aegis_ai.personal_ai.situation import SituationModel

    model = SituationModel(data_dir=str(tmp_path))
    for app in ("discord.exe", "slack.exe", "steam.exe", "Endgame"):
        state = model.update_from_structured_observation("pc", {"foreground_app": app})
        assert state["state"] != "game", app
        assert state["interruptibility"] != "important_only", app


def test_explicit_gaming_activity_still_suppresses(tmp_path) -> None:
    """A genuinely classified gaming activity must keep its old behaviour."""
    from aegis_ai.personal_ai.situation import SituationModel

    model = SituationModel(data_dir=str(tmp_path))
    state = model.update_from_structured_observation("pc", {"activity": "gaming"})
    assert state["state"] == "game"
    assert state["interruptibility"] == "important_only"


# ═══════════════════════════════════════════════════════════════
# §33 — browser operation inference (removed 2026-10-03)
# ═══════════════════════════════════════════════════════════════
#
# Four tests lived here, all of them exercising ``aegis_ai.permissions``: that the
# keyword classifier was gone from ``service_scope_types.py``, that an unknown browser
# operation asks for approval, that an explicit ``read`` is allowed, and that the helper
# passes an operation through unchanged.
#
# The owner **deleted** the ``aegis_ai.permissions`` package on 2026-10-03
# (``DELEGATION.md`` §4 item 3) — it was a working forced gate that nothing under ``src/``
# imported. The surface those four tests described therefore no longer exists, so they
# went with it. The retirement is now pinned negatively instead:
# ``test_forced_gate_stays_retired.py::test_the_permissions_gate_package_is_gone``.


# ═══════════════════════════════════════════════════════════════
# §34 — SkillMemory/WorkflowMemory stats and MemoryManager routing
# ═══════════════════════════════════════════════════════════════


def test_skill_memory_record_result_persists(tmp_path) -> None:
    """Success/failure counters must survive a reload.

    The self-improvement loop keys off ``success_rate < 0.6 and
    (success_count + failure_count) >= 3``; if the counters are never written to
    disk the signal can never fire.
    """
    from aegis_ai.memory.skill_memory import SkillMemory

    path = tmp_path / "skills.jsonl"
    memory = SkillMemory(path=str(path))
    skill = memory.add_skill(name="Check AGORA", execution_steps=[{"tool": "llm"}])
    memory.record_result(skill.skill_id, success=True)
    memory.record_result(skill.skill_id, success=False)

    reloaded = SkillMemory(path=str(path))
    stored = reloaded._skills[skill.skill_id]
    assert stored.success_count == 1
    assert stored.failure_count == 1
    assert stored.last_used_at_ms > 0


def test_skill_memory_low_success_rate_is_detectable(tmp_path) -> None:
    """A skill with recorded failures must be visible to the improvement loop."""
    from aegis_ai.memory.skill_memory import SkillMemory

    memory = SkillMemory(path=str(tmp_path / "skills.jsonl"))
    skill = memory.add_skill(name="Flaky skill", execution_steps=[{"tool": "llm"}])
    for _ in range(3):
        memory.record_result(skill.skill_id, success=False)

    reloaded = SkillMemory(path=str(tmp_path / "skills.jsonl"))
    stored = reloaded._skills[skill.skill_id]
    assert stored.success_rate < 0.6
    assert (stored.success_count + stored.failure_count) >= 3


def test_workflow_record_result_persists(tmp_path) -> None:
    """WorkflowMemory.record_result used to mutate memory only (real bug)."""
    from aegis_ai.memory.workflow_memory import WorkflowMemory

    path = tmp_path / "workflows.jsonl"
    memory = WorkflowMemory(path=str(path))
    workflow = memory.add(name="Check mail", steps=[{"tool_call": "llm"}], goal_pattern="check mail")
    memory.record_result(workflow.workflow_id, success=True, duration_ms=120)

    reloaded = WorkflowMemory(path=str(path))
    stored = reloaded._workflows[workflow.workflow_id]
    assert stored.success_count == 1
    assert stored.average_duration_ms == 120
    assert stored.last_used_at_ms > 0


def test_workflow_deprecate_persists(tmp_path) -> None:
    from aegis_ai.memory.workflow_memory import WorkflowMemory

    path = tmp_path / "workflows.jsonl"
    memory = WorkflowMemory(path=str(path))
    workflow = memory.add(name="Check mail", steps=[{"tool_call": "llm"}])
    memory.deprecate(workflow.workflow_id, reason="superseded")

    reloaded = WorkflowMemory(path=str(path))
    stored = reloaded._workflows[workflow.workflow_id]
    assert stored.deprecated is True
    assert "deprecated:superseded" in stored.tags


def test_curiosity_system_prefers_injected_skill_backend(tmp_path) -> None:
    """The runtime passes the MemoryManager-owned backend; it must be used as-is."""
    from aegis_ai.autonomous.curiosity_exploration import CuriosityDrivenExplorationSystem

    sentinel = object()
    system = CuriosityDrivenExplorationSystem(skill_memory=sentinel, data_dir=str(tmp_path))
    assert system._skill_memory() is sentinel


def test_curiosity_system_resolves_runtime_backend(tmp_path, monkeypatch) -> None:
    """Without an injected backend, resolution must go through the MemoryManager."""
    from aegis_ai.autonomous.curiosity_exploration import CuriosityDrivenExplorationSystem

    backend = object()

    class _Manager:
        def get_backend(self, name):
            return backend if name == "skill" else None

    class _Runtime:
        memory_manager = _Manager()

    monkeypatch.setattr("aegis_ai.runtime.peek_runtime", lambda: _Runtime())
    system = CuriosityDrivenExplorationSystem(data_dir=str(tmp_path))
    assert system._skill_memory() is backend


def test_memory_context_resolves_skill_backend_from_runtime(tmp_path, monkeypatch) -> None:
    from aegis_ai.llm import memory_context
    from aegis_ai.memory.skill_memory import SkillMemory

    backend = SkillMemory(path=str(tmp_path / "memory" / "skills.jsonl"))

    class _Manager:
        def get_backend(self, name):
            return backend if name == "skill" else None

    class _Runtime:
        memory_manager = _Manager()

    monkeypatch.setattr("aegis_ai.runtime.peek_runtime", lambda: _Runtime())
    assert memory_context._resolve_skill_memory(tmp_path) is backend


def test_memory_context_skill_stats_use_existing_key(tmp_path, monkeypatch) -> None:
    """`get_stats()` exposes `total`, not `total_skills` (the count was always 0)."""

    monkeypatch.setattr("aegis_ai.runtime.peek_runtime", lambda: None)
    (tmp_path / "memory").mkdir(parents=True, exist_ok=True)
    from aegis_ai.memory.skill_memory import SkillMemory

    memory = SkillMemory(path=str(tmp_path / "memory" / "skills.jsonl"))
    memory.add_skill(name="Check AGORA", execution_steps=[{"tool": "llm"}])

    assert memory.get_stats().get("total_skills") is None
    assert memory.get_stats().get("total") == 1


# ═══════════════════════════════════════════════════════════════
# §35 — misleading `goal_pattern` naming and skill/workflow telemetry
# ═══════════════════════════════════════════════════════════════


def test_goal_pattern_is_plain_text_not_a_regex() -> None:
    """`goal_pattern` is scored as free text; a regex-looking value must not be
    documented or treated as a pattern."""
    source = (AI_SRC / "memory" / "workflow_memory.py").read_text(encoding="utf-8")
    assert "Regex/keyword pattern" not in source
    assert "agora.*message" not in source


def test_autonomous_loop_does_not_claim_a_skill_was_replayed() -> None:
    """Skill/workflow matches are advisory hints; execution uses the LLM-chosen
    capability. The trace must not assert the skill's steps were used."""
    source = (AI_SRC / "autonomous" / "autonomous_loop.py").read_text(encoding="utf-8")
    assert 'f"Using skill: ' not in source
    assert 'f"Using workflow: ' not in source
    assert "advisory" in source


# ═══════════════════════════════════════════════════════════════
# §36 — Android feature detection from the server version string
# ═══════════════════════════════════════════════════════════════


def test_android_chat_support_is_not_version_sniffed() -> None:
    path = (
        REPO_ROOT
        / "android-server"
        / "app"
        / "src"
        / "main"
        / "java"
        / "com"
        / "aegis"
        / "android"
        / "grpc"
        / "AegisGrpcClient.kt"
    )
    source = path.read_text(encoding="utf-8")
    assert "supportsSendChat" not in source
    assert 'contains("sendchat")' not in source
    assert 'contains("chat-v1")' not in source
    # The lazy negotiation path must still be present.
    assert "isMethodNotFound" in source


# ═══════════════════════════════════════════════════════════════
# §31 — pc-server app classification (source-level guard; behaviour is
# covered by the Rust unit tests in pc-server/src/observe.rs)
# ═══════════════════════════════════════════════════════════════


def test_pc_server_app_category_has_no_substring_matching() -> None:
    source = (REPO_ROOT / "pc-server" / "src" / "observe.rs").read_text(encoding="utf-8")
    start = source.index("fn input_target_category")
    end = source.index("fn get_idle_ms")
    body = source[start:end]
    # No substring search against a literal (e.g. `text.contains("code")`).
    # `CODING_EXECUTABLES.contains(&exe.as_str())` is a slice membership test.
    assert '.contains("' not in body, "substring matching must not classify apps"
    assert "to_ascii_lowercase()" in body
    assert "title" not in body, "window titles are free text and must not be consulted"
    # Exact executable-name lookup is the replacement mechanism.
    assert "CODING_EXECUTABLES.contains" in body


# ═══════════════════════════════════════════════════════════════
# §37 — hardcoded capability-ID dispatch maps must not drift
# ═══════════════════════════════════════════════════════════════


def test_room_capability_ids_resolve_to_manifests(tmp_path) -> None:
    """Every dispatched capability ID must exist in the capability manifests."""
    from aegis_ai.capability_catalog import CapabilityCatalog
    from aegis_ai.integrations.room.grpc_client import (
        _ROOM_CAPABILITY_ALIASES,
        _ROOM_CAPABILITY_HANDLERS,
        RoomServerGrpcClient,
    )

    catalog = CapabilityCatalog(
        capabilities_dir=str(AI_SERVER / "capabilities"),
        apps_dir=str(tmp_path / "apps"),
    )

    for capability_id in _ROOM_CAPABILITY_HANDLERS:
        assert catalog.resolve(capability_id) is not None, (
            f"{capability_id} is dispatched by the room client but has no manifest"
        )

    for alias, canonical in _ROOM_CAPABILITY_ALIASES.items():
        assert canonical in _ROOM_CAPABILITY_HANDLERS, f"{alias} points at an unknown target"
        assert catalog.resolve(canonical) is not None, f"{canonical} has no manifest"

    client = RoomServerGrpcClient()
    for handler_name in _ROOM_CAPABILITY_HANDLERS.values():
        assert callable(getattr(client, handler_name, None)), f"missing handler {handler_name}"

    assert client.invoke_capability("room-server.nope.nope")["error"].startswith("Unsupported Room")


def test_android_capability_routes_resolve_to_manifests(tmp_path) -> None:
    """The Android dispatch map must stay in sync with the manifests."""
    from aegis_ai.capability_catalog import CapabilityCatalog
    from aegis_ai.integrations.android.capability_mapper import AndroidCapabilityMapper

    catalog = CapabilityCatalog(
        capabilities_dir=str(AI_SERVER / "capabilities"),
        apps_dir=str(tmp_path / "apps"),
    )

    missing = [
        capability_id
        for capability_id in AndroidCapabilityMapper().list_capabilities()
        if catalog.resolve(capability_id) is None
    ]
    assert not missing, f"Android routes without a manifest: {missing}"
