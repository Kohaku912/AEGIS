"""OpenTelemetry bootstrap and span helpers for AEGIS."""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Any, Iterator

from aegis_ai.audit.context import get_audit_group

logger = logging.getLogger("aegis_ai.observability.otel_tracing")

_initialized = False
_meter = None


def init_tracing() -> None:
    """Initialize OpenTelemetry tracing (OTLP if configured; Console fallback)."""
    global _initialized, _meter
    if _initialized:
        return

    try:
        from opentelemetry import metrics, trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor
    except Exception as exc:
        logger.debug("OpenTelemetry not available; tracing disabled: %s", exc)
        _initialized = True
        return

    service_name = os.getenv("AEGIS_OTEL_SERVICE_NAME", "aegis-ai-server")
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    if endpoint:
        try:
            exporter = OTLPSpanExporter(endpoint=endpoint, insecure="http://" in endpoint)
        except TypeError:
            exporter = OTLPSpanExporter(endpoint=endpoint)  # type: ignore[call-arg]
        provider.add_span_processor(BatchSpanProcessor(exporter))
        try:
            from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

            reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=endpoint, insecure="http://" in endpoint))
            metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))
            _meter = metrics.get_meter("aegis_ai")
        except Exception:
            logger.debug("OTel metrics exporter unavailable", exc_info=True)
        logger.info("OTel tracing enabled (OTLP): endpoint=%s", endpoint)
    else:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        metrics.set_meter_provider(MeterProvider(resource=resource))
        _meter = metrics.get_meter("aegis_ai")
        logger.info("OTel tracing enabled (Console fallback): service=%s", service_name)

    trace.set_tracer_provider(provider)
    _initialized = True


def instrument_flask(app: Any) -> None:
    """Auto-instrument a Flask app when instrumentation package is available."""
    try:
        from opentelemetry.instrumentation.flask import FlaskInstrumentor

        FlaskInstrumentor().instrument_app(app)
        logger.info("Flask OTel instrumentation enabled")
    except Exception:
        logger.debug("Flask OTel instrumentation unavailable", exc_info=True)


def instrument_grpc_server(server: Any) -> None:
    """Auto-instrument a gRPC server when instrumentation package is available."""
    try:
        from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer

        GrpcInstrumentorServer().instrument(server=server)
        logger.info("gRPC OTel instrumentation enabled")
    except Exception:
        logger.debug("gRPC OTel instrumentation unavailable", exc_info=True)


def record_capability_invocation(capability_id: str, *, success: bool, duration_ms: float) -> None:
    """Record capability health metrics when OTel metrics are configured."""
    if _meter is None:
        return
    try:
        counter = _meter.create_counter("aegis.capability.invocations")
        histogram = _meter.create_histogram("aegis.capability.duration_ms")
        attrs = {"capability.id": capability_id, "success": success}
        counter.add(1, attrs)
        histogram.record(duration_ms, attrs)
    except Exception:
        logger.debug("Failed to record capability metric", exc_info=True)


def current_trace_metadata() -> dict[str, Any]:
    """Return OTel + audit correlation fields for journal/audit records."""
    meta: dict[str, Any] = {}
    ctx = get_audit_group()
    if ctx is not None:
        if ctx.trace_id:
            meta["trace_id"] = ctx.trace_id
        if ctx.span_id:
            meta["span_id"] = ctx.span_id
        if ctx.workflow_id:
            meta["workflow_id"] = ctx.workflow_id
        if ctx.task_id:
            meta["task_id"] = ctx.task_id
        if ctx.group_id:
            meta["group_id"] = ctx.group_id
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        span_ctx = span.get_span_context() if span is not None else None
        if span_ctx is not None and getattr(span_ctx, "is_valid", False):
            meta["otel_trace_id"] = format(span_ctx.trace_id, "032x")
            meta["otel_span_id"] = format(span_ctx.span_id, "016x")
    except Exception:
        pass
    return meta


def _span_correlation_attributes() -> dict[str, Any]:
    ctx = get_audit_group()
    if ctx is None:
        return {}
    attrs: dict[str, Any] = {}
    if ctx.trace_id:
        attrs["aegis.trace_id"] = ctx.trace_id
    if ctx.span_id:
        attrs["aegis.span_id"] = ctx.span_id
    if ctx.workflow_id:
        attrs["aegis.workflow_id"] = ctx.workflow_id
    if ctx.group_id:
        attrs["aegis.audit_group_id"] = ctx.group_id
    return attrs


@contextmanager
def start_span(name: str, **attributes: Any) -> Iterator[Any]:
    """Start a span if tracing is initialized; otherwise, act as a no-op."""
    try:
        from opentelemetry import trace
    except Exception:
        yield None
        return

    tracer = trace.get_tracer("aegis_ai")
    attrs = {**_span_correlation_attributes(), **attributes}
    try:
        with tracer.start_as_current_span(name, attributes=attrs) as span:
            yield span
    except TypeError:
        with tracer.start_as_current_span(name) as span:
            try:
                for k, v in attrs.items():
                    span.set_attribute(k, v)
            except Exception:
                pass
            yield span


__all__ = [
    "init_tracing",
    "instrument_flask",
    "instrument_grpc_server",
    "record_capability_invocation",
    "current_trace_metadata",
    "start_span",
]
