from django.apps import AppConfig
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.instrumentation.django import DjangoInstrumentor

from charity import settings


class TelemetryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telemetry'

    def ready(self):
        trace.set_tracer_provider(TracerProvider(resource=Resource.create({
                "service.name": settings.APP_NAME,
            })))
        tracer_provider = trace.get_tracer_provider()

        span_processor = BatchSpanProcessor(ConsoleSpanExporter())
        tracer_provider.add_span_processor(span_processor)

        DjangoInstrumentor().instrument()
