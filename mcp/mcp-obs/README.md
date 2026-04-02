# mcp-obs

MCP server for querying VictoriaLogs and VictoriaTraces observability backends.

## Tools

- `logs_search` — Search logs using VictoriaLogs LogsQL query
- `logs_error_count` — Count errors by service over a time window
- `traces_list` — List recent traces for a service
- `traces_get` — Get a specific trace by ID

## Usage

```bash
python -m mcp_obs
```

## Environment Variables

- `NANOBOT_VICTORIALOGS_URL` — VictoriaLogs base URL (default: `http://localhost:9428`)
- `NANOBOT_VICTORIATRACES_URL` — VictoriaTraces base URL (default: `http://localhost:10428`)
