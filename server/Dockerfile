FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app


COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5001

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache /wheels/*

COPY . .

RUN mkdir -p /app/output && \
    addgroup --system appgroup && \
    adduser --system --group appuser && \
    chown -R appuser:0 /app && \
    chmod -R g=rwX /app


USER appuser

EXPOSE 5001

CMD ["sh", "-c", "uvicorn main:app_fastapi --host 0.0.0.0 --port ${PORT}"]