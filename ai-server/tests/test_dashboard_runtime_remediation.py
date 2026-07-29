from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

from aegis_ai.health.alert_manager import HealthAlertManager
from aegis_ai.integrations.agora.agora_client import AgoraClient
from aegis_ai.llm.gateway import LLMGateway
from aegis_ai.llm.provider_circuit import ProviderCircuitRegistry
from aegis_ai.llm.settings_resolver import LLMSettings, LLMSettingsResolver
from aegis_ai.personal_ai.storage import JsonStateFile
from aegis_ai.social.manager import SocialManager
from aegis_ai.web.ui_overview import _errors


def test_gateway_propagates_json_mode_and_separates_models() -> None:
    calls: list[dict[str, object]] = []

    class Provider:
        def generate(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(success=True, content="{}", tokens_used=1)

    gateway = LLMGateway(SimpleNamespace())
    provider = Provider()
    gateway._get_provider_for_profile = lambda _settings: provider
    gateway._resolve = lambda _profile: LLMSettings(model="model-a", max_tokens=777)

    gateway.generate("prompt", json_mode=True, profile="decision")

    assert calls[0]["json_mode"] is True
    assert calls[0]["max_tokens"] == 777


def test_decision_profile_resolves_from_deployed_config() -> None:
    config = Path(__file__).parents[1] / "config" / "llm.yaml"
    resolver = LLMSettingsResolver(str(config))
    settings = resolver.resolve(profile_id="decision")
    assert settings.model
    assert settings.max_tokens >= 1024


def test_provider_billing_circuits_are_origin_isolated() -> None:
    registry = ProviderCircuitRegistry()
    deepseek = registry.get("https://api.deepseek.com/v1")
    other = registry.get("https://example.invalid/v1")

    deepseek.record_error(Exception("402 Insufficient Balance"))
    other.record_success()

    assert deepseek.is_open()
    assert not other.is_open()
    assert registry.status()["open"] is True
    assert len(registry.status()["providers"]) == 2


def test_billing_incident_persists_until_one_successful_probe() -> None:
    registry = ProviderCircuitRegistry()
    circuit = registry.get("https://api.deepseek.com")
    circuit._cooldown_ms = 1
    circuit.record_error(Exception("402 Insufficient Balance"))
    circuit._opened_at_ms -= 10

    assert circuit.allow_request() is True
    assert circuit.allow_request() is False
    assert circuit.status()["degraded"] is True
    circuit.record_success()
    assert circuit.status()["degraded"] is False


def test_json_state_file_concurrent_saves_are_atomic(tmp_path: Path) -> None:
    state = JsonStateFile(tmp_path / "state.json")

    def save(index: int) -> None:
        state.save({"index": index, "payload": list(range(20))})

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(save, range(100)))

    loaded = state.load()
    assert loaded["index"] in range(100)
    assert loaded["payload"] == list(range(20))
    assert not list(tmp_path.glob("*.tmp"))


def test_agora_cursor_update_is_monotonic() -> None:
    client = AgoraClient(token="test")
    calls: list[tuple[str, str]] = []

    def request(method: str, path: str, **_kwargs):
        calls.append((method, path))
        if method == "GET":
            return {"last_read_post_id": 309}
        raise AssertionError("A regressive cursor must not be sent")

    client._request = request
    result = client.update_cursor(309)
    assert result.last_read_post_id == 309
    assert calls == [("GET", "/api/v1/me/cursor")]


def test_social_retry_batch_is_bounded_and_records_backoff(tmp_path: Path) -> None:
    calls = 0

    def generate(**_kwargs):
        nonlocal calls
        calls += 1
        return SimpleNamespace(success=False, content="", error="402 Insufficient Balance")

    manager = SocialManager(
        data_dir=str(tmp_path),
        llm=SimpleNamespace(generate=generate),
    )
    items = manager.ingest(
        "agora",
        [
            {"id": index, "thread_id": 1, "author": "peer", "body": f"message {index}"}
            for index in range(1, 7)
        ],
    )
    for item in items:
        saved = manager._store.get(item.item_id)
        saved.status = type(saved.status).RETRY_PENDING
        saved.metadata = {}
        manager._store.update(saved)

    processed = manager.retry_pending_items()
    records = manager.list_items(limit=10)

    assert len(processed) == 5
    assert calls == 10
    assert sum(item["metadata"].get("retry_count", 0) == 1 for item in records) == 5
    assert all(
        "last_error" in item["metadata"] and item["metadata"]["next_retry_at"] > 0
        for item in records
        if item["metadata"].get("retry_count")
    )

    terminal = processed[0]
    for _ in range(4):
        terminal = manager.process_new_items([terminal])[0]
    assert terminal.status.value == "failed"
    assert terminal.metadata["retry_count"] == 5
    assert terminal.metadata["next_retry_at"] == 0


def test_social_json_uses_decision_profile_token_limit(tmp_path: Path) -> None:
    calls: list[dict[str, object]] = []

    def generate(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(
            success=True,
            content='{"decision":"skip","reason":"not actionable","draft_body":""}',
        )

    manager = SocialManager(
        data_dir=str(tmp_path),
        llm=SimpleNamespace(generate=generate),
    )

    result = manager._generate_json("Decide how to handle this social item.")

    assert result["decision"] == "skip"
    assert calls == [
        {
            "prompt": "Decide how to handle this social item.",
            "system_prompt": (
                "You are AEGIS SocialManager. Make a reasoned social decision "
                "and return JSON only."
            ),
            "json_mode": True,
            "profile": "decision",
        }
    ]


def test_social_observe_more_is_a_terminal_non_action(tmp_path: Path) -> None:
    llm = SimpleNamespace(
        generate=lambda **_kwargs: SimpleNamespace(
            success=True,
            content=(
                '{"decision":"observe_more","reason":"No response is useful yet",'
                '"directed_to_aegis":false,"mentions_user":false,'
                '"question_detected":false,"reply_expected":false,'
                '"relevance":0.1,"urgency":0.0,"sentiment":"neutral",'
                '"draft_body":""}'
            ),
        )
    )
    manager = SocialManager(data_dir=str(tmp_path), llm=llm)
    item = manager.ingest(
        "agora",
        [{"id": 1, "thread_id": 1, "author": "peer", "body": "An update."}],
    )[0]

    processed = manager.process_new_items([item])[0]

    assert processed.decision == "observe_more"
    assert processed.status.value == "skipped"


def test_dismissed_repairs_are_not_active_errors() -> None:
    class Repair:
        def list_history(self, limit=30):
            return [
                {"repair_id": "r1", "timestamp": 10, "error": "old"},
                {"repair_id": "r1", "timestamp": 20, "final_result": "dismissed"},
                {"repair_id": "r2", "timestamp": 30, "error": "active"},
            ]

        def get_status(self):
            return {}

    audit = SimpleNamespace(
        list_recent=lambda _limit: [
            {"action": "browser_failed", "detail": {"error": "historical"}}
        ]
    )
    result = _errors(SimpleNamespace(repair_manager=Repair(), audit_manager=audit))
    assert [item["id"] for item in result["items"]] == ["r2"]
    assert result["items"][0]["created_at"] == 30


def test_recovered_server_connectivity_errors_are_not_active() -> None:
    class Repair:
        def list_history(self, limit=30):
            return [
                {
                    "repair_id": "browser-timeout",
                    "capability_id": "browser-server.page.read",
                    "timestamp": 10,
                    "error": "HTTP execution error: timed out",
                    "final_result": "recorded",
                },
                {
                    "repair_id": "android-permission",
                    "capability_id": "android-server.screen.get_screenshot",
                    "timestamp": 20,
                    "error": "Android permission missing: media_projection",
                    "final_result": "recorded",
                },
            ]

        def get_status(self):
            return {}

    class Status:
        def get_snapshot(self):
            return {
                "browser-server": {"status": "ONLINE"},
                "android-server": {"status": "ONLINE"},
            }

    result = _errors(SimpleNamespace(repair_manager=Repair(), status_manager=Status()))
    assert [item["id"] for item in result["items"]] == ["android-permission"]


def test_recovered_capability_permission_errors_are_not_active() -> None:
    class Repair:
        def list_history(self, limit=30):
            return [
                {
                    "repair_id": "android-permission",
                    "capability_id": "android-server.screen.get_screenshot",
                    "timestamp": 20,
                    "error": "Android permission missing: media_projection",
                    "final_result": "recorded",
                },
            ]

        def get_status(self):
            return {}

    class Status:
        def get_snapshot(self):
            return {
                "android-server": {
                    "status": "ONLINE",
                    "capability_health": {
                        "android-server.screen.get_screenshot": {
                            "available": True,
                            "missing_permissions": [],
                        }
                    },
                }
            }

    result = _errors(SimpleNamespace(repair_manager=Repair(), status_manager=Status()))
    assert result["items"] == []


def test_disabled_and_unconfigured_servers_are_resolved(tmp_path: Path) -> None:
    class Status:
        def __init__(self, value: str) -> None:
            self.value = value

        def get_snapshot(self):
            return {"room-server": {"status": self.value}}

    for value in ("disabled", "unconfigured"):
        manager = HealthAlertManager(
            data_dir=str(tmp_path / value),
            status_manager=Status(value),
        )
        manager._server_enabled = lambda _server_id: True
        manager._check_port = lambda *_args: (_ for _ in ()).throw(
            AssertionError("Resolved server states must not be probed")
        )
        assert manager.check_server_reachable("room-server", "localhost", 50055) is None


def test_data_directory_default_threshold_is_ten_gb(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    (data / "small.json").write_text(json.dumps({"ok": True}), encoding="utf-8")
    manager = HealthAlertManager(data_dir=str(tmp_path / "health"), data_path=str(data))
    assert manager.check_data_dir_size() is None
