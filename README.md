# OpenTelemetry FastAPI Demo

A compact observability reference service demonstrating distributed tracing, metrics, health checks, and OTLP export from a FastAPI application.

## Architecture

- FastAPI service with health, product, and simulated checkout endpoints
- Automatic HTTP instrumentation with OpenTelemetry
- Custom request counters and latency histograms
- OTLP export to an OpenTelemetry Collector
- Docker Compose for local startup
- Lightweight API tests

## Technology stack

Python 3.12, FastAPI, Uvicorn, OpenTelemetry SDK, OTLP, OpenTelemetry Collector, Docker Compose, and Pytest.

## Run locally

```bash
docker compose up --build
```

The API is available at `http://localhost:8000`, with OpenAPI documentation at `/docs`.

## Example requests

```bash
curl http://localhost:8000/health
curl http://localhost:8000/products/42
curl -X POST http://localhost:8000/checkout/42
```

## Purpose

This is a sanitized technical demonstration. It contains no employer, customer, or proprietary product source code.
