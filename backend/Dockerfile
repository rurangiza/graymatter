FROM python:3.12-slim-bookworm AS base

FROM base AS deps
RUN echo "Starting dependencies stage"
COPY --from=ghcr.io/astral-sh/uv:0.7.8 /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync

FROM deps AS runtime
RUN echo "Starting runtime stage"
COPY ./src ./src
ENV PATH=/app/.venv/bin/:$PATH
ENV PYTHONPATH=/app/src:/app/scr/graymatter/
EXPOSE 8000
CMD ["uvicorn", "graymatter.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
