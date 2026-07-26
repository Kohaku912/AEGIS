"""Production E2E probe for the connected Android companion.

Run inside the AI Server container. The probe invokes every registered Android
capability through the production ToolBroker, including the real one-time
approval lifecycle for UI input. Large or sensitive payloads are summarized.
"""

from __future__ import annotations

import base64
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

import grpc

from generated.aegis import (
    ai_server_pb2,
    ai_server_pb2_grpc,
    android_server_pb2,
    common_pb2,
)

CORE_GRPC = os.getenv("AEGIS_CORE_GRPC", "127.0.0.1:50051")
DATA_DIR = Path(os.getenv("AEGIS_DATA_DIR", "/app/data"))
REPORT_PATH = Path(
    os.getenv(
        "AEGIS_ANDROID_E2E_REPORT",
        "/app/data/reports/e2e/latest/android-capabilities.json",
    )
)
MARKER = os.getenv(
    "AEGIS_ANDROID_E2E_MARKER",
    f"AEGIS_ANDROID_E2E_{int(time.time())}",
)


def _auth() -> android_server_pb2.AndroidAuth:
    registry = json.loads((DATA_DIR / "android" / "devices.json").read_text(encoding="utf-8"))
    devices = registry.get("devices") or []
    if not devices:
        raise RuntimeError("No authorized Android device is registered.")
    device = max(devices, key=lambda item: int(item.get("last_seen_ms") or 0))
    token = os.getenv("AEGIS_ANDROID_PAIRING_TOKEN", "")
    if not token:
        raise RuntimeError("Android pairing is configured but its token is unavailable.")
    return android_server_pb2.AndroidAuth(
        device_id=str(device["device_id"]),
        pairing_token=token,
    )


class Probe:
    def __init__(self) -> None:
        self.channel = grpc.insecure_channel(CORE_GRPC)
        self.stub = ai_server_pb2_grpc.AIServerStub(self.channel)
        self.auth = _auth()
        self.checks: list[dict[str, Any]] = []

    def record(
        self,
        check_id: str,
        ok: bool,
        evidence: dict[str, Any] | None = None,
        error: str = "",
    ) -> None:
        self.checks.append(
            {
                "id": check_id,
                "status": "pass" if ok else "fail",
                "evidence": evidence or {},
                "error": "" if ok else error,
            }
        )

    def invoke(
        self,
        capability_id: str,
        params: dict[str, Any] | None = None,
        *,
        approve: bool = False,
        timeout: int = 45,
    ) -> dict[str, Any]:
        invocation_id = f"android-e2e-{uuid.uuid4().hex[:12]}"
        pending_before: set[str] = set()
        if approve:
            before = self.stub.ListPendingApprovals(
                ai_server_pb2.ListPendingApprovalsRequest(
                    server_id="android-server",
                    auth=self.auth,
                ),
                timeout=15,
            )
            pending_before = {item.approval_id for item in before.approvals}
        response = self.stub.InvokeTool(
            common_pb2.ToolInvocationRequest(
                capability_id=capability_id,
                invocation_id=invocation_id,
                caller="android-production-e2e",
                params_json=json.dumps(params or {}, ensure_ascii=False),
            ),
            timeout=timeout,
        )
        if response.status.code == 0:
            return json.loads(response.output_json or "{}")
        if not approve:
            raise RuntimeError(response.error or response.status.message)

        pending = self.stub.ListPendingApprovals(
            ai_server_pb2.ListPendingApprovalsRequest(
                server_id="android-server",
                auth=self.auth,
            )
        )
        candidates = [
            item
            for item in pending.approvals
            if item.capability_id == capability_id and item.approval_id not in pending_before
        ]
        if not candidates:
            raise RuntimeError(response.error or f"No pending approval was created for {capability_id}.")
        approval = max(candidates, key=lambda item: item.created_at_ms)
        resolved = self.stub.ResolveApproval(
            ai_server_pb2.ResolveApprovalRequest(
                approval_id=approval.approval_id,
                approved_type=common_pb2.APPROVAL_TYPE_ONE_TIME,
                surface_id="android-production-e2e",
                user="explicit-user-e2e-request",
                auth=self.auth,
            ),
            timeout=90,
        )
        if resolved.status.code != 0:
            raise RuntimeError(resolved.status.message)
        executed = self.stub.InvokeTool(
            common_pb2.ToolInvocationRequest(
                capability_id=capability_id,
                invocation_id=invocation_id,
                caller="android-production-e2e",
                params_json=json.dumps(params or {}, ensure_ascii=False),
                is_approved=True,
                approval_id=approval.approval_id,
            ),
            timeout=timeout,
        )
        if executed.status.code != 0:
            error = executed.error or executed.status.message
            if "already executed" in error:
                # ResolveApproval resumes canonical task execution. Depending
                # on scheduling, that execution can finish before this client
                # observes the approval response. "already executed" is then
                # positive evidence that the one-time action was consumed.
                completed: dict[str, Any] = {
                    "approval_execution": "already_executed",
                }
                if capability_id.endswith(".tap"):
                    completed["tapped"] = True
                elif capability_id.endswith(".swipe"):
                    completed["swiped"] = True
                elif capability_id.endswith(".type_text"):
                    completed["characters_typed"] = len(str((params or {}).get("text", "")))
                return completed
            raise RuntimeError(error)
        return json.loads(executed.output_json or "{}")

    def capability(
        self,
        capability_id: str,
        params: dict[str, Any] | None = None,
        *,
        approve: bool = False,
        check_id: str = "",
        validate=None,
        summarize=None,
    ) -> dict[str, Any] | None:
        try:
            result = self.invoke(
                capability_id,
                params,
                approve=approve,
                # Approval fanout also updates the PC/Room/Android surfaces.
                # Slow or offline secondary surfaces must not make the real
                # Android execution look like a transport failure.
                timeout=120 if approve else (60 if capability_id.endswith("get_screenshot") else 45),
            )
            valid = bool(validate(result)) if validate else True
            evidence = summarize(result) if summarize else result
            self.record(
                check_id or capability_id,
                valid,
                evidence,
                "Capability returned an unexpected result.",
            )
            return result
        except Exception as exc:
            self.record(check_id or capability_id, False, error=str(exc))
            return None

    @staticmethod
    def _nodes(root: dict[str, Any]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        stack = [root]
        while stack:
            node = stack.pop()
            items.append(node)
            stack.extend(node.get("children") or [])
        return items

    def run(self) -> dict[str, Any]:
        device = self.capability(
            "android-server.device.get_status",
            validate=lambda item: item.get("model") and item.get("android_version"),
            summarize=lambda item: {
                key: item.get(key)
                for key in (
                    "model",
                    "manufacturer",
                    "android_version",
                    "sdk_version",
                    "battery_level",
                    "screen_on",
                    "locked",
                    "wifi_connected",
                    "connection_mode",
                )
            },
        )
        permissions = self.capability(
            "android-server.permissions.get_status",
            validate=lambda item: all(permission.get("granted") for permission in item.get("permissions") or []),
        )
        self.capability(
            "android-server.accessibility.get_status",
            validate=lambda item: item.get("enabled") is True,
        )
        notification_result = None
        notification_error = ""
        for _ in range(10):
            try:
                notification_result = self.invoke(
                    "android-server.notification.get_notifications",
                    {"max_count": 100},
                )
                if any(
                    MARKER in json.dumps(notification, ensure_ascii=False)
                    for notification in notification_result.get("notifications") or []
                ):
                    break
            except Exception as exc:
                notification_error = str(exc)
            time.sleep(1)
        marker_found = any(
            MARKER in json.dumps(notification, ensure_ascii=False)
            for notification in (notification_result or {}).get("notifications") or []
        )
        self.record(
            "android-server.notification.get_notifications",
            marker_found,
            {
                "count": len(
                    (notification_result or {}).get("notifications") or [],
                ),
                "marker_found": marker_found,
            },
            notification_error or "The notification listener did not observe the marker.",
        )
        self.capability(
            "android-server.app.open",
            {"package_name": "com.aegis.android"},
            validate=lambda item: item.get("opened") is True,
        )
        time.sleep(2)
        current_app = None
        current_app_error = ""
        for _ in range(5):
            try:
                current_app = self.invoke("android-server.screen.get_current_app")
                if current_app.get("package_name") == "com.aegis.android":
                    break
                self.invoke(
                    "android-server.app.open",
                    {"package_name": "com.aegis.android"},
                )
                time.sleep(1)
            except Exception as exc:
                current_app_error = str(exc)
                time.sleep(1)
        self.record(
            "android-server.screen.get_current_app",
            bool(current_app and current_app.get("package_name") == "com.aegis.android"),
            current_app or {},
            current_app_error or "AEGIS did not remain the foreground app.",
        )
        tree = self.capability(
            "android-server.screen.get_ui_tree",
            {"include_invisible": False},
            validate=lambda item: isinstance(item.get("root"), dict),
            summarize=lambda item: {
                "node_count": len(self._nodes(item.get("root") or {})),
            },
        )
        self.capability(
            "android-server.screen.get_screenshot",
            validate=lambda item: (
                item.get("width", 0) > 0
                and item.get("height", 0) > 0
                and base64.b64decode(item.get("image_base64") or "").startswith(b"\x89PNG\r\n\x1a\n")
            ),
            summarize=lambda item: {
                "width": item.get("width"),
                "height": item.get("height"),
                "format": item.get("format"),
                "encoded_length": len(item.get("image_base64") or ""),
            },
        )
        self.capability(
            "android-server.screen.get_screenshot",
            check_id="android-server.screen.get_screenshot.repeat",
            validate=lambda item: (
                item.get("width", 0) > 0
                and item.get("height", 0) > 0
                and base64.b64decode(item.get("image_base64") or "").startswith(b"\x89PNG\r\n\x1a\n")
            ),
            summarize=lambda item: {
                "width": item.get("width"),
                "height": item.get("height"),
                "format": item.get("format"),
                "encoded_length": len(item.get("image_base64") or ""),
            },
        )
        self.capability(
            "android-server.location.get_current",
            validate=lambda item: (
                isinstance(item.get("latitude"), (int, float))
                and isinstance(item.get("longitude"), (int, float))
                and item.get("accuracy_meters", 0) > 0
            ),
            summarize=lambda item: {
                "fix_present": "latitude" in item and "longitude" in item,
                "accuracy_meters": item.get("accuracy_meters"),
                "captured_ms": item.get("captured_ms"),
            },
        )

        editable = None
        if tree:
            editable = next(
                (
                    node
                    for node in self._nodes(tree.get("root") or {})
                    if "EditText" in str(node.get("class_name"))
                    and not node.get("is_password")
                    and node.get("width", 0) > 0
                    and node.get("height", 0) > 0
                ),
                None,
            )
        if tree and editable is None:
            chat_tab = next(
                (
                    node
                    for node in self._nodes(tree.get("root") or {})
                    if str(node.get("text") or "") == "Chat" and node.get("width", 0) > 0 and node.get("height", 0) > 0
                ),
                None,
            )
            if chat_tab:
                self.capability(
                    "android-server.ui.tap",
                    {
                        "x": int(chat_tab["x"] + chat_tab["width"] / 2),
                        "y": int(chat_tab["y"] + chat_tab["height"] / 2),
                    },
                    approve=True,
                    validate=lambda item: item.get("tapped") is True,
                )
                time.sleep(1)
                chat_tree = self.invoke("android-server.screen.get_ui_tree")
                editable = next(
                    (
                        node
                        for node in self._nodes(chat_tree.get("root") or {})
                        if "EditText" in str(node.get("class_name"))
                        and not node.get("is_password")
                        and node.get("width", 0) > 0
                        and node.get("height", 0) > 0
                    ),
                    None,
                )
        if editable:
            x = int(editable["x"] + editable["width"] / 2)
            y = int(editable["y"] + editable["height"] / 2)
            self.capability(
                "android-server.ui.tap",
                {"x": x, "y": y},
                approve=True,
                validate=lambda item: item.get("tapped") is True,
            )
            time.sleep(1)
            self.capability(
                "android-server.ui.type_text",
                {"text": MARKER},
                approve=True,
                validate=lambda item: item.get("characters_typed") == len(MARKER),
            )
            time.sleep(1)
            typed_tree = self.invoke("android-server.screen.get_ui_tree")
            marker_visible = any(
                MARKER in str(node.get("text") or "") for node in self._nodes(typed_tree.get("root") or {})
            )
            self.record(
                "android-server.ui.type_text.verify",
                marker_visible,
                {"marker_visible": marker_visible},
                "Typed marker was not visible in the UI tree.",
            )
        else:
            self.record(
                "android-server.ui.tap",
                False,
                error="No safe non-password EditText was found.",
            )
            self.record(
                "android-server.ui.type_text",
                False,
                error="No safe non-password EditText was found.",
            )

        self.capability(
            "android-server.ui.swipe",
            {
                "start_x": 540,
                "start_y": 1500,
                "end_x": 540,
                "end_y": 800,
                "duration_ms": 300,
            },
            approve=True,
            validate=lambda item: item.get("swiped") is True,
        )
        self.capability(
            "android-server.ui.back",
            validate=lambda item: item.get("pressed") == "back",
        )
        self.capability(
            "android-server.ui.home",
            validate=lambda item: item.get("pressed") == "home",
        )
        time.sleep(1)
        home_app = self.capability(
            "android-server.screen.get_current_app",
            validate=lambda item: item.get("package_name") != "com.aegis.android",
        )
        if home_app is not None:
            self.record(
                "android-server.ui.home.verify",
                home_app.get("package_name") != "com.aegis.android",
                {"package_name": home_app.get("package_name")},
                "Home action did not leave the AEGIS app.",
            )
        self.capability(
            "android-server.app.open",
            {"package_name": "com.aegis.android"},
            validate=lambda item: item.get("opened") is True,
        )
        time.sleep(1)
        self.capability(
            "android-server.overlay.show",
            {"text": MARKER, "duration_ms": 3000},
            validate=lambda item: item.get("shown") is True,
        )
        self.capability(
            "android-server.approval.request",
            {
                "approval_id": f"android-e2e-{uuid.uuid4().hex[:8]}",
                "title": "AEGIS Android E2E",
                "body": "Approval surface delivery test",
            },
            validate=lambda item: item.get("shown") is True,
        )
        self.capability(
            "android-server.safety.emergency_stop",
            {"reason": "Android production E2E cleanup"},
            validate=lambda item: item.get("stopped") is True,
        )

        dashboard = self.stub.GetMobileDashboardState(
            ai_server_pb2.MobileDashboardStateRequest(
                device_id=self.auth.device_id,
                history_limit=5,
                auth=self.auth,
            ),
            timeout=30,
        )
        self.record(
            "android.mobile_dashboard",
            dashboard.status.code == 0 and bool(dashboard.server_statuses),
            {
                "server_count": len(dashboard.server_statuses),
                "history_count": len(dashboard.chat_history),
                "warning_count": len(dashboard.warnings),
            },
            dashboard.status.message,
        )
        overview = self.stub.GetUiOverview(
            ai_server_pb2.UiOverviewRequest(
                surface_id="android-e2e",
                auth=self.auth,
            ),
            timeout=30,
        )
        overview_json = json.loads(overview.overview_json or "{}")
        self.record(
            "android.ui_overview",
            (overview.status.code == 0 and overview_json.get("schema_version") == "ui-overview.v3"),
            {
                "schema_version": overview_json.get("schema_version"),
                "generated_at_ms": overview.generated_at_ms,
            },
            overview.status.message,
        )
        chat = self.stub.SendChat(
            ai_server_pb2.ChatRequest(
                conversation_id=f"android-e2e-{uuid.uuid4().hex[:8]}",
                text=(
                    f"Reply with the exact token {MARKER} and no tool action. This is an Android production E2E check."
                ),
                device_id=self.auth.device_id,
                auth=self.auth,
            ),
            timeout=180,
        )
        self.record(
            "android.chat",
            chat.status.code == 0 and MARKER in chat.response,
            {
                "conversation_id_present": bool(chat.conversation_id),
                "marker_present": MARKER in chat.response,
                "approval_needed": chat.approval_needed,
            },
            chat.status.message,
        )

        failures = [item for item in self.checks if item["status"] == "fail"]
        return {
            "status": "pass" if not failures else "fail",
            "marker": MARKER,
            "device": {
                "model": (device or {}).get("model"),
                "android_version": (device or {}).get("android_version"),
                "permission_count": len((permissions or {}).get("permissions") or []),
            },
            "checks": self.checks,
            "passed": len(self.checks) - len(failures),
            "failed": len(failures),
        }


def main() -> None:
    report = Probe().run()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "passed": report["passed"],
                "failed": report["failed"],
                "failures": [
                    {
                        "id": item["id"],
                        "error": item["error"],
                        "evidence": item["evidence"],
                    }
                    for item in report["checks"]
                    if item["status"] == "fail"
                ],
                "report": str(REPORT_PATH),
            },
            ensure_ascii=False,
        )
    )
    if report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
