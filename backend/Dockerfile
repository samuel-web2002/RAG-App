# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build
COPY pyproject.toml ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir build \
    && pip wheel --no-cache-dir --wheel-dir=/build/wheels .


# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Security: non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Install compiled wheels
COPY --from=builder /build/wheels /tmp/wheels
RUN pip install --no-cache-dir --no-index --find-links=/tmp/wheels rag-chatbot-backend \
    && rm -rf /tmp/wheels

# Copy application code
COPY app/ ./app/

# Chroma persist dir
RUN mkdir -p /data/chroma_db && chown appuser:appgroup /data/chroma_db

USER appuser

ENV CHROMA_PERSIST_DIR=/data/chroma_db
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
