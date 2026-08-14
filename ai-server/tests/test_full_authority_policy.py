"""Full-authority policy: purchase/policy-bypass DENY; everything else ALLOW_WITH_AUDIT."""

from __future__ import annotations

from aegis_ai.personal_ai.delegation import DelegationPolicyStore
from aegis_schema.models import Capability, RiskLevel, ServerType
from policy_engine import PolicyDecision, PolicyEngine


def _cap(cap_id: str, risk: RiskLevel = RiskLevel.APPROVAL_REQUIRED) -> Capability:
    prefix = cap_id.split(".", 1)[0]
    server = {
        "ai": ServerType.AI,
        "ai-server": ServerType.AI,
        "browser": ServerType.BROWSER,
        "browser-server": ServerType.BROWSER,
        "pc": ServerType.PC,
        "pc-server": ServerType.PC,
        "dev": ServerType.DEV,
        "dev-server": ServerType.DEV,
    }.get(prefix, ServerType.AI)
    return Capability(
        id=cap_id,
        name=cap_id,
        description=cap_id,
        server_type=server,
        risk_level=risk,
    )


def test_agora_post_and_mouse_click_are_allow_with_audit() -> None:
    engine = PolicyEngine()
    agora = engine.evaluate(_cap("ai-server.agora.post", RiskLevel.HIGH_RISK), {"body": "hi"})
    click = engine.evaluate(
        Capability(
            id="pc-server.input.mouse_click",
            name="Click",
            description="Click",
            server_type=ServerType.PC,
            risk_level=RiskLevel.APPROVAL_REQUIRED,
        ),
        {"x": 1, "y": 1},
    )
    assert agora.decision == PolicyDecision.ALLOW_WITH_AUDIT
    assert click.decision == PolicyDecision.ALLOW_WITH_AUDIT


def test_purchase_and_disable_policy_are_denied() -> None:
    engine = PolicyEngine()
    purchase = engine.evaluate(_cap("browser-server.store.purchase"), {})
    bypass = engine.evaluate(_cap("ai-server.policy.disable_policy"), {})
    assert purchase.decision == PolicyDecision.DENY
    assert bypass.decision == PolicyDecision.DENY


def test_delegation_does_not_ask_for_social_communication(tmp_path) -> None:
    store = DelegationPolicyStore(data_dir=str(tmp_path))
    result = store.evaluate(
        "ai-server.agora.post",
        operation_context={"operation_category": "social_communication"},
    )
    assert result.decision == "auto_allowed"


def test_catalog_requires_approval_toggle_still_asks() -> None:
    engine = PolicyEngine()
    cap = _cap("ai-server.agora.post", RiskLevel.SAFE_ACTION)
    cap.requires_approval = True
    result = engine.evaluate(cap, {"body": "hi"})
    assert result.decision == PolicyDecision.ASK_APPROVAL


def test_autonomous_and_event_paths_match_chat() -> None:
    engine = PolicyEngine()
    cap = _cap("ai-server.agora.post", RiskLevel.SAFE_ACTION)
    chat = engine.evaluate(cap, {"body": "hi"})
    auto = engine.evaluate_autonomous_task(cap, {"body": "hi"})
    event = engine.evaluate_event_trigger(cap, {"body": "hi"})
    assert chat.decision == auto.decision == event.decision
