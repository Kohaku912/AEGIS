# AEGIS Agent Runtime Patterns

This document describes the standard execution patterns introduced by the platform hardening work (schema boundaries, OTel, event journal, Temporal, and existing LangGraph agents).

## Composition root

`AegisRuntime` (`ai-server/src/aegis_ai/runtime.py`) is the sole composition root. External entry points (Flask dashboard, gRPC, autonomous loop) must not construct managers or brokers directly.

## Policy + schema gate

All capability invocations go through `ToolBroker.execute()`:

- Manifest arguments are validated with Pydantic + JSON Schema at invoke time.
- `PolicyEngine` is always consulted before execution.
- Completion verification can use screenshot or `ui_tree` observations (Android + PC).

## Durable orchestration (Temporal)

When `TEMPORAL_ADDRESS` is set:

- User-facing multi-step tasks start `TaskWorkflow` (`aegis_ai/temporal/workflows/task_workflow.py`).
- Tool steps run as activities (`execute_tool_step_activity`) with idempotency keys `task_id:step_id`.
- Approval waits use workflow signals (`approval_granted`).
- Resume API: `POST /api/tasks/{task_id}/continue`.

Autonomous desire ticks remain in-process and are not Temporal workflows (Phase 3 scope).

## Reasoning graph (LangGraph)

LangGraph is used for single-session reasoning subgraphs (for example Support Agent). Pattern:

1. LangGraph decides the next reasoning step inside a session.
2. Side effects and durable steps are executed via Temporal activities or `ToolBroker` (never directly from graph nodes).

## Event journal + projections

Full-fidelity events append to `data/journal/events.jsonl` via `JournalStore`.

- `JournalProjector` writes UI summaries into `EventManager` (bounded hot window).
- Audit log remains the compliance source of truth; OTel traces are for live debugging.

## Correlation context

`aegis_ai/audit/context.py` propagates `trace_id`, `span_id`, `workflow_id`, and audit group IDs through Flask middleware and gRPC ingress.

## Observability

OpenTelemetry bootstrap lives in `aegis_ai/observability/otel_tracing.py`:

- Flask + gRPC auto-instrumentation when packages are installed.
- Manual spans on tool execution, LLM calls, and autonomous ticks.
- OTLP export to Jaeger/Tempo when `OTEL_EXPORTER_OTLP_ENDPOINT` is configured.

## Adding new capabilities

1. Add JSON manifest under `ai-server/capabilities/builtin/<server>/...`.
2. Ensure CI passes `tests/test_manifest_schemas.py`.
3. Route execution through server executor / app executor — no hardcoded capability IDs in Python.
