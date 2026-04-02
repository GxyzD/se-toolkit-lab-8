# Adapted from backend/Dockerfile and qwen-code-api/Dockerfile
# Also see https://docs.astral.sh/uv/guides/integration/docker/

# ---
# Stage 1: build the application in the `/app` directory.
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Disable Python downloads - use the system interpreter across both images.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy workspace root files for dependency resolution from the workspace context
COPY --from=workspace pyproject.toml uv.lock /app/

# Copy nanobot pyproject.toml
COPY pyproject.toml /app/nanobot/pyproject.toml

# Copy mcp-lms (workspace dependency)
COPY --from=workspace mcp/mcp-lms /app/mcp/mcp-lms

# Copy mcp-obs (workspace dependency)
COPY --from=workspace mcp/mcp-obs /app/mcp/mcp-obs

# Copy nanobot-websocket-channel packages (workspace dependencies)
COPY --from=workspace nanobot-websocket-channel/nanobot-channel-protocol /app/nanobot-websocket-channel/nanobot-channel-protocol
COPY --from=workspace nanobot-websocket-channel/mcp-webchat /app/nanobot-websocket-channel/mcp-webchat
COPY --from=workspace nanobot-websocket-channel/nanobot-webchat /app/nanobot-websocket-channel/nanobot-webchat

# Copy nanobot source files
COPY . /app/nanobot/

# Copy workspace to a builtin location (will be copied to tmpfs at runtime)
RUN cp -r /app/nanobot/workspace /app/nanobot/workspace.builtin

# First sync to get the base environment
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package nanobot

# Then install workspace packages into the venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install \
        /app/mcp/mcp-lms \
        /app/mcp/mcp-obs \
        /app/nanobot-websocket-channel/nanobot-channel-protocol \
        /app/nanobot-websocket-channel/mcp-webchat \
        /app/nanobot-websocket-channel/nanobot-webchat

# ---
# Stage 2: use a final image without uv
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

# Set environment variables for Python and application
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Make sure we use UTF-8 encoding
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends gosu && rm -rf /var/lib/apt/lists/*

# Accept APP_UID and APP_GID as build args (default to host user)
ARG APP_UID=1000
ARG APP_GID=1000

# Setup user with configurable UID/GID to match host user
RUN groupadd --system --gid ${APP_GID} appgroup \
    && useradd --system --gid ${APP_GID} --uid ${APP_UID} --create-home appuser

# Copy the application from the builder
COPY --from=builder --chown=appuser:appgroup /app /app

# Create writable directories for nanobot workspace
RUN mkdir -p /app/nanobot/workspace/cron /app/nanobot/workspace/memory /app/nanobot/workspace/skills \
    && chown -R appuser:appgroup /app/nanobot/workspace

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy entrypoint script
COPY entrypoint.py /app/nanobot/entrypoint.py
COPY startup.sh /app/nanobot/startup.sh
RUN chmod +x /app/nanobot/startup.sh

# Run the nanobot gateway via startup script (runs as root to setup workspace, then drops to appuser)
CMD ["/bin/bash", "-c", "/app/nanobot/startup.sh"]
