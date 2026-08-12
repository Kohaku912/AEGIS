"""Temporal client and worker bootstrap."""

from __future__ import annotations

import asyncio
import logging
import os
import threading
from typing import Any

logger = logging.getLogger("aegis_ai.temporal.client")

_RUNTIME: "TemporalRuntime | None" = None


class TemporalRuntime:
    """Thin facade over Temporal client + background worker."""

    def __init__(
        self,
        address: str,
        *,
        namespace: str = "default",
        task_queue: str = "aegis-tasks",
    ) -> None:
        self.address = address
        self.namespace = namespace
        self.task_queue = task_queue
        self._client: Any = None
        self._worker_thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._ready = threading.Event()

    @property
    def enabled(self) -> bool:
        return bool(self.address)

    def start_worker(self, **deps: Any) -> None:
        if not self.enabled or self._worker_thread is not None:
            return

        from aegis_ai.temporal.activities.llm_activity import configure_llm_activity_context
        from aegis_ai.temporal.activities.tool_activity import configure_activity_context

        configure_activity_context(**deps)
        configure_llm_activity_context(**deps)

        def _run() -> None:
            asyncio.run(self._worker_main())

        self._worker_thread = threading.Thread(target=_run, name="aegis-temporal-worker", daemon=True)
        self._worker_thread.start()
        self._ready.wait(timeout=30)

    async def _worker_main(self) -> None:
        try:
            from temporalio.client import Client
            from temporalio.worker import Worker

            from aegis_ai.temporal.activities.llm_activity import llm_generate_activity
            from aegis_ai.temporal.activities.tool_activity import execute_tool_step_activity
            from aegis_ai.temporal.workflows.task_workflow import TaskWorkflow
        except Exception as exc:
            logger.warning("Temporal packages unavailable: %s", exc)
            self._ready.set()
            return

        self._loop = asyncio.get_running_loop()
        self._client = await Client.connect(self.address, namespace=self.namespace)
        worker = Worker(
            self._client,
            task_queue=self.task_queue,
            workflows=[TaskWorkflow],
            activities=[execute_tool_step_activity, llm_generate_activity],
        )
        self._ready.set()
        logger.info("Temporal worker started queue=%s address=%s", self.task_queue, self.address)
        await worker.run()

    async def start_task_workflow(self, task_id: str, plan: dict[str, Any]) -> str:
        if self._client is None:
            raise RuntimeError("Temporal client not connected")
        from aegis_ai.temporal.workflows.task_workflow import TaskWorkflow

        handle = await self._client.start_workflow(
            TaskWorkflow.run,
            task_id,
            plan,
            id=f"task-{task_id}",
            task_queue=self.task_queue,
        )
        return handle.id

    async def signal_approval(self, workflow_id: str, approval_id: str = "") -> None:
        if self._client is None:
            raise RuntimeError("Temporal client not connected")
        from aegis_ai.temporal.workflows.task_workflow import TaskWorkflow

        handle = self._client.get_workflow_handle(workflow_id)
        await handle.signal(TaskWorkflow.approval_granted, approval_id)

    def start_task_workflow_sync(self, task_id: str, plan: dict[str, Any]) -> str:
        return self._run_coro(self.start_task_workflow(task_id, plan))

    def signal_approval_sync(self, workflow_id: str, approval_id: str = "") -> None:
        self._run_coro(self.signal_approval(workflow_id, approval_id))

    def _run_coro(self, coro: Any) -> Any:
        if self._loop is None or not self._loop.is_running():
            return asyncio.run(coro)
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=120)


def get_temporal_runtime() -> TemporalRuntime | None:
    return _RUNTIME


def init_temporal_runtime(**worker_deps: Any) -> TemporalRuntime | None:
    global _RUNTIME
    address = os.getenv("TEMPORAL_ADDRESS", "").strip()
    if not address:
        logger.info("Temporal disabled (TEMPORAL_ADDRESS unset)")
        return None
    if _RUNTIME is None:
        _RUNTIME = TemporalRuntime(
            address=address,
            namespace=os.getenv("TEMPORAL_NAMESPACE", "default"),
            task_queue=os.getenv("TEMPORAL_TASK_QUEUE", "aegis-tasks"),
        )
    _RUNTIME.start_worker(**worker_deps)
    return _RUNTIME
