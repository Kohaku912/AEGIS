"""Presentation Engine MVP — unit / integration tests."""

from __future__ import annotations

import json
import os
import tempfile
import time
from types import SimpleNamespace

import pytest

from aegis_ai.presentation.models import (
    DeliverySpec,
    Importance,
    InteractionMode,
    InteractionSpec,
    LifecycleSpec,
    Modality,
    PlacementSpec,
    PresentationRequest,
    PresentationSpec,
    PresentationStatus,
)
from aegis_ai.presentation.object_store import PresentationObjectStore
from aegis_ai.presentation.planner import plan_presentation
from aegis_ai.presentation.device_router import (
    DashboardAdapter,
    DeviceRouter,
    OverlayBroadcastAdapter,
    XRPendingAdapter,
)
from aegis_ai.presentation.manager import PresentationManager


# ── Helpers ──────────────────────────────────────────────────────


def _make_request(**overrides) -> PresentationRequest:
    defaults = dict(
        source="test",
        intent="verify",
        title="Hello",
        summary="World",
        content={"text": "payload"},
        targets=["dashboard"],
        ttl_ms=60_000,
    )
    defaults.update(overrides)
    return PresentationRequest(**defaults)


def _make_manager(tmp_path: str) -> PresentationManager:
    store = PresentationObjectStore(data_dir=tmp_path)
    router = DeviceRouter(
        dashboard_adapter=DashboardAdapter(),
        overlay_adapter=OverlayBroadcastAdapter(core_capability_client=None),
        xr_adapter=XRPendingAdapter(),
    )
    return PresentationManager(object_store=store, device_router=router, data_dir=tmp_path)


# ── Spec creation ────────────────────────────────────────────────


class TestPresentationSpec:
    def test_roundtrip(self):
        spec = PresentationSpec(
            presentation_id="p1",
            source="test",
            intent="verify",
            importance=Importance.HIGH,
            modality=Modality.CHART_PANEL,
            title="Chart",
            summary="A chart",
            content={"data": [1, 2, 3]},
        )
        d = spec.to_dict()
        restored = PresentationSpec.from_dict(d)
        assert restored.presentation_id == "p1"
        assert restored.importance == Importance.HIGH
        assert restored.modality == Modality.CHART_PANEL
        assert restored.content == {"data": [1, 2, 3]}

    def test_safety_fields_absent(self):
        spec = PresentationSpec()
        d = spec.to_dict()
        assert "safety" not in d
        assert "safety_level" not in d
        assert "requires_approval" not in d


# ── Planner ──────────────────────────────────────────────────────


class TestPlanner:
    def test_basic_plan(self):
        req = _make_request()
        spec = plan_presentation(req)
        assert spec.presentation_id.startswith("pres_")
        assert spec.status == PresentationStatus.PENDING
        assert spec.modality == Modality.TEXT_CARD
        assert spec.importance == Importance.NORMAL
        assert spec.lifecycle.expires_at_ms > spec.created_at_ms

    def test_invalid_modality_fallback(self):
        req = _make_request(modality="bogus")
        spec = plan_presentation(req)
        assert spec.modality == Modality.TEXT_CARD

    def test_invalid_importance_fallback(self):
        req = _make_request(importance="bogus")
        spec = plan_presentation(req)
        assert spec.importance == Importance.NORMAL

    def test_ttl_clamped_minimum(self):
        req = _make_request(ttl_ms=0)
        spec = plan_presentation(req)
        assert spec.delivery.ttl_ms >= 1_000


# ── Object store ─────────────────────────────────────────────────


class TestObjectStore:
    def test_put_get_list(self, tmp_path):
        store = PresentationObjectStore(data_dir=str(tmp_path))
        spec = plan_presentation(_make_request())
        store.put(spec)
        assert store.count() == 1
        assert store.get(spec.presentation_id) is not None
        assert len(store.list_active()) == 1

    def test_persistence_survives_reload(self, tmp_path):
        store = PresentationObjectStore(data_dir=str(tmp_path))
        spec = plan_presentation(_make_request())
        store.put(spec)
        pid = spec.presentation_id

        store2 = PresentationObjectStore(data_dir=str(tmp_path))
        assert store2.get(pid) is not None
        assert store2.count() == 1

    def test_delete(self, tmp_path):
        store = PresentationObjectStore(data_dir=str(tmp_path))
        spec = plan_presentation(_make_request())
        store.put(spec)
        assert store.delete(spec.presentation_id) is True
        assert store.count() == 0
        assert store.delete("nonexistent") is False


# ── Device router ────────────────────────────────────────────────


class TestDeviceRouter:
    def test_dashboard_delivery(self):
        router = DeviceRouter(dashboard_adapter=DashboardAdapter())
        spec = plan_presentation(_make_request(targets=["dashboard"]))
        result = router.deliver(spec)
        assert result["ok"] is True
        assert "dashboard" in result["delivered"]
        assert spec.status == PresentationStatus.DELIVERED

    def test_xr_delivery(self):
        xr = XRPendingAdapter()
        router = DeviceRouter(xr_adapter=xr)
        spec = plan_presentation(_make_request(targets=["xr_scene"]))
        result = router.deliver(spec)
        assert result["ok"] is True
        assert xr.count() == 1
        drained = xr.drain()
        assert len(drained) == 1

    def test_unknown_target_fails(self):
        router = DeviceRouter()
        spec = plan_presentation(_make_request(targets=["bogus"]))
        result = router.deliver(spec)
        assert result["ok"] is False
        assert spec.status == PresentationStatus.FAILED

    def test_overlay_skips_non_text(self):
        router = DeviceRouter(overlay_adapter=OverlayBroadcastAdapter(core_capability_client=None))
        spec = plan_presentation(_make_request(targets=["pc_overlay"], modality="chart_panel"))
        result = router.deliver(spec)
        assert result["results"]["pc_overlay"].get("skipped") is True


# ── Manager ──────────────────────────────────────────────────────


class TestPresentationManager:
    def test_present_and_list(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        result = mgr.present(_make_request().to_dict())
        assert result["ok"] is True
        pid = result["presentation"]["presentation_id"]
        assert pid.startswith("pres_")

        active = mgr.list_active()
        assert len(active) == 1
        assert active[0]["presentation_id"] == pid

    def test_dismiss(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        result = mgr.present(_make_request().to_dict())
        pid = result["presentation"]["presentation_id"]
        dismiss_result = mgr.dismiss(pid)
        assert dismiss_result["ok"] is True
        assert dismiss_result["presentation"]["status"] == "dismissed"
        assert len(mgr.list_active()) == 0

    def test_dismiss_not_found(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        assert mgr.dismiss("nonexistent")["ok"] is False

    def test_user_action(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        result = mgr.present(_make_request().to_dict())
        pid = result["presentation"]["presentation_id"]
        action_result = mgr.user_action(pid, {"type": "click", "button": "ok"})
        assert action_result["ok"] is True
        pres = mgr.get(pid)
        assert len(pres["user_actions"]) == 1

    def test_update(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        result = mgr.present(_make_request().to_dict())
        pid = result["presentation"]["presentation_id"]
        update_result = mgr.update(pid, {"title": "Updated", "summary": "New"})
        assert update_result["ok"] is True
        assert update_result["presentation"]["title"] == "Updated"
        assert update_result["presentation"]["revision"] == 1

    def test_get_status(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        mgr.present(_make_request().to_dict())
        status = mgr.get_status()
        assert status["total"] == 1
        assert status["active"] == 1


# ── Event publication ────────────────────────────────────────────


class TestEventPublication:
    def test_events_published(self, tmp_path):
        events: list[dict] = []

        class FakeEventManager:
            def publish_event(self, **kwargs):
                events.append(kwargs)

        store = PresentationObjectStore(data_dir=str(tmp_path))
        router = DeviceRouter(dashboard_adapter=DashboardAdapter())
        mgr = PresentationManager(
            object_store=store,
            device_router=router,
            event_manager=FakeEventManager(),
            data_dir=str(tmp_path),
        )
        result = mgr.present(_make_request().to_dict())
        pid = result["presentation"]["presentation_id"]

        event_types = [e["event_type"] for e in events]
        assert "presentation.created" in event_types
        assert "presentation.delivered" in event_types

        mgr.dismiss(pid)
        event_types = [e["event_type"] for e in events]
        assert "presentation.dismissed" in event_types


# ── Capability client integration ────────────────────────────────


class TestCapabilityClient:
    def test_invoke_present(self, tmp_path):
        from aegis_ai.core_capabilities import AegisCoreCapabilityClient

        events: list[dict] = []

        class FakeEventManager:
            def publish_event(self, **kwargs):
                events.append(kwargs)

        class FakeAuditManager:
            def append(self, **kwargs):
                pass

        store = PresentationObjectStore(data_dir=str(tmp_path))
        router = DeviceRouter(dashboard_adapter=DashboardAdapter())
        mgr = PresentationManager(
            object_store=store,
            device_router=router,
            event_manager=FakeEventManager(),
            audit_manager=FakeAuditManager(),
            data_dir=str(tmp_path),
        )
        client = AegisCoreCapabilityClient(
            data_dir=str(tmp_path),
            server_executor=SimpleNamespace(),
            personal_managers={"presentation_manager": mgr},
        )
        result = client.invoke_capability("ai-server.presentation.present", {
            "title": "Test",
            "content": {"text": "hello"},
        })
        assert result["ok"] is True
        assert "presentation" in result

    def test_invoke_list(self, tmp_path):
        from aegis_ai.core_capabilities import AegisCoreCapabilityClient

        store = PresentationObjectStore(data_dir=str(tmp_path))
        router = DeviceRouter(dashboard_adapter=DashboardAdapter())
        mgr = PresentationManager(object_store=store, device_router=router, data_dir=str(tmp_path))
        client = AegisCoreCapabilityClient(
            data_dir=str(tmp_path),
            server_executor=SimpleNamespace(),
            personal_managers={"presentation_manager": mgr},
        )
        result = client.invoke_capability("ai-server.presentation.list", {})
        assert result["ok"] is True
        assert "presentations" in result

    def test_invoke_dismiss(self, tmp_path):
        from aegis_ai.core_capabilities import AegisCoreCapabilityClient

        store = PresentationObjectStore(data_dir=str(tmp_path))
        router = DeviceRouter(dashboard_adapter=DashboardAdapter())
        mgr = PresentationManager(object_store=store, device_router=router, data_dir=str(tmp_path))
        present_result = mgr.present(_make_request().to_dict())
        pid = present_result["presentation"]["presentation_id"]

        client = AegisCoreCapabilityClient(
            data_dir=str(tmp_path),
            server_executor=SimpleNamespace(),
            personal_managers={"presentation_manager": mgr},
        )
        result = client.invoke_capability("ai-server.presentation.dismiss", {"presentation_id": pid})
        assert result["ok"] is True

    def test_invoke_action(self, tmp_path):
        from aegis_ai.core_capabilities import AegisCoreCapabilityClient

        store = PresentationObjectStore(data_dir=str(tmp_path))
        router = DeviceRouter(dashboard_adapter=DashboardAdapter())
        mgr = PresentationManager(object_store=store, device_router=router, data_dir=str(tmp_path))
        present_result = mgr.present(_make_request().to_dict())
        pid = present_result["presentation"]["presentation_id"]

        client = AegisCoreCapabilityClient(
            data_dir=str(tmp_path),
            server_executor=SimpleNamespace(),
            personal_managers={"presentation_manager": mgr},
        )
        result = client.invoke_capability("ai-server.presentation.action", {
            "presentation_id": pid,
            "action": {"type": "click", "button": "ok"},
        })
        assert result["ok"] is True
