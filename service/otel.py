import logging
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from config.setting import get_settings

logger = logging.getLogger("PW-Admin-Backend")

_provider: TracerProvider | None = None


def _parse_headers(raw: str) -> dict[str, str]:
    headers: dict[str, str] = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair or "=" not in pair:
            continue
        key, _, value = pair.partition("=")
        headers[key.strip()] = value.strip()
    return headers


def setup_telemetry() -> None:
    global _provider

    settings = get_settings()
    if not settings.OTEL_ENABLED:
        logger.info("OpenTelemetry disabled (set OTEL_ENABLED=true to enable).")
        return
    if _provider is not None:
        return

    resource = Resource.create(
        {
            SERVICE_NAME: settings.SERVICE_NAME,
            "deployment.environment": settings.ENVIRONMENT,
        }
    )
    _provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=f"{settings.OTEL_EXPORTER_OTLP_ENDPOINT.rstrip('/')}/v1/traces",
        headers=_parse_headers(settings.OTEL_EXPORTER_OTLP_HEADERS),
    )
    _provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(_provider)
    logger.info(
        "OpenTelemetry enabled, exporting traces to %s",
        settings.OTEL_EXPORTER_OTLP_ENDPOINT,
    )


def shutdown_telemetry() -> None:
    global _provider

    if _provider is None:
        return
    _provider.shutdown()
    _provider = None
