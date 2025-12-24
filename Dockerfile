# Stage 1 
FROM python:3.12-alpine AS python-base

ENV PYTHONBUFFERED=1
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

# Stage 2
FROM python-base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Stage 3
FROM python-base AS dev

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

ENTRYPOINT ["python", "main.py"]

# Stage 4
FROM python-base AS prod

RUN addgroup -S appuser && adduser -S appuser -G appuser -h /app

USER appuser

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
COPY main.py ./main.py
COPY config/ ./config/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

ENTRYPOINT ["python", "main.py"]
