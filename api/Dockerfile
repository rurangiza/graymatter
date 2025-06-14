FROM python:3.12-slim-bookworm AS base

FROM base AS deps
COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync

FROM deps AS runtime
COPY ./src ./src
ENV PATH=/app/.venv/bin/:$PATH
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
