FROM python:3.11-slim

LABEL org.opencontainers.image.authors="Florian Schweikert <kelvan@ist-total.org>"

WORKDIR /gardena-smartsystem-prometheus-exporter

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ADD . $WORKDIR

RUN uv sync --no-dev --no-cache

# Prometheus Metrics
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "--host=0.0.0.0", "gardena_smartsystem_prometheus_exporter.serve:app"]
