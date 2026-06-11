"""Dev Server + SelfDevAgent E2E — integration tests for Phase 5.

Tests the full self-development workflow:
  Reflection → Analyze → Propose → Branch → Patch → Test → Lint → Commit → PR → Reflect

CI uses MockDevProvider (no real git/test/lint).
Architecture reference: docs/architecture.md §8
"""

from __future__ import annotations

import json

from aegis_ai.agents.self_dev import SelfDevAgent, SelfDevPhase
from aegis_ai.audit import AuditLog
from aegis_ai.memory.reflection import Reflection, ReflectionLog
from aegis_schema.models import (
    Capability,
    Event,
    RiskLevel,
    ServerType,
)
from approval import ApprovalStore, ApprovalType
from dev_server_client import (
    DevServerClient,
    MockDevProvider,
)
from event_bus import EventBus
from policy_engine import PolicyDecision, PolicyEngine
from tool_broker import InvokeStatus, ToolBroker
from tool_registry import ToolRegistry
from trigger_engine import TriggerEngine, create_default_rules

# ── Helpers ──────────────────────────────────────────────────

FullStack = tuple[
    EventBus,
    TriggerEngine,
    ToolRegistry,
    PolicyEngine,
    ToolBroker,
    AuditLog,
    DevServerClient,
    ApprovalStore,
    ReflectionLog,
]


def _setup_full_stack(
    provider: MockDevProvider | None = None,
) -> FullStack:
    """Wire up the full AEGIS Core stack for Dev Server E2E testing."""
    bus = EventBus()
    engine = TriggerEngine()
    for rule in create_default_rules():
        engine.add_rule(rule)

    registry = ToolRegistry()
    approval_store = ApprovalStore()
    policy = PolicyEngine(approval_store=approval_store)
    broker = ToolBroker(registry, policy)

    audit = AuditLog(path="data/test_dev_audit.jsonl")
    reflection = ReflectionLog(path="data/test_dev_reflection.jsonl")

    prov = provider or MockDevProvider()
    client = DevServerClient(bus, registry, provider=prov, tool_broker=broker)

    bus.subscribe(engine.on_event)

    return bus, engine, registry, policy, broker, audit, client, approval_store, reflection


# ═══════════════════════════════════════════════════════════════
# 1. Capability Registration
# ═══════════════════════════════════════════════════════════════


class TestCapabilityRegistration:
    """Dev Server registers capabilities with AEGIS Core."""

    def test_observe_capabilities_registered(self):
        """All Dev observe capabilities are registered."""
        _, _, registry, _, _, _, client, _, _ = _setup_full_stack()
        client.register()

        for cap_id in ["dev.get_repo_status", "dev.get_diff", "dev.read_file", "dev.search_code"]:
            cap = registry.get_capability(cap_id)
            assert cap is not None, f"Capability {cap_id} not registered"
            assert cap.risk_level == RiskLevel.READ_ONLY

    def test_action_capabilities_registered(self):
        """All Dev action capabilities are registered."""
        _, _, registry, _, _, _, client, _, _ = _setup_full_stack()
        client.register()

        for cap_id in ["dev.create_branch", "dev.run_tests", "dev.run_lint"]:
            cap = registry.get_capability(cap_id)
            assert cap is not None
            assert cap.risk_level == RiskLevel.SAFE_ACTION

        for cap_id in ["dev.apply_patch", "dev.create_commit", "dev.create_pull_request", "dev.revert_changes"]:
            cap = registry.get_capability(cap_id)
            assert cap is not None
            assert cap.risk_level == RiskLevel.APPROVAL_REQUIRED

    def test_forbidden_capabilities_not_registered(self):
        """Forbidden capabilities are NOT registered."""
        _, _, registry, _, _, _, client, _, _ = _setup_full_stack()
        client.register()

        for cap_id in ["dev.push_main", "dev.merge_to_main", "dev.deploy_production"]:
            cap = registry.get_capability(cap_id)
            assert cap is None, f"Forbidden capability {cap_id} should not be registered"


# ═══════════════════════════════════════════════════════════════
# 2. Read-Only Repo Analysis
# ═══════════════════════════════════════════════════════════════


class TestReadOnlyAnalysis:
    """Read-only repo operations (Level 0, no approval)."""

    def test_repo_status(self):
        """dev.get_repo_status returns repo info."""
        _, _, _, _, _, _, client, _, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("dev.get_repo_status")
        assert "branch" in result
        assert "commit_hash" in result
        assert "is_clean" in result

    def test_get_diff(self):
        """dev.get_diff returns diff info."""
        _, _, _, _, _, _, client, _, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("dev.get_diff", {"from_branch": "main", "to_branch": "feature"})
        assert "files" in result

    def test_read_file(self):
        """dev.read_file returns file content."""
        _, _, _, _, _, _, client, _, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("dev.read_file", {"path": "src/example.py"})
        assert result.get("success") is True
        assert "content" in result

    def test_read_file_denied_for_secrets(self):
        """dev.read_file denies secret files."""
        _, _, _, _, _, _, client, _, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("dev.read_file", {"path": ".env"})
        assert "error" in result
        assert "denied" in result["error"].lower()

    def test_search_code(self):
        """dev.search_code returns matches."""
        _, _, _, _, _, _, client, _, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("dev.search_code", {"query": "EventBus"})
        assert "matches" in result


# ═══════════════════════════════════════════════════════════════
# 3. Branch Creation (Level 1)
# ═══════════════════════════════════════════════════════════════


class TestBranchCreation:
    """dev.create_branch — Level 1, auto-allowed."""

    def test_create_branch_allowed(self):
        """Branch creation is allowed without approval."""
        _, _, _, policy, _, _, client, _, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("dev.create_branch")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_create_branch_via_invoke(self):
        """Branch creation via invoke_capability works."""
        _, _, _, _, _, _, client, _, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability(
            "dev.create_branch",
            {
                "branch_name": "aegis/improve-event-bus",
                "base_branch": "main",
            },
        )
        assert result["success"] is True
        assert result["branch_name"] == "aegis/improve-event-bus"


# ═══════════════════════════════════════════════════════════════
# 4. Apply Patch (Level 2 — approval required)
# ═══════════════════════════════════════════════════════════════


class TestApplyPatch:
    """dev.apply_patch — Level 2, requires approval."""

    def test_patch_requires_approval(self):
        """Patch requires approval."""
        _, _, _, policy, _, _, client, _, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("dev.apply_patch")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_patch_blocked_without_approval(self):
        """Patch is blocked without approval."""
        _, _, _, _, broker, _, client, _, _ = _setup_full_stack()
        client.register()

        result = broker.invoke_tool(
            "dev.apply_patch",
            {
                "file_path": "src/example.py",
                "patch_content": "--- a/src/example.py\n+++ b/src/example.py\n",
            },
        )
        assert result.status == InvokeStatus.APPROVAL_NEEDED

    def test_patch_works_after_approval(self):
        """Patch works after approval."""
        _, _, _, _, broker, _, client, approval_store, _ = _setup_full_stack()
        client.register()

        result = broker.invoke_tool(
            "dev.apply_patch",
            {
                "file_path": "src/example.py",
                "patch_content": "--- a/src/example.py\n+++ b/src/example.py\n",
            },
        )
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        approval_req = result.policy_result.approval_request
        approval_store.approve(approval_req.approval_id, ApprovalType.ONE_TIME)

        def mock_patch(cap, params):
            return {"success": True, "applied": True, "error_detail": ""}

        broker.register_mock("dev.apply_patch", mock_patch)

        result2 = broker.invoke_tool_approved(
            "dev.apply_patch",
            {
                "file_path": "src/example.py",
                "patch_content": "--- a/src/example.py\n+++ b/src/example.py\n",
            },
        )
        assert result2.success is True


# ═══════════════════════════════════════════════════════════════
# 5. Run Tests / Lint (Level 1)
# ═══════════════════════════════════════════════════════════════


class TestRunTestsLint:
    """dev.run_tests / dev.run_lint — Level 1, auto-allowed."""

    def test_run_tests_allowed(self):
        """Test execution is allowed without approval."""
        _, _, _, policy, _, _, client, _, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("dev.run_tests")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_run_tests_pass(self):
        """Test execution returns pass results."""
        _, _, _, _, _, _, client, _, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("dev.run_tests")
        assert result["success"] is True
        assert result["passed"] == 100
        assert result["failed"] == 0

    def test_run_lint_allowed(self):
        """Lint execution is allowed without approval."""
        _, _, _, policy, _, _, client, _, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("dev.run_lint")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ALLOW

    def test_run_lint_pass(self):
        """Lint execution returns pass results."""
        _, _, _, _, _, _, client, _, _ = _setup_full_stack()
        client.register()

        result = client.invoke_capability("dev.run_lint")
        assert result["success"] is True
        assert result["passed"] is True


# ═══════════════════════════════════════════════════════════════
# 6. Create PR (Level 2 — approval required)
# ═══════════════════════════════════════════════════════════════


class TestCreatePR:
    """dev.create_pull_request — Level 2, requires approval."""

    def test_pr_requires_approval(self):
        """PR creation requires approval."""
        _, _, _, policy, _, _, client, _, _ = _setup_full_stack()
        client.register()

        cap = client._registry.get_capability("dev.create_pull_request")
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.ASK_APPROVAL

    def test_pr_works_after_approval(self):
        """PR creation works after approval."""
        _, _, _, _, broker, _, client, approval_store, _ = _setup_full_stack()
        client.register()

        result = broker.invoke_tool(
            "dev.create_pull_request",
            {
                "title": "Test PR",
                "description": "Test",
                "head_branch": "aegis/test",
                "base_branch": "main",
            },
        )
        assert result.status == InvokeStatus.APPROVAL_NEEDED

        approval_req = result.policy_result.approval_request
        approval_store.approve(approval_req.approval_id, ApprovalType.ONE_TIME)

        def mock_pr(cap, params):
            return {"success": True, "pr_url": "https://github.com/test/pull/1", "pr_number": 1}

        broker.register_mock("dev.create_pull_request", mock_pr)

        result2 = broker.invoke_tool_approved(
            "dev.create_pull_request",
            {
                "title": "Test PR",
                "description": "Test",
                "head_branch": "aegis/test",
                "base_branch": "main",
            },
        )
        assert result2.success is True


# ═══════════════════════════════════════════════════════════════
# 7. Forbidden Operations — Deny
# ═══════════════════════════════════════════════════════════════


class TestForbiddenOperations:
    """Dangerous dev operations are explicitly denied."""

    def test_push_main_denied(self):
        """dev.push_main is explicitly denied."""
        _, _, _, policy, _, _, client, _, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="dev.push_main",
            name="Push Main",
            description="Push to main branch.",
            server_type=ServerType.DEV,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_merge_to_main_denied(self):
        """dev.merge_to_main is explicitly denied."""
        _, _, _, policy, _, _, client, _, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="dev.merge_to_main",
            name="Merge to Main",
            description="Merge to main branch.",
            server_type=ServerType.DEV,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_deploy_production_denied(self):
        """dev.deploy_production is explicitly denied."""
        _, _, _, policy, _, _, client, _, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="dev.deploy_production",
            name="Deploy Production",
            description="Deploy to production.",
            server_type=ServerType.DEV,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_read_secrets_denied(self):
        """dev.read_secrets is explicitly denied."""
        _, _, _, policy, _, _, client, _, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="dev.read_secrets",
            name="Read Secrets",
            description="Read secrets.",
            server_type=ServerType.DEV,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY

    def test_delete_repo_denied(self):
        """dev.delete_repo is explicitly denied."""
        _, _, _, policy, _, _, client, _, _ = _setup_full_stack()
        client.register()

        cap = Capability(
            id="dev.delete_repo",
            name="Delete Repo",
            description="Delete repository.",
            server_type=ServerType.DEV,
            risk_level=RiskLevel.HIGH_RISK,
        )
        result = policy.evaluate(cap)
        assert result.decision == PolicyDecision.DENY


# ═══════════════════════════════════════════════════════════════
# 8. EventBus — Action Result Events
# ═══════════════════════════════════════════════════════════════


class TestActionResultEvents:
    """Dev action results are pushed to EventBus."""

    def test_action_completed_event(self):
        """Successful action pushes dev.action_completed."""
        bus, _, _, _, _, _, client, _, _ = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_action_result_event("dev.run_tests", True, {"passed": 100})

        events = [e for e in received if e.event_type == "dev.action_completed"]
        assert len(events) == 1

        payload = json.loads(events[0].payload_json)
        assert payload["success"] is True

    def test_action_failed_event(self):
        """Failed action pushes dev.action_failed."""
        bus, _, _, _, _, _, client, _, _ = _setup_full_stack()
        client.register()

        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))

        client.push_action_result_event("dev.run_tests", False, error="2 failures")

        events = [e for e in received if e.event_type == "dev.action_failed"]
        assert len(events) == 1


# ═══════════════════════════════════════════════════════════════
# 9. Provider Unavailable
# ═══════════════════════════════════════════════════════════════


class TestProviderUnavailable:
    """Graceful failure when Dev provider is unavailable."""

    def test_action_fails_when_unavailable(self):
        """Action returns error when provider is down."""
        provider = MockDevProvider(available=False)
        bus = EventBus()
        registry = ToolRegistry()
        client = DevServerClient(bus, registry, provider)

        result = client.invoke_capability("dev.get_repo_status")
        assert "error" in result
        assert "not available" in result["error"]


# ═══════════════════════════════════════════════════════════════
# 10. SelfDevAgent Full Workflow
# ═══════════════════════════════════════════════════════════════


class TestSelfDevAgent:
    """SelfDevAgent full workflow: Analyze → Propose → Branch → Patch → Test → Lint → Commit → PR → Reflect."""

    def test_full_workflow_success(self):
        """Full self-dev workflow succeeds."""
        _, _, _, _, broker, audit, client, approval_store, reflection = _setup_full_stack()
        client.register()

        # Register mock executors
        broker.register_mock("dev.create_branch", lambda cap, p: {"success": True, "branch_name": p.get("branch_name")})
        broker.register_mock("dev.apply_patch", lambda cap, p: {"success": True, "applied": True, "error_detail": ""})
        broker.register_mock(
            "dev.run_tests",
            lambda cap, p: {"success": True, "total": 100, "passed": 100, "failed": 0, "output": "100 passed"},
        )
        broker.register_mock(
            "dev.run_lint", lambda cap, p: {"success": True, "passed": True, "error_count": 0, "output": "clean"}
        )
        broker.register_mock("dev.create_commit", lambda cap, p: {"success": True, "commit_hash": "abc1234"})
        broker.register_mock(
            "dev.create_pull_request",
            lambda cap, p: {"success": True, "pr_url": "https://github.com/test/pull/1", "pr_number": 1},
        )
        broker.register_mock("dev.revert_changes", lambda cap, p: {"success": True, "reverted_files": []})

        agent = SelfDevAgent(
            tool_broker=broker,
            audit_log=audit,
            reflection_log=reflection,
            approval_store=approval_store,
        )

        result = agent.run(
            improvement_description="Add error handling to EventBus",
            file_path="src/event_bus.py",
            patch_content="--- a/src/event_bus.py\n+++ b/src/event_bus.py\n",
        )

        assert result.phase == SelfDevPhase.REFLECT
        assert result.branch_name != ""
        assert result.patch_applied is True
        assert result.test_result.get("success") is True
        assert result.lint_result.get("passed") is True
        assert result.pr_created is True
        assert result.pr_url != ""
        assert result.reflection != ""

    def test_full_workflow_test_failure_reverts(self):
        """Self-dev workflow reverts on test failure."""
        _, _, _, _, broker, audit, client, approval_store, reflection = _setup_full_stack()
        client.register()

        broker.register_mock("dev.create_branch", lambda cap, p: {"success": True, "branch_name": p.get("branch_name")})
        broker.register_mock("dev.apply_patch", lambda cap, p: {"success": True, "applied": True, "error_detail": ""})
        broker.register_mock(
            "dev.run_tests",
            lambda cap, p: {"success": False, "total": 100, "passed": 98, "failed": 2, "output": "FAILED"},
        )
        broker.register_mock("dev.revert_changes", lambda cap, p: {"success": True, "reverted_files": []})

        agent = SelfDevAgent(
            tool_broker=broker, audit_log=audit, reflection_log=reflection, approval_store=approval_store
        )

        result = agent.run(
            improvement_description="Fix bug in EventBus",
            file_path="src/event_bus.py",
            patch_content="--- a/src/event_bus.py\n+++ b/src/event_bus.py\n",
        )

        assert result.phase == SelfDevPhase.FAILED
        assert len(result.errors) >= 1
        assert "Tests failed" in result.errors[0]

    def test_full_workflow_lint_failure_reverts(self):
        """Self-dev workflow reverts on lint failure."""
        _, _, _, _, broker, audit, client, approval_store, reflection = _setup_full_stack()
        client.register()

        broker.register_mock("dev.create_branch", lambda cap, p: {"success": True, "branch_name": p.get("branch_name")})
        broker.register_mock("dev.apply_patch", lambda cap, p: {"success": True, "applied": True, "error_detail": ""})
        broker.register_mock(
            "dev.run_tests",
            lambda cap, p: {"success": True, "total": 100, "passed": 100, "failed": 0, "output": "100 passed"},
        )
        broker.register_mock(
            "dev.run_lint", lambda cap, p: {"success": False, "passed": False, "error_count": 3, "output": "3 errors"}
        )
        broker.register_mock("dev.revert_changes", lambda cap, p: {"success": True, "reverted_files": []})

        agent = SelfDevAgent(
            tool_broker=broker, audit_log=audit, reflection_log=reflection, approval_store=approval_store
        )

        result = agent.run(
            improvement_description="Refactor EventBus",
            file_path="src/event_bus.py",
            patch_content="--- a/src/event_bus.py\n+++ b/src/event_bus.py\n",
        )

        assert result.phase == SelfDevPhase.FAILED
        assert any("Lint failed" in e for e in result.errors)

    def test_analyze_reflections_finds_ideas(self):
        """SelfDevAgent analyzes reflection log for improvement ideas."""
        _, _, _, _, _, audit, _, approval_store, reflection = _setup_full_stack()

        reflection.add(
            Reflection(
                summary="Test failure in EventBus",
                what_failed=["event_bus.publish"],
                improvement_ideas=["Add retry logic to EventBus"],
            )
        )

        agent = SelfDevAgent(audit_log=audit, reflection_log=reflection, approval_store=approval_store)
        description = agent._analyze_reflections()

        assert description != ""
        assert "EventBus" in description or "retry" in description.lower()

    def test_workflow_without_tool_broker(self):
        """SelfDevAgent works without ToolBroker (mock mode)."""
        _, _, _, _, _, audit, _, approval_store, reflection = _setup_full_stack()

        agent = SelfDevAgent(audit_log=audit, reflection_log=reflection, approval_store=approval_store)

        result = agent.run(improvement_description="Test improvement")

        assert result.dev_id != ""
        assert result.duration_ms > 0

    def test_main_merge_forbidden(self):
        """main merge is NOT a registered capability."""
        _, _, registry, _, _, _, client, _, _ = _setup_full_stack()
        client.register()

        cap = registry.get_capability("dev.merge_to_main")
        assert cap is None

    def test_audit_trail_complete(self):
        """Self-dev workflow creates complete audit trail."""
        _, _, _, _, broker, audit, client, approval_store, reflection = _setup_full_stack()
        client.register()

        broker.register_mock("dev.create_branch", lambda cap, p: {"success": True, "branch_name": "test"})
        broker.register_mock(
            "dev.run_tests", lambda cap, p: {"success": True, "total": 1, "passed": 1, "failed": 0, "output": "ok"}
        )
        broker.register_mock(
            "dev.run_lint", lambda cap, p: {"success": True, "passed": True, "error_count": 0, "output": "ok"}
        )
        broker.register_mock("dev.create_commit", lambda cap, p: {"success": True, "commit_hash": "abc"})
        broker.register_mock(
            "dev.create_pull_request",
            lambda cap, p: {"success": True, "pr_url": "https://github.com/test/pull/1", "pr_number": 1},
        )

        agent = SelfDevAgent(
            tool_broker=broker, audit_log=audit, reflection_log=reflection, approval_store=approval_store
        )
        agent.run(improvement_description="Test audit trail")

        recent = audit.list_recent(20)
        actions = {e.action for e in recent}
        assert "self_dev_analyze" in actions
        assert "self_dev_propose" in actions
        assert "self_dev_branch" in actions
        assert "self_dev_test" in actions
        assert "self_dev_lint" in actions
        assert "self_dev_commit" in actions
        assert "self_dev_pr" in actions
        assert "self_dev_reflect" in actions


# ═══════════════════════════════════════════════════════════════
# 11. Full E2E Flow
# ═══════════════════════════════════════════════════════════════


class TestFullE2EFlow:
    """Complete E2E: Dev Server → SelfDevAgent → EventBus → AuditLog → Reflection."""

    def test_full_e2e_observe_to_pr(self):
        """Full E2E from repo observation to PR creation."""
        bus, engine, registry, policy, broker, audit, client, approval_store, reflection = _setup_full_stack()
        client.register()

        # 1. Observe repo status
        status = client.invoke_capability("dev.get_repo_status")
        assert status["branch"] == "main"

        # 2. Register mock executors
        broker.register_mock("dev.create_branch", lambda cap, p: {"success": True, "branch_name": p.get("branch_name")})
        broker.register_mock("dev.apply_patch", lambda cap, p: {"success": True, "applied": True})
        broker.register_mock(
            "dev.run_tests",
            lambda cap, p: {"success": True, "total": 50, "passed": 50, "failed": 0, "output": "50 passed"},
        )
        broker.register_mock(
            "dev.run_lint", lambda cap, p: {"success": True, "passed": True, "error_count": 0, "output": "clean"}
        )
        broker.register_mock("dev.create_commit", lambda cap, p: {"success": True, "commit_hash": "def5678"})
        broker.register_mock(
            "dev.create_pull_request",
            lambda cap, p: {"success": True, "pr_url": "https://github.com/test/pull/42", "pr_number": 42},
        )

        # 3. Run SelfDevAgent
        agent = SelfDevAgent(
            tool_broker=broker, audit_log=audit, reflection_log=reflection, approval_store=approval_store
        )
        result = agent.run(
            improvement_description="Improve error handling in EventBus",
            file_path="src/event_bus.py",
            patch_content="--- a/src/event_bus.py\n+++ b/src/event_bus.py\n@@ -1 +1 @@\n-old\n+new",
        )

        # 4. Verify workflow completed
        assert result.phase == SelfDevPhase.REFLECT
        assert result.pr_created is True
        assert result.pr_url == "https://github.com/test/pull/42"

        # 5. Verify audit trail
        recent = audit.list_recent(20)
        assert len(recent) >= 8

        # 6. Verify reflection written
        reflections = reflection.list_recent(5)
        assert len(reflections) >= 1
        assert "Improve error handling" in reflections[-1].summary
