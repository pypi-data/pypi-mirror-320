import logging
import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, ResourceAttributes
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SpanExporter,
)
from pydantic import BaseModel


class TraceConfig(BaseModel):
    # trace basic config
    ak: Optional[str] = None
    sk: Optional[str] = None
    topic: Optional[str] = None
    region: Optional[str] = None

    # batch exporter config
    max_queue_size: Optional[int] = None
    schedule_delay_millis: Optional[float] = None
    max_export_batch_size: Optional[int] = None
    export_timeout_millis: Optional[float] = None

    def __init__(
        self,
        ak: Optional[str] = None,
        sk: Optional[str] = None,
        topic: Optional[str] = None,
        region: Optional[str] = None,
        max_queue_size: Optional[int] = None,
        schedule_delay_millis: Optional[float] = None,
        max_export_batch_size: Optional[int] = None,
        export_timeout_millis: Optional[float] = None,
    ):
        super().__init__(
            ak=ak or os.getenv("VOLC_ACCESSKEY", ""),
            sk=sk or os.getenv("VOLC_SECRETKEY", ""),
            topic=topic or os.getenv("TRACE_TOPIC", ""),
            region=region or os.getenv("REGION", "cn-beijing"),
            max_queue_size=max_queue_size,
            schedule_delay_millis=schedule_delay_millis,
            max_export_batch_size=max_export_batch_size,
            export_timeout_millis=export_timeout_millis,
        )


def setup_tracing(
    endpoint: Optional[str] = None,
    trace_on: bool = True,
    trace_config: Optional[TraceConfig] = None,
) -> None:
    if not trace_on:
        return

    # ensure only initialize once
    provider = trace._TRACER_PROVIDER
    if provider is not None:
        return

    exporter: SpanExporter = ConsoleSpanExporter()
    resource: Resource = Resource.create(
        {
            ResourceAttributes.SERVICE_NAME: "bot",
            ResourceAttributes.HOST_NAME: _get_host_name(),
        },
        schema_url="https://opentelemetry.io/schemas/1.4.0",
    )

    if not trace_config:
        trace_config = TraceConfig()

    if endpoint:
        headers = {
            "x-tls-otel-tracetopic": trace_config.topic or os.getenv("TRACE_TOPIC", ""),
            "x-tls-otel-ak": trace_config.ak or os.getenv("VOLC_ACCESSKEY", ""),
            "x-tls-otel-sk": trace_config.sk or os.getenv("VOLC_SECRETKEY", ""),
            "x-tls-otel-region": trace_config.region
            or os.getenv("REGION", "cn-beijing"),
        }
        logging.info(f"initialize tls trace info: {headers}")
        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True, headers=headers)  # type: ignore

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        BatchSpanProcessor(
            exporter,
            max_queue_size=trace_config.max_queue_size,  # type: ignore
            schedule_delay_millis=trace_config.schedule_delay_millis,  # type: ignore
            max_export_batch_size=trace_config.max_export_batch_size,  # type: ignore
            export_timeout_millis=trace_config.export_timeout_millis,  # type: ignore
        )
    )
    trace.set_tracer_provider(provider)


def _get_host_name() -> str:
    # default env key
    host_name = os.getenv("HOSTNAME", "")
    if not host_name and os.getenv("IS_LOCAL") is None:
        # faas env key
        host_name = os.getenv("_BYTEFAAS_POD_NAME", "")
    return host_name
