"""
Telemetry initialization for lambda-otel-lite.

This module provides the initialization function for OpenTelemetry in AWS Lambda.
"""

import os
from typing import Final
from urllib import parse

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor
from opentelemetry.sdk.trace.export import SpanExporter
from otlp_stdout_span_exporter import OTLPStdoutSpanExporter

from . import ProcessorMode
from .extension import init_extension
from .processor import LambdaSpanProcessor

# Global state
_tracer_provider: TracerProvider | None = None
_processor_mode: Final[ProcessorMode] = ProcessorMode.from_env(
    "LAMBDA_EXTENSION_SPAN_PROCESSOR_MODE", ProcessorMode.SYNC
)


def get_lambda_resource() -> Resource:
    """Create a Resource instance with AWS Lambda attributes and OTEL environment variables.

    This function combines AWS Lambda environment attributes with any OTEL resource attributes
    specified via environment variables (OTEL_RESOURCE_ATTRIBUTES and OTEL_SERVICE_NAME).

    Returns:
        Resource instance with AWS Lambda and OTEL environment attributes
    """
    # Start with Lambda attributes
    function_name = os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
    service_name = os.environ.get("OTEL_SERVICE_NAME", function_name)

    # Create base attributes
    attributes = {
        "cloud.provider": "aws",
        "cloud.region": os.environ.get("AWS_REGION", ""),
        "faas.name": function_name or "",
        "faas.version": os.environ.get("AWS_LAMBDA_FUNCTION_VERSION", ""),
        "faas.instance": os.environ.get("AWS_LAMBDA_LOG_STREAM_NAME", ""),
        "faas.max_memory": os.environ.get("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", ""),
    }

    # Add service name if available
    if service_name:
        attributes["service.name"] = service_name

    # Add OTEL environment resource attributes if present
    env_resources_items = os.environ.get("OTEL_RESOURCE_ATTRIBUTES")
    if env_resources_items:
        for item in env_resources_items.split(","):
            try:
                key, value = item.split("=", maxsplit=1)
            except ValueError:
                continue
            value_url_decoded = parse.unquote(value.strip())
            attributes[key.strip()] = value_url_decoded

    # Create resource and merge with default resource
    resource = Resource(attributes)
    return Resource.create().merge(resource)


def init_telemetry(
    name: str,
    resource: Resource | None = None,
    span_processor: SpanProcessor | None = None,
    exporter: SpanExporter | None = None,
) -> tuple[trace.Tracer, TracerProvider]:
    """Initialize OpenTelemetry with manual OTLP stdout configuration.

    This function provides a flexible way to initialize OpenTelemetry for AWS Lambda,
    with sensible defaults that work well in most cases but allowing customization
    where needed.

    Args:
        name: Name for the tracer (e.g., 'my-service', 'payment-processor')
        resource: Optional custom Resource. Defaults to Lambda resource detection
        span_processor: Optional custom SpanProcessor. Defaults to LambdaSpanProcessor
        exporter: Optional custom SpanExporter. Defaults to OTLPStdoutSpanExporter

    Returns:
        tuple: (tracer, provider) instances
    """
    global _tracer_provider

    # Setup resource
    resource = resource or get_lambda_resource()
    _tracer_provider = TracerProvider(resource=resource)

    # Setup exporter and processor
    if span_processor is None:
        compression_level = int(os.environ.get("OTLP_STDOUT_SPAN_EXPORTER_COMPRESSION_LEVEL", "6"))
        if exporter is None:
            exporter = OTLPStdoutSpanExporter(gzip_level=compression_level)
        span_processor = LambdaSpanProcessor(
            exporter, max_queue_size=int(os.getenv("LAMBDA_SPAN_PROCESSOR_QUEUE_SIZE", "2048"))
        )

    _tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(_tracer_provider)

    # Initialize extension for async and finalize modes
    if _processor_mode in [ProcessorMode.ASYNC, ProcessorMode.FINALIZE]:
        init_extension(_processor_mode, _tracer_provider)

    return trace.get_tracer(name), _tracer_provider
