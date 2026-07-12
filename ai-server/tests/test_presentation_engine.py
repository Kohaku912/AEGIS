"""Presentation Engine MVP — unit / integration tests."""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from flask import Flask
import pytest
from jsonschema import validate

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
from aegis_ai.presentation.planner import plan_presentation, plan_presentation_v2
from aegis_ai.presentation.schemas import infer_modality, normalize_content, schema_for_modality
from aegis_ai.presentation.preferences import PresentationPreferences
from aegis_ai.presentation.device_router import (
    DashboardAdapter,
    DeviceRouter,
    OverlayBroadcastAdapter,
    XRPendingAdapter,
)
from aegis_ai.presentation.manager import PresentationManager
from aegis_ai.autonomous.autonomous_loop import AutonomousLoop
from aegis_ai.task.execution_engine import TaskExecutionEngine
from aegis_ai.task_plan import PlanStep, StepStatus, TaskPlan
from aegis_ai.web import manager_routes
from aegis_ai.web.routes.presentation import init_presentation_routes
from aegis_ai.web import chat_tools


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

    def test_new_modality_values(self):
        assert Modality.IMAGE.value == "image"
        assert Modality.VIDEO.value == "video"
        assert Modality.SPEECH.value == "speech"
        assert Modality.HUD.value == "hud"

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


class TestPresentationSchemas:
    def test_image_modality_schema(self):
        content = normalize_content(
            "image",
            {"url": "https://example.com/image.png", "alt": "Example", "width": 640, "height": 480},
        )
        validate(instance=content, schema=schema_for_modality("image"))
        assert content == {
            "url": "https://example.com/image.png",
            "alt": "Example",
            "width": 640,
            "height": 480,
        }
        assert infer_modality({"url": "https://example.com/image.png"}) == "image"

    def test_speech_modality_schema(self):
        content = normalize_content("speech", {"text": "Hello", "voice": "alloy", "language": "en-US", "speed": 1.2})
        validate(instance=content, schema=schema_for_modality("speech"))
        assert content == {
            "text": "Hello",
            "voice": "alloy",
            "language": "en-US",
            "speed": 1.2,
        }
        assert infer_modality({"text": "Hello", "voice": "alloy"}) == "speech"

    def test_hud_modality_schema(self):
        content = normalize_content("hud", {"elements": [{"kind": "label", "text": "Status"}], "position": "top"})
        validate(instance=content, schema=schema_for_modality("hud"))
        assert content == {
            "elements": [{"kind": "label", "text": "Status"}],
            "position": "top",
        }
        assert infer_modality({"elements": [{"kind": "label", "text": "Status"}], "position": "top"}) == "hud"

    def test_planner_v2_fallback_to_deterministic(self, monkeypatch):
        calls: list[bool] = []

        def fake_plan(request):
            calls.append(True)
            return PresentationSpec(
                presentation_id="pres_det",
                source=request.source,
                intent=request.intent,
                title=request.title,
                summary=request.summary,
                content=request.content,
            )

        monkeypatch.setattr("aegis_ai.presentation.planner.plan_presentation", fake_plan)
        req = _make_request(modality="bogus", content={"text": "hello"})
        spec = asyncio.run(plan_presentation_v2(req, llm_router=None))
        assert spec.presentation_id == "pres_det"
        assert calls == [True]


# ── Evaluation / regression ───────────────────────────────────────


class TestPresentationEvaluation:
    def test_presentation_shown_at_right_time(self, tmp_path):
        mgr = _make_manager(str(tmp_path))

        result = mgr.present(_make_request(ttl_ms=5_000).to_dict())
        pid = result["presentation"]["presentation_id"]

        assert result["presentation"]["status"] == "delivered"

        time.sleep(0.1)

        stored = mgr.get(pid)
        assert stored is not None
        assert stored["status"] == "delivered"
        assert pid in {item["presentation_id"] for item in mgr.list_active()}
        assert stored["lifecycle"]["expires_at_ms"] > int(time.time() * 1000)

    def test_content_correctness_text_card(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        content = {"text": "Exact text payload", "footer": "Footer line", "icon": "info"}

        result = mgr.present(_make_request(modality="text_card", content=content).to_dict())
        pid = result["presentation"]["presentation_id"]

        stored = mgr.get(pid)
        assert stored is not None
        assert stored["content"] == content

    def test_content_correctness_chart_panel(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        content = {
            "chart_type": "bar",
            "data": {"series": [1, 3, 2], "labels": ["Q1", "Q2", "Q3"]},
            "options": {"stacked": True, "legend": False},
        }

        result = mgr.present(_make_request(modality="chart_panel", content=content).to_dict())
        pid = result["presentation"]["presentation_id"]

        stored = mgr.get(pid)
        assert stored is not None
        assert stored["content"]["chart_type"] == content["chart_type"]
        assert stored["content"]["data"] == content["data"]
        assert stored["content"]["options"] == content["options"]

    def test_modality_selection_by_content(self):
        assert infer_modality({"model_url": "https://example.com/model.gltf"}) == "gltf_model"
        assert infer_modality({"diagram_type": "flowchart"}) == "diagram_panel"
        assert infer_modality({"chart_type": "bar"}) == "chart_panel"
        assert infer_modality({"message": "Hello"}) == "overlay_short"
        assert infer_modality({"text": "Plain text"}) == "text_card"


class TestPresentationRegression:
    def test_no_safety_fields_in_output(self, tmp_path):
        mgr = _make_manager(str(tmp_path))

        result = mgr.present(_make_request().to_dict())
        presentation = result["presentation"]

        assert "safety" not in presentation
        assert "safety_level" not in presentation
        assert "requires_approval" not in presentation

    def test_empty_content_handled(self, tmp_path):
        mgr = _make_manager(str(tmp_path))

        result = mgr.present(_make_request(content={}).to_dict())
        pid = result["presentation"]["presentation_id"]

        stored = mgr.get(pid)
        assert stored is not None
        assert stored["content"] == {}
        assert stored["modality"] == "text_card"

    def test_long_title_handled(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        long_title = "T" * 1000

        result = mgr.present(_make_request(title=long_title).to_dict())
        pid = result["presentation"]["presentation_id"]

        stored = mgr.get(pid)
        assert stored is not None
        assert stored["title"] == long_title

    def test_special_characters_in_content(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        content = {
            "text": "<script>alert('xss')</script>",
            "footer": "<img src=x onerror=alert(1)>",
            "icon": "<b>safe</b>",
        }

        result = mgr.present(_make_request(content=content).to_dict())
        pid = result["presentation"]["presentation_id"]

        stored = mgr.get(pid)
        assert stored is not None
        assert stored["content"] == content

    def test_concurrent_presentations(self, tmp_path):
        mgr = _make_manager(str(tmp_path))

        results = [mgr.present(_make_request(title=f"Presentation {i}").to_dict()) for i in range(10)]
        ids = [result["presentation"]["presentation_id"] for result in results]

        assert len(set(ids)) == 10
        assert all(mgr.get(pid) is not None for pid in ids)


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
    class FakeOverlayClient:
        def __init__(self):
            self.calls: list[dict[str, Any]] = []

        def _broadcast_overlay(self, payload):
            self.calls.append(payload)
            return {"ok": True, "delivered": ["pc"], "payload": payload}

    def test_dashboard_delivery(self):
        router = DeviceRouter(dashboard_adapter=DashboardAdapter())
        spec = plan_presentation(_make_request(targets=["dashboard"]))
        result = router.deliver(spec)
        assert result["ok"] is True
        assert "dashboard" in result["delivered"]
        assert spec.status == PresentationStatus.DELIVERED

    def test_delivery_state_tracking(self):
        router = DeviceRouter(dashboard_adapter=DashboardAdapter())
        spec = plan_presentation(_make_request(targets=["dashboard", "xr_scene"]))

        result = router.deliver(spec)

        assert result["ok"] is True
        assert spec.delivery_state["delivered_count"] == 2
        assert spec.delivery_state["failed_count"] == 0
        assert set(spec.delivery_state["targets"]) == {"dashboard", "xr_scene"}
        assert spec.delivery_state["targets"]["dashboard"]["ok"] is True
        assert spec.delivery_state["targets"]["xr_scene"]["ok"] is True
        assert isinstance(spec.delivery_state["delivered_at_ms"], int)

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

    def test_overlay_chart_summary(self):
        client = self.FakeOverlayClient()
        router = DeviceRouter(overlay_adapter=OverlayBroadcastAdapter(core_capability_client=client))
        spec = plan_presentation(
            _make_request(
                targets=["pc"],
                modality="chart_panel",
                summary="Sales trend",
                content={"chart_type": "bar", "data": {"series": [1, 2, 3], "labels": ["Q1", "Q2", "Q3"]}},
            )
        )
        result = router.deliver(spec)
        assert result["ok"] is True
        assert client.calls
        assert client.calls[0]["message"] == "Sales trend | chart: bar | data keys: series, labels"

    def test_overlay_3d_skipped(self):
        client = self.FakeOverlayClient()
        router = DeviceRouter(overlay_adapter=OverlayBroadcastAdapter(core_capability_client=client))
        spec = plan_presentation(_make_request(targets=["pc_overlay"], modality="gltf_model"))
        result = router.deliver(spec)
        assert result["ok"] is True
        assert result["results"]["pc_overlay"] == {
            "ok": True,
            "skipped": True,
            "reason": "3D not supported in overlay",
        }
        assert client.calls == []

    def test_delivery_state_tracks_failures(self):
        router = DeviceRouter(overlay_adapter=OverlayBroadcastAdapter(core_capability_client=None))
        spec = plan_presentation(_make_request(targets=["pc_overlay"], modality="overlay_short"))

        result = router.deliver(spec)

        assert result["ok"] is False
        assert spec.delivery_state["delivered_count"] == 0
        assert spec.delivery_state["failed_count"] == 1
        assert spec.delivery_state["targets"]["pc_overlay"]["ok"] is False
        assert spec.delivery_state["targets"]["pc_overlay"]["error"] == "CoreCapabilityClient unavailable"


# ── Manager ──────────────────────────────────────────────────────


class TestPresentationManager:
    def test_interruption_controller_keeps_dashboard_visible(self, tmp_path):
        calls: list[dict] = []

        class FakeInterruptionController:
            def decide(self, notification):
                calls.append(notification)
                return {"decision": "suppress", "reason": "quiet hours"}

        class FakeRouter:
            def __init__(self):
                self.called = False

            def deliver(self, spec):
                self.called = True
                return {"ok": True}

        router = FakeRouter()
        mgr = PresentationManager(
            object_store=PresentationObjectStore(data_dir=str(tmp_path)),
            device_router=router,
            interruption_controller=FakeInterruptionController(),
            data_dir=str(tmp_path),
        )

        result = mgr.present(_make_request(importance="low").to_dict())

        assert result["ok"] is True
        assert result["delivery"]["ok"] is True
        assert result["delivery"]["suppressed"] is True
        assert result["delivery"]["reason"] == "quiet hours"
        assert result["presentation"]["status"] == "delivered"
        assert result["presentation"]["metadata"]["interruption"]["decision"] == "suppress"
        assert result["presentation"]["metadata"]["interruption"]["reason"] == "quiet hours"
        assert calls == [{"category": "presentation", "severity": "low", "title": "Hello"}]
        assert router.called is True

    def test_interruption_controller_queues_intrusive_only_targets(self, tmp_path):
        class FakeInterruptionController:
            def decide(self, notification):
                return {"decision": "batch_later", "reason": "quiet hours"}

        class FakeRouter:
            def __init__(self):
                self.called = False

            def deliver(self, spec):
                self.called = True
                return {"ok": True}

        router = FakeRouter()
        mgr = PresentationManager(
            object_store=PresentationObjectStore(data_dir=str(tmp_path)),
            device_router=router,
            interruption_controller=FakeInterruptionController(),
            data_dir=str(tmp_path),
        )

        result = mgr.present(_make_request(importance="low", targets=["pc_overlay"]).to_dict())

        assert result["ok"] is True
        assert result["delivery"] == {"ok": False, "suppressed": True, "reason": "quiet hours"}
        assert result["presentation"]["status"] == "queued"
        assert router.called is False

    def test_critical_bypasses_interruption_controller(self, tmp_path):
        calls: list[dict] = []

        class FakeInterruptionController:
            def decide(self, notification):
                calls.append(notification)
                raise AssertionError("critical presentations must bypass interruption control")

        class FakeRouter:
            def __init__(self):
                self.called = False

            def deliver(self, spec):
                self.called = True
                return {"ok": True, "delivered": ["dashboard"]}

        router = FakeRouter()
        mgr = PresentationManager(
            object_store=PresentationObjectStore(data_dir=str(tmp_path)),
            device_router=router,
            interruption_controller=FakeInterruptionController(),
            data_dir=str(tmp_path),
        )

        result = mgr.present(_make_request(importance="critical").to_dict())

        assert result["ok"] is True
        assert result["delivery"]["ok"] is True
        assert result["presentation"]["status"] == "delivered"
        assert router.called is True
        assert calls == []

    def test_present_and_list(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        result = mgr.present(_make_request().to_dict())
        assert result["ok"] is True
        pid = result["presentation"]["presentation_id"]
        assert pid.startswith("pres_")
        assert result["presentation"]["delivery_state"]["delivered_count"] == 1
        assert result["presentation"]["delivery_state"]["targets"]["dashboard"]["ok"] is True

        active = mgr.list_active()
        assert len(active) == 1
        assert active[0]["presentation_id"] == pid

        summaries = mgr.list_summaries()
        assert summaries[0]["presentation_id"] == pid
        assert summaries[0]["_summary_only"] is True
        assert summaries[0]["content"] == {}
        assert summaries[0]["content_size"] > 0

    def test_delivery_state_persisted_after_delivery(self, tmp_path):
        mgr = _make_manager(str(tmp_path))

        result = mgr.present(_make_request(targets=["dashboard", "xr_scene"]).to_dict())
        pid = result["presentation"]["presentation_id"]

        stored = mgr.get(pid)

        assert result["presentation"]["delivery_state"]["delivered_count"] == 2
        assert stored is not None
        assert stored["delivery_state"]["delivered_count"] == 2
        assert set(stored["delivery_state"]["targets"]) == {"dashboard", "xr_scene"}

    def test_important_presentation_creates_notification(self, tmp_path):
        calls: list[dict] = []

        class FakeNotificationManager:
            def create_notification(self, **kwargs):
                calls.append(kwargs)
                return {"notification_id": "notif_123"}

        mgr = PresentationManager(
            object_store=PresentationObjectStore(data_dir=str(tmp_path)),
            device_router=DeviceRouter(dashboard_adapter=DashboardAdapter()),
            notification_manager=FakeNotificationManager(),
            data_dir=str(tmp_path),
        )

        result = mgr.present(_make_request(importance=Importance.HIGH).to_dict())

        assert result["ok"] is True
        assert calls == [{
            "title": "Hello",
            "body": "World",
            "severity": "warning",
            "category": "presentation",
            "channels": ["dashboard"],
        }]
        assert result["presentation"]["metadata"]["notification_id"] == "notif_123"

    def test_dismiss(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        result = mgr.present(_make_request().to_dict())
        pid = result["presentation"]["presentation_id"]
        dismiss_result = mgr.dismiss(pid)
        assert dismiss_result["ok"] is True
        assert dismiss_result["presentation"]["status"] == "dismissed"
        assert len(mgr.list_active()) == 0

    def test_dismiss_syncs_notification(self, tmp_path):
        dismissed: list[str] = []

        class FakeNotificationManager:
            def create_notification(self, **kwargs):
                return {"notification_id": "notif_456"}

            def dismiss_notification(self, notification_id):
                dismissed.append(notification_id)
                return {"ok": True}

        mgr = PresentationManager(
            object_store=PresentationObjectStore(data_dir=str(tmp_path)),
            device_router=DeviceRouter(dashboard_adapter=DashboardAdapter()),
            notification_manager=FakeNotificationManager(),
            data_dir=str(tmp_path),
        )
        result = mgr.present(_make_request(importance=Importance.CRITICAL).to_dict())
        pid = result["presentation"]["presentation_id"]

        dismiss_result = mgr.dismiss(pid)

        assert dismiss_result["ok"] is True
        assert dismissed == ["notif_456"]

    def test_dismiss_not_found(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        assert mgr.dismiss("nonexistent")["ok"] is False

    def test_present_async_uses_v2(self, tmp_path):
        class FakeLLMRouter:
            def __init__(self):
                self.calls: list[dict[str, Any]] = []

            def generate_json(self, prompt, system_prompt="", context_meta=None):
                self.calls.append(
                    {
                        "prompt": prompt,
                        "system_prompt": system_prompt,
                        "context_meta": context_meta,
                    }
                )
                return {
                    "modality": "chart_panel",
                    "targets": ["dashboard"],
                    "content": {"chart_type": "bar", "data": {"series": [1, 2, 3]}},
                }

        mgr = _make_manager(str(tmp_path))
        router = FakeLLMRouter()
        result = asyncio.run(
            mgr.present_async(
                _make_request(targets=["pc_overlay"], content={"data": {"series": [1, 2, 3]}}),
                llm_router=router,
            )
        )

        assert result["ok"] is True
        assert result["presentation"]["modality"] == "chart_panel"
        assert result["presentation"]["delivery"]["targets"] == ["dashboard"]
        assert result["presentation"]["content"] == {
            "chart_type": "bar",
            "data": {"series": [1, 2, 3]},
            "options": {},
        }
        assert router.calls


class TestChatPresentationTool:
    def test_chat_present_info_tool(self):
        captured: list[Any] = []

        class FakePresentationManager:
            def present(self, request):
                captured.append(request)
                return {
                    "ok": True,
                    "presentation": {"presentation_id": "pres_test", "title": request.title},
                    "delivery": {"ok": True},
                }

        runtime = SimpleNamespace(presentation_manager=FakePresentationManager())

        result = chat_tools.execute_tool_call(
            catalog=None,
            function_name="present_info",
            arguments={
                "title": "Task result",
                "summary": "The analysis finished successfully.",
                "content": {"text": "The analysis finished successfully."},
                "modality": "text_card",
                "importance": "high",
            },
            runtime=runtime,
        )

        assert result["ok"] is True
        assert len(captured) == 1
        request = captured[0]
        assert request.title == "Task result"
        assert request.summary == "The analysis finished successfully."
        assert request.modality == "text_card"
        assert request.importance == "high"


class TestTaskCompletionPresentation:
    def test_task_completion_creates_presentation(self, monkeypatch):
        captured: list[Any] = []

        class FakePresentationManager:
            def present(self, request):
                captured.append(request)
                return {"ok": True, "presentation": request.to_dict(), "delivery": {"ok": True}}

        class FakeRuntime:
            presentation_manager = FakePresentationManager()

        class FakeTaskManager:
            def __init__(self):
                self.tasks = {
                    "task_1": {
                        "task_id": "task_1",
                        "title": "Investigate logs",
                        "goal": "Inspect recent failures",
                        "status": "running",
                        "result_summary": "",
                        "priority": 5,
                    }
                }

            def get_task(self, task_id):
                return self.tasks.get(task_id)

            def complete_task(self, task_id, result_summary=""):
                task = self.tasks.get(task_id)
                if task is None:
                    return None
                task["result_summary"] = result_summary
                task["status"] = "completed"
                return task

        monkeypatch.setattr("aegis_ai.runtime.get_runtime", lambda: FakeRuntime())

        engine = TaskExecutionEngine(task_manager=FakeTaskManager())
        plan = TaskPlan(
            plan_id="plan_1",
            interpreted_request="inspect recent failures",
            expected_result="All steps completed",
            steps=[
                PlanStep(
                    step_id="step_1",
                    description="Inspect logs",
                    action_type="info",
                    capability_id="",
                    status=StepStatus.COMPLETED,
                ),
            ],
        )

        engine.apply_task_state("task_1", plan)

        assert len(captured) == 1
        request = captured[0]
        assert request.source == "task_execution_engine"
        assert request.modality == "text_card"
        assert request.summary == "All steps completed"
        assert request.content["task_id"] == "task_1"
        assert request.importance == "high"


class TestAutonomousPresentation:
    def test_autonomous_result_creates_presentation(self, monkeypatch, tmp_path):
        captured: list[Any] = []

        class FakePresentationManager:
            def present(self, request):
                captured.append(request)
                return {"ok": True, "presentation": request.to_dict(), "delivery": {"ok": True}}

        class FakeRuntime:
            presentation_manager = FakePresentationManager()

        monkeypatch.setattr("aegis_ai.runtime.get_runtime", lambda: FakeRuntime())

        loop = AutonomousLoop(data_dir=str(tmp_path))
        loop._present_autonomous_result(
            {"desire": "user_support", "action": "Summarize findings", "capability_id": "ai-server.test"},
            {
                "success": True,
                "result": "A chart was generated successfully.",
                "full_output": {"chart_type": "bar", "series": [1, 2, 3]},
            },
        )

        assert len(captured) == 1
        request = captured[0]
        assert request.source == "autonomous_loop"
        assert request.modality == "chart_panel"
        assert request.importance == "high"
        assert request.summary == "A chart was generated successfully."

    def test_user_action(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        result = mgr.present(_make_request().to_dict())
        pid = result["presentation"]["presentation_id"]
        action_result = mgr.user_action(pid, {"type": "click", "button": "ok"})
        assert action_result["ok"] is True
        pres = mgr.get(pid)
        assert len(pres["user_actions"]) == 1

    def test_preference_learning_records_interactions(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        result = mgr.present(_make_request(modality="chart_panel", placement_zone="sidebar").to_dict())
        pid = result["presentation"]["presentation_id"]

        mgr.user_action(pid, {"type": "click"})

        prefs = mgr.get_preferences()
        assert prefs["interaction_count"] == 1
        assert prefs["modality_scores"]["chart_panel"] == 0.2
        assert prefs["placement_scores"]["sidebar"] == 0.2

    def test_preference_learning_dismiss_decreases_score(self, tmp_path):
        prefs = PresentationPreferences(data_dir=str(tmp_path))

        prefs.record_interaction("chart_panel", "sidebar", "click")
        prefs.record_interaction("chart_panel", "sidebar", "dismiss")

        scores = prefs.get_scores()
        assert scores["modality_scores"]["chart_panel"] == 0.1
        assert scores["placement_scores"]["sidebar"] == 0.1

    def test_preference_learning_click_increases_score(self, tmp_path):
        prefs = PresentationPreferences(data_dir=str(tmp_path))

        prefs.record_interaction("diagram_panel", "main", "click")

        scores = prefs.get_scores()
        assert scores["modality_scores"]["diagram_panel"] == 0.2
        assert scores["placement_scores"]["main"] == 0.2

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

    def test_present_async_uses_v2(self, tmp_path, monkeypatch):
        calls: list[Any] = []

        async def fake_plan(request, llm_router=None):
            calls.append(llm_router)
            return PresentationSpec(
                presentation_id="pres_async",
                source=request.source,
                intent=request.intent,
                title=request.title,
                summary=request.summary,
                content={"text": "async"},
                delivery=DeliverySpec(targets=["dashboard"], ttl_ms=request.ttl_ms),
                placement=PlacementSpec(zone=request.placement_zone),
                interaction=InteractionSpec(mode=InteractionMode.DISMISS_ONLY, actions=request.actions),
                lifecycle=LifecycleSpec(expires_at_ms=int(time.time() * 1000) + request.ttl_ms),
                status=PresentationStatus.PENDING,
                created_at_ms=int(time.time() * 1000),
                updated_at_ms=int(time.time() * 1000),
            )

        monkeypatch.setattr("aegis_ai.presentation.manager.plan_presentation_v2", fake_plan)

        mgr = _make_manager(str(tmp_path))
        result = asyncio.run(mgr.present_async(_make_request().to_dict(), llm_router={"mode": "test"}))

        assert result["ok"] is True
        assert result["presentation"]["presentation_id"] == "pres_async"
        assert calls == [{"mode": "test"}]


class TestXRPendingAPI:
    def test_xr_pending_api(self):
        xr = XRPendingAdapter()
        spec1 = plan_presentation(_make_request(targets=["xr_scene"], title="One"))
        spec2 = plan_presentation(_make_request(targets=["xr_scene"], title="Two"))
        xr.deliver(spec1)
        xr.deliver(spec2)

        runtime = SimpleNamespace(
            presentation_manager=SimpleNamespace(
                _router=SimpleNamespace(_xr=xr),
            )
        )

        app = Flask(__name__)
        manager_routes.init_manager_routes(app, runtime)
        client = app.test_client()

        count_response = client.get("/api/presentations/xr/count")
        assert count_response.status_code == 200
        assert count_response.get_json() == {"count": 2}

        pending_response = client.get("/api/presentations/xr/pending?limit=1")
        assert pending_response.status_code == 200
        pending = pending_response.get_json()["presentations"]
        assert len(pending) == 1
        assert pending[0]["title"] == "One"

        count_response = client.get("/api/presentations/xr/count")
        assert count_response.get_json() == {"count": 1}

        pending_response = client.get("/api/presentations/xr/pending")
        assert len(pending_response.get_json()["presentations"]) == 1


class TestDedicatedDisplayRoute:
    def test_display_route_is_local_only_and_read_only(self, tmp_path):
        mgr = _make_manager(str(tmp_path))
        mgr.present(_make_request(title="Display Ready", summary="Presentation surface only."))

        template_dir = Path(__file__).resolve().parents[1] / "src" / "aegis_ai" / "web" / "templates"
        app = Flask(__name__, template_folder=str(template_dir))
        owner = SimpleNamespace(app=app, _runtime=SimpleNamespace(presentation_manager=mgr))
        init_presentation_routes(owner)
        client = app.test_client()

        page = client.get("/display/presentations", headers={"Host": "127.0.0.1:8090"})
        assert page.status_code == 200
        assert b"presentation display" in page.data
        assert b"Dashboard" not in page.data
        assert b"dismissPresentation" not in page.data

        data = client.get("/display/presentations/data", headers={"Host": "127.0.0.1:8090"})
        payload = data.get_json()
        assert data.status_code == 200
        assert payload["presentations"][0]["title"] == "Display Ready"
        assert "user_actions" not in payload["presentations"][0]

        external = client.get("/display/presentations", headers={"Host": "kawahara.pp.ua"})
        assert external.status_code == 403

    def test_sweeper_expires_presentations(self, tmp_path):
        events: list[dict] = []
        audits: list[dict] = []

        class FakeEventManager:
            def publish_event(self, **kwargs):
                events.append(kwargs)

        class FakeAuditManager:
            def append(self, **kwargs):
                audits.append(kwargs)

        mgr = PresentationManager(
            object_store=PresentationObjectStore(data_dir=str(tmp_path)),
            device_router=DeviceRouter(dashboard_adapter=DashboardAdapter()),
            event_manager=FakeEventManager(),
            audit_manager=FakeAuditManager(),
            data_dir=str(tmp_path),
        )

        now_ms = int(time.time() * 1000)
        spec = PresentationSpec(
            presentation_id="pres_expire",
            source="test",
            intent="verify",
            title="Soon expired",
            summary="TTL test",
            lifecycle=LifecycleSpec(expires_at_ms=now_ms + 100),
            status=PresentationStatus.PENDING,
            created_at_ms=now_ms,
            updated_at_ms=now_ms,
        )
        mgr._store.put(spec)

        time.sleep(0.15)
        mgr._sweep_once()

        stored = mgr.get("pres_expire")
        assert stored is not None
        assert stored["status"] == "expired"
        assert any(event["event_type"] == "presentation.expired" for event in events)
        assert any(audit["action"] == "presentation.expire" for audit in audits)


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
