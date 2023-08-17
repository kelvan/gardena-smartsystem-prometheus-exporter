FROM python:3.11-slim

LABEL org.opencontainers.image.authors="Florian Schweikert <kelvan@ist-total.org>"

WORKDIR /gardena-smartsystem-prometheus-exporter

RUN pip install --no-cache-dir -U pip setuptools wheel poetry

ADD . $WORKDIR

RUN poetry config installer.max-workers 10

RUN poetry install --no-cache --no-interaction --no-ansi

# Prometheus Metrics
EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "--host=0.0.0.0", "gardena_smartsystem_prometheus_exporter.serve:app"]
