#!/bin/bash
set -e

# Copy builtin workspace to actual workspace (for tmpfs mounts)
if [ -d "/app/nanobot/workspace.builtin" ] && [ -d "/app/nanobot/workspace" ]; then
    # Copy files preserving permissions but allowing overwrites
    cp -rf /app/nanobot/workspace.builtin/. /app/nanobot/workspace/ || true
    # Ensure appuser owns the workspace
    chown -R appuser:appgroup /app/nanobot/workspace 2>/dev/null || true
fi

# Drop privileges and run the entrypoint
exec gosu appuser:appgroup python /app/nanobot/entrypoint.py
