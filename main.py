import os
import random
import time

from fastapi import FastAPI, HTTPException
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "fastapi-observability-demo")
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
resource = Resource.create({"service.name": SERVICE_NAME, "service.version": "1.0.0"})
trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)))
trace.set_tracer_provider(trace_provider)
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=OTLP_ENDPOINT, insecure=True), export_interval_millis=5000)
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)
request_counter = meter.create_counter("demo.requests", description="Requests handled")
checkout_latency = meter.create_histogram("demo.checkout.duration", unit="ms")
app = FastAPI(title="OpenTelemetry FastAPI Demo", version="1.0.0")
FastAPIInstrumentor.instrument_app(app)

@app.get("/health")
def health() -> dict[str, str]:
    request_counter.add(1, {"endpoint": "health"})
    return {"status": "healthy", "service": SERVICE_NAME}

@app.get("/products/{product_id}")
def get_product(product_id: int) -> dict[str, object]:
    request_counter.add(1, {"endpoint": "product"})
    if product_id < 1:
        raise HTTPException(status_code=400, detail="product_id must be positive")
    with tracer.start_as_current_span("catalog.lookup") as span:
        span.set_attribute("product.id", product_id)
        return {"id": product_id, "name": f"Demo product {product_id}", "available": True}

@app.post("/checkout/{product_id}")
def checkout(product_id: int) -> dict[str, object]:
    request_counter.add(1, {"endpoint": "checkout"})
    if product_id < 1:
        raise HTTPException(status_code=400, detail="product_id must be positive")
    started = time.perf_counter()
    with tracer.start_as_current_span("checkout.process") as span:
        span.set_attribute("product.id", product_id)
        time.sleep(random.uniform(0.02, 0.08))
        duration_ms = (time.perf_counter() - started) * 1000
        checkout_latency.record(duration_ms, {"status": "accepted"})
        return {"product_id": product_id, "status": "accepted", "duration_ms": round(duration_ms, 2)}
