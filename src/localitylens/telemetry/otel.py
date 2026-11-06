"""OpenTelemetry export of job-attempt traces (opt-in; off by default).

Each stored :class:`~localitylens.telemetry.trace.RecordTrace` becomes one span,
``localitylens.job_attempt``, with child spans for the timed stages (extract, validate,
retrieve, propose) laid end to end from their measured durations. Span attributes are the
trace's own allowlisted fields, prefixed ``localitylens.``: IDs, hashes, versions, counts,
timings and codes. Label text and coordinates are never attributes, because the trace schema
cannot hold them.

Turn it on with ``LOCALITYLENS_OTEL``:

* ``console``: print spans (local debugging);
* ``otlp``: send them to an OpenTelemetry collector, configured by the standard
  ``OTEL_EXPORTER_OTLP_*`` variables. Needs the ``otel`` extra
  (``uv sync --extra otel``).

The provider is kept in this module, not set globally, so tests and embedding programs can
install their own.
"""

from __future__ import annotations

import os
import time
from typing import Any, Final

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    SpanExporter,
)
from opentelemetry.trace import Status, StatusCode, set_span_in_context

from localitylens.telemetry.trace import TELEMETRY_VERSION, RecordTrace

OTEL_ENV: Final = "LOCALITYLENS_OTEL"
SPAN_NAME: Final = "localitylens.job_attempt"
_STAGES: Final = ("extract_ms", "validate_ms", "retrieve_ms", "propose_ms")

_provider: TracerProvider | None = None


def _resource() -> Resource:
    return Resource.create({"service.name": "localitylens",
                            "localitylens.telemetry_version": TELEMETRY_VERSION})  # fmt: skip


def install(exporter: SpanExporter, *, batch: bool = False) -> TracerProvider:
    """Use ``exporter`` for job-attempt spans. Returns the provider (call ``shutdown`` on it)."""
    global _provider
    provider = TracerProvider(resource=_resource())
    processor = BatchSpanProcessor(exporter) if batch else SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)
    _provider = provider
    return provider


def uninstall() -> None:
    global _provider
    if _provider is not None:
        _provider.shutdown()
    _provider = None


def configure_from_env() -> TracerProvider | None:
    """Install the exporter named by ``LOCALITYLENS_OTEL`` (``console`` / ``otlp``), if any."""
    mode = os.environ.get(OTEL_ENV, "").strip().lower()
    if not mode or mode == "off":
        return None
    if mode == "console":
        return install(ConsoleSpanExporter())
    if mode == "otlp":
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        except ImportError as exc:
            raise RuntimeError(
                "LOCALITYLENS_OTEL=otlp needs the otel extra: uv sync --extra otel"
            ) from exc
        return install(OTLPSpanExporter(), batch=True)
    raise ValueError(f"{OTEL_ENV}={mode!r}: expected console, otlp or off")


def enabled() -> bool:
    return _provider is not None


def _attributes(trace: RecordTrace) -> dict[str, Any]:
    """The trace's fields as flat span attributes (scalars and lists of strings only)."""
    data = trace.model_dump(mode="json", exclude_none=True)
    out: dict[str, Any] = {}

    def put(prefix: str, value: Any) -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                put(f"{prefix}.{k}", v)
        elif isinstance(value, list):
            out[prefix] = [str(v) for v in value]
        else:
            out[prefix] = value

    for key, value in data.items():
        put(f"localitylens.{key}", value)
    return out


def record(trace: RecordTrace) -> None:
    """Export one attempt as a span (no-op unless an exporter is installed)."""
    if _provider is None:
        return
    tracer = _provider.get_tracer("localitylens.jobs")
    end = time.time_ns()
    total = trace.stages.total_ms
    start = end - int((total or 0.0) * 1_000_000)
    span = tracer.start_span(SPAN_NAME, start_time=start, attributes=_attributes(trace))
    if trace.outcome.startswith(("failed:", "retry:")):
        span.set_status(Status(StatusCode.ERROR, trace.outcome))
    ctx = set_span_in_context(span)
    cursor = start
    for stage in _STAGES:
        ms = getattr(trace.stages, stage)
        if ms is None:
            continue
        child_end = cursor + int(ms * 1_000_000)
        child = tracer.start_span(f"localitylens.{stage.removesuffix('_ms')}", context=ctx,
                                  start_time=cursor)  # fmt: skip
        child.end(end_time=child_end)
        cursor = child_end
    span.end(end_time=end)
