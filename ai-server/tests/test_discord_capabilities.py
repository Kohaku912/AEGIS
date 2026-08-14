from aegis_schema.models import Capability, RiskLevel, ServerType

from aegis_ai.capability_catalog import CapabilityCatalog, risk_level_from_label
from policy_engine import PolicyDecision, PolicyEngine


def test_discord_manifests_load_with_expected_risks() -> None:
    catalog = CapabilityCatalog(capabilities_dir="capabilities", apps_dir="apps")

    status = catalog.resolve("pc-server.discord.status")
    join = catalog.resolve("pc-server.discord.join_voice_by_name")

    assert status is not None
    assert status.tcp_command_json == "discord_status"
    assert risk_level_from_label(status.risk_level) == RiskLevel.READ_ONLY
    assert join is not None
    assert join.tcp_command_json == "discord_join_voice_by_name"
    assert risk_level_from_label(join.risk_level) == RiskLevel.SAFE_ACTION
    assert "memoサーバーの通話に入って" in str(join.examples)


def test_discord_join_is_allowed_with_audit() -> None:
    policy = PolicyEngine()
    capability = Capability(
        id="pc-server.discord.join_voice_by_name",
        name="Join Discord voice",
        description="Join Discord voice",
        server_type=ServerType.PC,
        risk_level=RiskLevel.SAFE_ACTION,
    )

    result = policy.evaluate(capability, {"guild_name": "memo"})

    assert result.decision == PolicyDecision.ALLOW_WITH_AUDIT


def test_discord_read_only_status_is_allowed() -> None:
    policy = PolicyEngine()
    capability = Capability(
        id="pc-server.discord.status",
        name="Discord status",
        description="Read Discord RPC status",
        server_type=ServerType.PC,
        risk_level=RiskLevel.READ_ONLY,
    )

    result = policy.evaluate(capability, {})

    assert result.decision == PolicyDecision.ALLOW
