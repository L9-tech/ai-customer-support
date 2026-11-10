FROM node:22-slim AS ui
WORKDIR /ui
RUN corepack enable && corepack prepare pnpm@11.25.0 --activate
COPY dashboard/package.json dashboard/pnpm-lock.yaml dashboard/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY dashboard/ ./
RUN pnpm run build

FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.9.8 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY app ./app
COPY knowledge_base ./knowledge_base
COPY --from=ui /ui/dist ./dashboard/dist
RUN useradd --create-home support && mkdir -p /app/data && chown -R support:support /app
USER support
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
