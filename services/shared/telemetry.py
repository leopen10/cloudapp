"""Tracage distribue OpenTelemetry (facultatif).

Actif uniquement si OTEL_EXPORTER_OTLP_ENDPOINT est defini (par exemple http://jaeger:4318) :
sans cette variable, ce module ne fait rien et n'importe aucune bibliotheque OpenTelemetry.
Une erreur de telemetrie ne doit jamais empecher un service de demarrer.
"""
import os


def setup_tracing(app, service_name, instrument_db=True):
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return False
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(provider)

        # /metrics (Prometheus) et /health (controles de sante) sont appeles en boucle : hors traces.
        FastAPIInstrumentor.instrument_app(app, excluded_urls="metrics,health", exclude_spans=["receive", "send"])
        # Propage l'en-tete traceparent vers les services appeles (Gateway -> services).
        HTTPXClientInstrumentor().instrument()

        if instrument_db:
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
            from database import engine

            SQLAlchemyInstrumentor().instrument(engine=engine)

        print(f"[telemetry] tracage actif pour '{service_name}' vers {endpoint}", flush=True)
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[telemetry] tracage desactive ({type(exc).__name__}: {exc})", flush=True)
        return False
