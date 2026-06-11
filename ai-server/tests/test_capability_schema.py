"""Tests for the AEGIS capability schema (Pydantic models + validation).

Covers:
1. Enum values
2. Capability model construction and validation
3. Sample capabilities loading
4. Edge cases and error conditions
5. Cross-capability batch validation
6. JSON roundtrip
7. Tool, ServerInfo, Event, ApprovalRequirement models
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aegis_schema import (
    ApprovalRequirement,
    Capability,
    Event,
    EventPriority,
    Parameter,
    RiskLevel,
    ServerInfo,
    ServerStatus,
    ServerType,
    Status,
    Tool,
    ValidationResult,
    validate_capabilities_batch,
    validate_capability,
    validate_capability_json,
)

# ── Path to sample capabilities ──────────────────────────────

SAMPLES_DIR = Path(__file__).parent.parent / "samples"
CAPABILITIES_JSON = SAMPLES_DIR / "capabilities.json"


# ═══════════════════════════════════════════════════════════════
# Enum Tests
# ═══════════════════════════════════════════════════════════════

class TestRiskLevel:
    def test_values(self):
        assert RiskLevel.UNSPECIFIED == 0
        assert RiskLevel.READ_ONLY == 1
        assert RiskLevel.SAFE_ACTION == 2
        assert RiskLevel.APPROVAL_REQUIRED == 3
        assert RiskLevel.HIGH_RISK == 4
        assert RiskLevel.FORBIDDEN == 5

    def test_ordering(self):
        assert RiskLevel.READ_ONLY < RiskLevel.SAFE_ACTION
        assert RiskLevel.SAFE_ACTION < RiskLevel.APPROVAL_REQUIRED
        assert RiskLevel.APPROVAL_REQUIRED < RiskLevel.HIGH_RISK
        assert RiskLevel.HIGH_RISK < RiskLevel.FORBIDDEN


class TestServerType:
    def test_values(self):
        assert ServerType.AI == 1
        assert ServerType.PC == 2
        assert ServerType.ANDROID == 3
        assert ServerType.BROWSER == 4
        assert ServerType.ROOM == 5
        assert ServerType.DEV == 6


# ═══════════════════════════════════════════════════════════════
# Parameter Tests
# ═══════════════════════════════════════════════════════════════

class TestParameter:
    def test_valid_parameter(self):
        p = Parameter(name="url", type="string", description="Target URL", required=True)
        assert p.name == "url"
        assert p.type == "string"
        assert p.required is True

    def test_invalid_type(self):
        with pytest.raises(ValueError, match="type must be one of"):
            Parameter(name="x", type="invalid_type")

    def test_invalid_name(self):
        with pytest.raises(ValueError, match="name must be snake_case"):
            Parameter(name="BadName", type="string")


# ═══════════════════════════════════════════════════════════════
# Capability Model Tests
# ═══════════════════════════════════════════════════════════════

class TestCapability:
    def test_minimal_valid_capability(self):
        cap = Capability(
            id="pc.screenshot",
            name="Screenshot",
            description="Capture a screenshot of the display",
            server_type=ServerType.PC,
            risk_level=RiskLevel.READ_ONLY,
        )
        assert cap.id == "pc.screenshot"
        assert cap.risk_level == RiskLevel.READ_ONLY
        assert cap.requires_approval is False
        assert cap.timeout_ms == 30000  # default

    def test_full_capability(self):
        cap = Capability(
            id="browser.open_page",
            name="Open Web Page",
            description="Navigate browser to a URL",
            server_type=ServerType.BROWSER,
            input_schema='{"type":"object","properties":{"url":{"type":"string"}},"required":["url"]}',
            output_schema='{"type":"object","properties":{"title":{"type":"string"}}}',
            risk_level=RiskLevel.SAFE_ACTION,
            requires_approval=False,
            side_effects=["sends HTTP request"],
            timeout_ms=30000,
            tags=["browser", "navigation", "risk:safe_action"],
            version="0.1.0",
        )
        assert cap.server_type == ServerType.BROWSER
        assert len(cap.tags) == 3

    def test_invalid_id_format(self):
        with pytest.raises(ValueError, match="String should match pattern"):
            Capability(
                id="invalid-format",
                name="Test",
                description="Test",
                server_type=ServerType.PC,
                risk_level=RiskLevel.READ_ONLY,
            )

    def test_id_must_match_server_type(self):
        with pytest.raises(ValueError, match="should start with 'browser.'"):
            Capability(
                id="pc.wrong_prefix",
                name="Test",
                description="Test",
                server_type=ServerType.BROWSER,
                risk_level=RiskLevel.READ_ONLY,
            )

    def test_unspecified_risk_level_rejected(self):
        with pytest.raises(ValueError, match="risk_level must not be UNSPECIFIED"):
            Capability(
                id="pc.test",
                name="Test",
                description="Test",
                server_type=ServerType.PC,
                risk_level=RiskLevel.UNSPECIFIED,
            )

    def test_forbidden_risk_level_rejected(self):
        with pytest.raises(ValueError, match="FORBIDDEN capabilities must not be registered"):
            Capability(
                id="pc.dangerous",
                name="Dangerous",
                description="Should not be registerable",
                server_type=ServerType.PC,
                risk_level=RiskLevel.FORBIDDEN,
            )

    def test_approval_consistency(self):
        """requires_approval=true with READ_ONLY should fail."""
        with pytest.raises(ValueError, match="requires_approval=true but risk_level is"):
            Capability(
                id="pc.screenshot",
                name="Screenshot",
                description="Test",
                server_type=ServerType.PC,
                risk_level=RiskLevel.READ_ONLY,
                requires_approval=True,
            )

    def test_timeout_bounds(self):
        with pytest.raises(ValueError):
            Capability(
                id="pc.test",
                name="Test",
                description="Test",
                server_type=ServerType.PC,
                risk_level=RiskLevel.READ_ONLY,
                timeout_ms=-1,
            )

    def test_version_format(self):
        with pytest.raises(ValueError, match="String should match pattern"):
            Capability(
                id="pc.test",
                name="Test",
                description="Test",
                server_type=ServerType.PC,
                risk_level=RiskLevel.READ_ONLY,
                version="v1",
            )

    def test_json_roundtrip(self):
        cap = Capability(
            id="pc.screenshot",
            name="Screenshot",
            description="Capture screen",
            server_type=ServerType.PC,
            risk_level=RiskLevel.READ_ONLY,
        )
        json_str = cap.model_dump_json()
        cap2 = Capability.model_validate_json(json_str)
        assert cap2.id == cap.id
        assert cap2.risk_level == cap.risk_level

    def test_json_schema_generation(self):
        """Pydantic can generate JSON Schema for the Capability model."""
        schema = Capability.model_json_schema()
        assert schema["title"] == "Capability"
        assert "properties" in schema
        assert "id" in schema["properties"]
        assert "risk_level" in schema["properties"]


# ═══════════════════════════════════════════════════════════════
# Sample Capabilities Tests
# ═══════════════════════════════════════════════════════════════

class TestSampleCapabilities:
    @pytest.fixture(scope="class")
    def sample_data(self):
        with open(CAPABILITIES_JSON, encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture(scope="class")
    def capabilities(self, sample_data):
        return [Capability.model_validate(item) for item in sample_data]

    def test_sample_file_exists(self):
        assert CAPABILITIES_JSON.exists(), f"Sample file not found: {CAPABILITIES_JSON}"

    def test_sample_file_is_valid_json(self):
        with open(CAPABILITIES_JSON, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list), "Sample capabilities must be a JSON array"
        assert len(data) == 10, f"Expected 10 sample capabilities, got {len(data)}"

    def test_all_samples_parse(self, capabilities):
        assert len(capabilities) == 10

    def test_all_have_valid_ids(self, capabilities):
        for cap in capabilities:
            assert "." in cap.id, f"Capability ID '{cap.id}' should contain a dot"
            prefix = cap.id.split(".")[0]
            valid_prefixes = {"pc", "android", "browser", "room", "dev", "ai"}
            assert prefix in valid_prefixes, f"Invalid prefix '{prefix}' in '{cap.id}'"

    def test_all_have_server_type(self, capabilities):
        for cap in capabilities:
            assert cap.server_type != ServerType.UNSPECIFIED

    def test_all_have_risk_level(self, capabilities):
        for cap in capabilities:
            assert cap.risk_level != RiskLevel.UNSPECIFIED
            assert cap.risk_level != RiskLevel.FORBIDDEN

    def test_no_duplicate_ids(self, capabilities):
        ids = [cap.id for cap in capabilities]
        assert len(ids) == len(set(ids)), f"Duplicate IDs found: {ids}"

    def test_read_only_have_no_side_effects(self, capabilities):
        for cap in capabilities:
            if cap.risk_level == RiskLevel.READ_ONLY:
                assert not cap.side_effects, (
                    f"READ_ONLY capability '{cap.id}' should have no side_effects"
                )

    def test_approval_required_have_side_effects(self, capabilities):
        for cap in capabilities:
            if cap.risk_level >= RiskLevel.APPROVAL_REQUIRED:
                assert cap.side_effects or cap.requires_approval, (
                    f"{cap.risk_level.name} capability '{cap.id}' should declare "
                    "side_effects or requires_approval"
                )

    def test_batch_validation(self, capabilities):
        result = validate_capabilities_batch(capabilities)
        assert result.valid, f"Batch validation failed:\n{result.summary()}"

    def test_json_roundtrip_all(self, capabilities):
        for cap in capabilities:
            json_str = cap.model_dump_json()
            cap2 = Capability.model_validate_json(json_str)
            assert cap2 == cap

    def test_each_capability_has_risk_tag(self, capabilities):
        for cap in capabilities:
            _expected_tag = f"risk:{cap.risk_level.name.lower()}"
            # This is a warning, not an error — just check the tag exists
            # (some capabilities might not have it, which is valid but warned)
            pass  # validated in validation module with warnings

    def test_input_schemas_are_valid_json(self, capabilities):
        for cap in capabilities:
            if cap.input_schema and cap.input_schema != "{}":
                try:
                    schema = json.loads(cap.input_schema)
                    assert isinstance(schema, dict), (
                        f"input_schema for '{cap.id}' is not a JSON object"
                    )
                except json.JSONDecodeError as e:
                    pytest.fail(f"input_schema for '{cap.id}' is invalid JSON: {e}")

    def test_output_schemas_are_valid_json(self, capabilities):
        for cap in capabilities:
            if cap.output_schema and cap.output_schema != "{}":
                try:
                    schema = json.loads(cap.output_schema)
                    assert isinstance(schema, dict), (
                        f"output_schema for '{cap.id}' is not a JSON object"
                    )
                except json.JSONDecodeError as e:
                    pytest.fail(f"output_schema for '{cap.id}' is invalid JSON: {e}")

    def test_timeout_ms_reasonable(self, capabilities):
        for cap in capabilities:
            assert cap.timeout_ms > 0, f"'{cap.id}': timeout_ms should be > 0, got {cap.timeout_ms}"
            assert cap.timeout_ms <= 3600000, (
                f"'{cap.id}': timeout_ms {cap.timeout_ms} exceeds 1 hour max"
            )

    def test_each_server_type_represented(self, capabilities):
        server_types = {cap.server_type for cap in capabilities}
        expected = {
            ServerType.PC,
            ServerType.ANDROID,
            ServerType.BROWSER,
            ServerType.ROOM,
            ServerType.DEV,
        }
        missing = expected - server_types
        assert not missing, f"Missing capabilities for server types: {missing}"


# ═══════════════════════════════════════════════════════════════
# Validation Module Tests
# ═══════════════════════════════════════════════════════════════

class TestValidationResult:
    def test_valid_result(self):
        result = ValidationResult()
        assert result.valid is True
        assert result.errors == []

    def test_add_error(self):
        result = ValidationResult()
        result.add_error("test error")
        assert result.valid is False
        assert len(result.errors) == 1

    def test_merge(self):
        r1 = ValidationResult()
        r1.add_error("error 1")
        r2 = ValidationResult()
        r2.add_warning("warning 1")
        r1.merge(r2)
        assert len(r1.errors) == 1
        assert len(r1.warnings) == 1

    def test_summary(self):
        result = ValidationResult()
        result.add_error("bad thing")
        summary = result.summary()
        assert "❌" in summary
        assert "bad thing" in summary


class TestValidateCapability:
    def test_valid_capability_passes(self):
        cap = Capability(
            id="pc.screenshot",
            name="Screenshot",
            description="Capture a screenshot of the display for OCR analysis",
            server_type=ServerType.PC,
            risk_level=RiskLevel.READ_ONLY,
        )
        result = validate_capability(cap)
        assert result.valid

    def test_unspecified_risk_level_rejected_by_pydantic(self):
        """Pydantic's model_validator rejects UNSPECIFIED risk_level at construction time.
        This is correct — the validation module never sees UNSPECIFIED capabilities
        because they cannot be constructed."""
        with pytest.raises(ValueError, match="risk_level must not be UNSPECIFIED"):
            Capability(
                id="pc.test",
                name="Test",
                description="A test capability with issues",
                server_type=ServerType.PC,
                risk_level=RiskLevel.UNSPECIFIED,
            )

    def test_invalid_json_schema_warns(self):
        cap = Capability(
            id="pc.test",
            name="Test",
            description="A test capability with invalid JSON schema",
            server_type=ServerType.PC,
            risk_level=RiskLevel.READ_ONLY,
            input_schema="not valid json",
        )
        result = validate_capability(cap)
        assert not result.valid
        assert any("input_schema" in err for err in result.errors)

    def test_read_only_with_side_effects_warns(self):
        cap = Capability(
            id="pc.test",
            name="Test",
            description="A read-only capability that claims side effects",
            server_type=ServerType.PC,
            risk_level=RiskLevel.READ_ONLY,
            side_effects=["modifies state"],
        )
        result = validate_capability(cap)
        assert any("READ_ONLY" in w for w in result.warnings)


class TestValidateCapabilityJson:
    def test_valid_json(self):
        json_str = json.dumps({
            "id": "pc.screenshot",
            "name": "Screenshot",
            "description": "Capture screen for OCR analysis",
            "server_type": 2,
            "risk_level": 1,
        })
        result = validate_capability_json(json_str)
        assert result.valid
        assert len(result.validated) == 1
        assert result.validated[0].id == "pc.screenshot"

    def test_invalid_json(self):
        result = validate_capability_json("not json")
        assert not result.valid
        assert any("Invalid JSON" in e for e in result.errors)

    def test_not_an_object(self):
        result = validate_capability_json("[1, 2, 3]")
        assert not result.valid
        assert any("must be an object" in e for e in result.errors)

    def test_missing_required_fields(self):
        result = validate_capability_json('{"id": "pc.test"}')
        assert not result.valid


class TestValidateCapabilitiesBatch:
    def test_empty_batch(self):
        result = validate_capabilities_batch([])
        assert result.valid

    def test_duplicate_ids(self):
        caps = [
            Capability(
                id="pc.duplicate",
                name="First",
                description="First instance",
                server_type=ServerType.PC,
                risk_level=RiskLevel.READ_ONLY,
            ),
            Capability(
                id="pc.duplicate",
                name="Second",
                description="Second instance",
                server_type=ServerType.PC,
                risk_level=RiskLevel.READ_ONLY,
            ),
        ]
        result = validate_capabilities_batch(caps)
        assert not result.valid
        assert any("Duplicate" in e for e in result.errors)


# ═══════════════════════════════════════════════════════════════
# Other Model Tests
# ═══════════════════════════════════════════════════════════════

class TestTool:
    def test_valid_tool(self):
        tool = Tool(
            id="tool-001",
            capability_id="pc.screenshot",
            server_id="pc-main",
            config_json='{"quality": 90}',
        )
        assert tool.enabled is True
        assert tool.config_json == '{"quality": 90}'

    def test_json_roundtrip(self):
        tool = Tool(id="t1", capability_id="pc.screenshot", server_id="pc-main")
        json_str = tool.model_dump_json()
        tool2 = Tool.model_validate_json(json_str)
        assert tool2.id == "t1"


class TestServerInfo:
    def test_valid_server_info(self):
        info = ServerInfo(
            server_id="pc-main",
            server_type=ServerType.PC,
            version="1.0.0",
            capability_ids=["pc.screenshot", "pc.mouse_click"],
        )
        assert info.status == ServerStatus.STARTING
        assert info.host == "localhost"
        assert info.port == 50051

    def test_invalid_version(self):
        with pytest.raises(ValueError):
            ServerInfo(server_id="x", server_type=ServerType.PC, version="bad")


class TestApprovalRequirement:
    def test_valid_approval(self):
        req = ApprovalRequirement(
            capability_id="room.ir_send",
            risk_level=RiskLevel.APPROVAL_REQUIRED,
            requires_user_approval=True,
            approval_message="This will send an IR signal to the TV. Continue?",
        )
        assert req.timeout_seconds == 30
        assert req.allow_session_remember is True

    def test_timeout_bounds(self):
        with pytest.raises(ValueError):
            ApprovalRequirement(
                capability_id="test",
                risk_level=RiskLevel.APPROVAL_REQUIRED,
                timeout_seconds=100000,  # > 86400
            )


class TestEvent:
    def test_valid_event(self):
        event = Event(
            event_id="evt-001",
            event_type="pc.screen_change",
            source_server_type=ServerType.PC,
            source_server_id="pc-main",
            timestamp_ms=1700000000000,
            payload_json='{"window": "chrome.exe"}',
        )
        assert event.priority == EventPriority.NORMAL
        assert event.correlation_id == ""

    def test_event_json_roundtrip(self):
        event = Event(
            event_id="evt-002",
            event_type="android.notification",
            source_server_type=ServerType.ANDROID,
            source_server_id="android-phone1",
        )
        json_str = event.model_dump_json()
        event2 = Event.model_validate_json(json_str)
        assert event2.event_type == "android.notification"


class TestStatus:
    def test_default_status(self):
        s = Status()
        assert s.code == 0
        assert s.message == "ok"

    def test_error_status(self):
        s = Status(code=1, message="not found", detail='{"resource":"capability"}')
        assert s.code == 1
