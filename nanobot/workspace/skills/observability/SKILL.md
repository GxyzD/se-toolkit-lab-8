---
name: observability
description: Use observability tools to investigate errors, logs, and traces
always: true
---

# Observability Skill

You have access to MCP tools that query VictoriaLogs and VictoriaTraces for system observability.

## Available Tools

- `logs_search` — Search logs using LogsQL query (e.g., `_time:10m service.name:"LMS" severity:ERROR`)
- `logs_error_count` — Count errors by service over a time window
- `traces_list` — List recent traces for a service
- `traces_get` — Get a specific trace by ID
- `cron` — Schedule recurring jobs (for proactive health checks)

## Strategy

### When asked "What went wrong?" or "Check system health":

1. **Check for recent errors first:**
   - Call `logs_error_count(service="Learning Management Service", minutes=10)`
   - If errors exist, proceed to investigation

2. **Search for specific error logs:**
   - Call `logs_search(query="_time:10m service.name:\"Learning Management Service\" severity:ERROR", limit=10)`
   - Look for error messages and extract any `trace_id` from the results

3. **Fetch the matching trace:**
   - If you found a `trace_id`, call `traces_get(trace_id="...")`
   - Examine the span hierarchy to see where the failure occurred

4. **Summarize findings concisely:**
   - Mention the service affected
   - Quote the key error message from logs
   - Explain what the trace shows (which operation failed)
   - Don't dump raw JSON — synthesize a clear explanation
   - Cite BOTH log evidence AND trace evidence in your answer

### When asked about errors in a time window:

1. First call `logs_error_count` with the service name and time window
2. If errors exist, call `logs_search` to see the actual error messages
3. Look for `trace_id` in error logs
4. If you find a trace_id, call `traces_get` to see the full request flow

### Query patterns:

- Time filter: `_time:10m` for last 10 minutes, `_time:1h` for last hour
- Service filter: `service.name:"Learning Management Service"` or `service.name:"LMS"`
- Severity filter: `severity:ERROR` or `severity:WARNING`
- Combined: `_time:10m service.name:"Learning Management Service" severity:ERROR`

### For trace investigation:

- Use `traces_list` to find recent traces for a service
- Use `traces_get` with a specific trace_id to see span hierarchy
- Look for spans with errors or long durations

### Response style:

- Summarize findings concisely — don't dump raw JSON
- Include counts, time ranges, and key error messages
- If you found a trace, explain what went wrong in the request flow
- For "What went wrong?" provide a single coherent investigation citing both log AND trace evidence

## Examples

**User:** Any errors in the last hour?
**Agent:** Let me check for recent errors.
→ calls `logs_error_count(minutes=60)`
→ If errors found: calls `logs_search(query="_time:1h severity:ERROR", limit=10)`
**Agent:** Found 3 errors in the last hour. The most recent was a database connection failure in the LMS backend at 14:25. The error was "connection is closed" when querying the items table.

**User:** What went wrong?
**Agent:** Let me investigate the recent failure.
→ calls `logs_error_count(service="Learning Management Service", minutes=10)`
→ Found 5 errors. Calls `logs_search(query="_time:10m service.name:\"Learning Management Service\" severity:ERROR")`
→ Found error: "(sqlalchemy.dialects.postgresql.asyncpg.InterfaceError) connection is closed"
→ Extracts trace_id="abc123..." from log
→ calls `traces_get(trace_id="abc123...")`
**Agent:** The LMS backend failed because PostgreSQL was unreachable. The logs show "connection is closed" errors when querying the items table. The trace confirms this: the request started successfully, authentication passed, but the database query span failed immediately. The backend returned a 404 response, but the root cause is actually a database connection failure — PostgreSQL appears to be down.

**User:** Show me recent traces
**Agent:** → calls `traces_list(service="Learning Management Service", limit=5)`
**Agent:** Here are 5 recent traces for the LMS backend:
- Trace abc123: 4 spans, 45ms total (healthy)
- Trace def456: 3 spans, 120ms total (healthy)

**User:** Create a health check for this chat that runs every 2 minutes
**Agent:** → calls `cron({"action": "add", "schedule": "*/2 * * * *", "chat_id": "...", "prompt": "Check for LMS backend errors in the last 2 minutes..."})`
**Agent:** I've created a health check job that runs every 2 minutes. It will check for recent errors and post a summary in this chat.
