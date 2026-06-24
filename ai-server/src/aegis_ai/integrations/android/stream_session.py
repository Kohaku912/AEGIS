"""Reverse-stream Android session support."""

from __future__ import annotations

import json
import queue
import threading
import time
import uuid
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

from generated.aegis import android_server_pb2, common_pb2


@dataclass
class AndroidStreamResult:
    """Result returned by an Android reverse-stream command."""

    command_id: str
    capability_id: str
    ok: bool
    result: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    status_code: int = 0


class AndroidStreamSession:
    """A live Android reverse-stream connection."""

    def __init__(
        self,
        *,
        device_id: str,
        connection_id: str,
        on_message: Callable[[Any, AndroidStreamSession], None],
        on_disconnect: Callable[[AndroidStreamSession, str], None],
    ) -> None:
        self.device_id = device_id
        self.connection_id = connection_id
        self.connection_mode = "reverse_stream"
        self.created_at_ms = int(time.time() * 1000)
        self.last_seen_ms = self.created_at_ms
        self._on_message = on_message
        self._on_disconnect = on_disconnect
        self._commands: queue.Queue[Any] = queue.Queue()
        self._pending: dict[str, queue.Queue[AndroidStreamResult]] = {}
        self._lock = threading.RLock()
        self._closed = threading.Event()

    @property
    def closed(self) -> bool:
        return self._closed.is_set()

    def start_reader(self, request_iterator: Iterable[Any]) -> None:
        thread = threading.Thread(
            target=self._read_loop,
            args=(request_iterator,),
            name=f"android-stream-{self.device_id}",
            daemon=True,
        )
        thread.start()

    def command_generator(self) -> Iterable[Any]:
        ack = android_server_pb2.AndroidServerCommand(
            ack=android_server_pb2.AndroidStreamAck(
                connection_id=self.connection_id,
                status=common_pb2.Status(code=0, message="ok"),
            )
        )
        yield ack
        while not self._closed.is_set():
            try:
                command = self._commands.get(timeout=20)
            except queue.Empty:
                yield android_server_pb2.AndroidServerCommand(
                    heartbeat=android_server_pb2.AndroidServerHeartbeat(
                        timestamp_ms=int(time.time() * 1000),
                    )
                )
                continue
            if command is None:
                break
            yield command

    def invoke(
        self,
        capability_id: str,
        method: str,
        params: dict[str, Any],
        timeout_seconds: float = 30.0,
    ) -> dict[str, Any]:
        """Send an invoke command over the stream and wait for the result."""
        if self._closed.is_set():
            return {
                "error": "Android reverse stream is disconnected",
                "code": "ANDROID_SERVER_UNAVAILABLE",
                "capability_id": capability_id,
            }
        command_id = f"cmd_{uuid.uuid4().hex[:12]}"
        result_queue: queue.Queue[AndroidStreamResult] = queue.Queue(maxsize=1)
        with self._lock:
            self._pending[command_id] = result_queue
        command = android_server_pb2.AndroidServerCommand(
            invoke=android_server_pb2.AndroidInvokeCommand(
                command_id=command_id,
                capability_id=capability_id,
                method=method,
                params_json=json.dumps(params or {}, ensure_ascii=False),
                timeout_ms=int(timeout_seconds * 1000),
                correlation_id=command_id,
            )
        )
        self._commands.put(command)
        try:
            result = result_queue.get(timeout=timeout_seconds)
        except queue.Empty:
            with self._lock:
                self._pending.pop(command_id, None)
            return {
                "error": "Android reverse stream command timed out",
                "code": "ANDROID_SERVER_UNAVAILABLE",
                "capability_id": capability_id,
                "command_id": command_id,
            }
        if not result.ok:
            code = result.result.get("code") if isinstance(result.result, dict) else ""
            return {
                "error": result.error or "Android command failed",
                "code": code or "ANDROID_COMMAND_FAILED",
                "status_code": result.status_code,
                "capability_id": capability_id,
                "command_id": command_id,
                "result": result.result,
            }
        output = dict(result.result)
        output.setdefault("command_id", command_id)
        output.setdefault("connection_mode", self.connection_mode)
        return output

    def send_approval(self, approval_id: str, title: str, body: str, state: str, summary: dict[str, Any]) -> None:
        """Send an approval overlay command to Android as one fanout surface."""
        command = android_server_pb2.AndroidServerCommand(
            approval_request=android_server_pb2.AndroidApprovalCommand(
                approval_id=approval_id,
                title=title,
                body=body,
                state=state,
                summary_json=json.dumps(summary, ensure_ascii=False),
            )
        )
        self._commands.put(command)

    def send_chat_update(self, messages: list[dict[str, Any]]) -> None:
        """Push shared chat history updates to Android Home."""
        command = android_server_pb2.AndroidServerCommand(
            chat_update=android_server_pb2.AndroidChatUpdate(
                messages=[
                    android_server_pb2.AndroidChatHistoryMessage(
                        message_id=str(item.get("message_id", "")),
                        role=str(item.get("role", "")),
                        text=str(item.get("text", "")),
                        timestamp_ms=int(item.get("timestamp_ms", 0) or 0),
                        image=str(item.get("image", "")),
                        conversation_id=str(item.get("conversation_id", "")),
                        source=str(item.get("source", "")),
                    )
                    for item in messages
                ]
            )
        )
        self._commands.put(command)

    def close(self, reason: str = "") -> None:
        if self._closed.is_set():
            return
        self._closed.set()
        try:
            self._commands.put(
                android_server_pb2.AndroidServerCommand(
                    stop=android_server_pb2.AndroidStopCommand(reason=reason or "closed")
                )
            )
            self._commands.put(None)
        except Exception:
            pass

    def handle_result(self, message: Any) -> None:
        result_json = message.result_json or "{}"
        try:
            parsed = json.loads(result_json)
        except json.JSONDecodeError:
            parsed = {"raw": result_json}
        result = AndroidStreamResult(
            command_id=message.command_id,
            capability_id=message.capability_id,
            ok=message.status.code == 0,
            result=parsed if isinstance(parsed, dict) else {"result": parsed},
            error=message.status.message if message.status.code else "",
            status_code=message.status.code,
        )
        with self._lock:
            result_queue = self._pending.pop(message.command_id, None)
        if result_queue is not None:
            result_queue.put(result)

    def _read_loop(self, request_iterator: Iterable[Any]) -> None:
        try:
            for message in request_iterator:
                self.last_seen_ms = int(time.time() * 1000)
                self._on_message(message, self)
        except Exception as exc:
            self._on_disconnect(self, str(exc))
        finally:
            self.close("client disconnected")
            self._on_disconnect(self, "client disconnected")
