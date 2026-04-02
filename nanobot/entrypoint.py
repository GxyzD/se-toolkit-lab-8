#!/usr/bin/env python3
"""
Entrypoint for nanobot gateway in Docker.

Reads config.json, injects environment variables for:
- LLM API key and base URL
- Gateway host/port
- MCP server env vars (backend URL, API key, webchat settings)

Writes config.resolved.json and execs into `nanobot gateway`.
"""

import json
import os
import sys


def main():
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")
    resolved_path = "/tmp/config.resolved.json"  # Write to /tmp to avoid permission issues
    workspace_dir = os.path.join(script_dir, "workspace")

    # Read base config
    with open(config_path, "r") as f:
        config = json.load(f)

    # Inject LLM provider settings from env vars
    llm_api_key = os.environ.get("LLM_API_KEY")
    llm_api_base_url = os.environ.get("LLM_API_BASE_URL")
    llm_api_model = os.environ.get("LLM_API_MODEL")

    if llm_api_key:
        config.setdefault("providers", {}).setdefault("custom", {})["apiKey"] = llm_api_key
    if llm_api_base_url:
        config.setdefault("providers", {}).setdefault("custom", {})["apiBase"] = llm_api_base_url
    if llm_api_model:
        config.setdefault("agents", {}).setdefault("defaults", {})["model"] = llm_api_model

    # Inject gateway settings
    gateway_host = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS")
    gateway_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT")
    if gateway_host:
        config.setdefault("gateway", {})["host"] = gateway_host
    if gateway_port:
        config.setdefault("gateway", {})["port"] = int(gateway_port)

    # Inject webchat channel settings if enabled
    webchat_host = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_ADDRESS")
    webchat_port = os.environ.get("NANOBOT_WEBCHAT_CONTAINER_PORT")
    nanobot_access_key = os.environ.get("NANOBOT_ACCESS_KEY")

    if webchat_host or webchat_port:
        webchat_config = config.setdefault("channels", {}).setdefault("webchat", {})
        webchat_config["enabled"] = True  # Ensure channel is enabled
        webchat_config["allowFrom"] = ["*"]  # Allow connections from anywhere
        if webchat_host:
            webchat_config["host"] = webchat_host
        if webchat_port:
            webchat_config["port"] = int(webchat_port)
        if nanobot_access_key:
            webchat_config["accessKey"] = nanobot_access_key

    print(f"Webchat config: {config.get('channels', {}).get('webchat', 'NOT SET')}", file=sys.stderr)

    # Inject MCP server environment variables
    mcp_servers = config.setdefault("tools", {}).setdefault("mcpServers", {})

    # LMS MCP server
    lms_backend_url = os.environ.get("NANOBOT_LMS_BACKEND_URL")
    lms_api_key = os.environ.get("NANOBOT_LMS_API_KEY")
    if "lms" not in mcp_servers:
        mcp_servers["lms"] = {"command": "python", "args": ["-m", "mcp_lms"]}
    mcp_servers["lms"].setdefault("env", {})
    if lms_backend_url:
        mcp_servers["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = lms_backend_url
    if lms_api_key:
        mcp_servers["lms"]["env"]["NANOBOT_LMS_API_KEY"] = lms_api_key

    # Webchat MCP server (for structured UI messages)
    webchat_ui_relay_url = os.environ.get("NANOBOT_WEBCHAT_UI_RELAY_URL")
    webchat_ui_token = os.environ.get("NANOBOT_WEBCHAT_UI_TOKEN")
    if webchat_ui_relay_url or webchat_ui_token:
        if "webchat" not in mcp_servers:
            mcp_servers["webchat"] = {"command": "python", "args": ["-m", "mcp_webchat"]}
        mcp_servers["webchat"].setdefault("env", {})
        if webchat_ui_relay_url:
            mcp_servers["webchat"]["env"]["NANOBOT_WEBCHAT_UI_RELAY_URL"] = webchat_ui_relay_url
        if webchat_ui_token:
            mcp_servers["webchat"]["env"]["NANOBOT_WEBCHAT_UI_TOKEN"] = webchat_ui_token

    # Observability MCP server (for logs and traces)
    victorialogs_url = os.environ.get("NANOBOT_VICTORIALOGS_URL")
    victoriatraces_url = os.environ.get("NANOBOT_VICTORIATRACES_URL")
    if victorialogs_url or victoriatraces_url:
        if "obs" not in mcp_servers:
            mcp_servers["obs"] = {"command": "python", "args": ["-m", "mcp_obs"]}
        mcp_servers["obs"].setdefault("env", {})
        if victorialogs_url:
            mcp_servers["obs"]["env"]["NANOBOT_VICTORIALOGS_URL"] = victorialogs_url
        if victoriatraces_url:
            mcp_servers["obs"]["env"]["NANOBOT_VICTORIATRACES_URL"] = victoriatraces_url

    # Write resolved config
    with open(resolved_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Using config: {resolved_path}", file=sys.stderr)

    # Exec into nanobot gateway
    os.execvp("nanobot", ["nanobot", "gateway", "--config", resolved_path, "--workspace", workspace_dir])


if __name__ == "__main__":
    main()
