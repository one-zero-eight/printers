# Based on https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

# pycups is sources-only so we have to build it
RUN apt-get update && apt-get install -y --no-install-recommends libcups2-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Then, use a final image without uv
FROM python:3.13-slim-bookworm
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.
RUN groupadd -g 1500 app && \
    useradd -m -u 1500 -g app app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcups2 cups-client && rm -rf /var/lib/apt/lists/*

ENV PATH="/app/.venv/bin:$PATH"
# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app
USER app
WORKDIR /app

EXPOSE 8000
CMD [ "gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "4", "src.api.app:app" ]
