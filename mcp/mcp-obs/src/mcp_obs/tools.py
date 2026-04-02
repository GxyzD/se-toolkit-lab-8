"""Tool schemas, handlers, and registry for the observability MCP server."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_obs.client import ObsClient


class LogSearchQuery(BaseModel):
    query: str = Field(
        description="LogsQL query string, e.g. '_time:10m service.name:\"LMS\" severity:ERROR'"
    )
    limit: int = Field(
        default=100, ge=1, le=1000, description="Max results to return (default 100)"
    )


class LogErrorCountQuery(BaseModel):
    service: str | None = Field(
        default=None, description="Service name to filter (optional)"
    )
    minutes: int = Field(
        default=60, ge=1, le=1440, description="Time window in minutes (default 60)"
    )


class TracesListQuery(BaseModel):
    service: str | None = Field(
        default=None, description="Service name to filter (optional)"
    )
    limit: int = Field(
        default=10, ge=1, le=100, description="Max traces to return (default 10)"
    )


class TraceGetQuery(BaseModel):
    trace_id: str = Field(description="Trace ID to fetch")


ToolPayload = BaseModel
ToolHandler = Callable[[ObsClient, BaseModel], Awaitable[ToolPayload]]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    model: type[BaseModel]
    handler: ToolHandler

    def as_tool(self) -> Tool:
        schema = self.model.model_json_schema()
        schema.pop("$defs", None)
        schema.pop("title", None)
        return Tool(name=self.name, description=self.description, inputSchema=schema)


async def _logs_search(client: ObsClient, args: BaseModel) -> ToolPayload:
    query = args if isinstance(args, LogSearchQuery) else LogSearchQuery.model_validate(
        args
    )
    results = await client.logs_search(query.query, query.limit)
    return {"results": results, "count": len(results)}


async def _logs_error_count(client: ObsClient, args: BaseModel) -> ToolPayload:
    query = (
        args if isinstance(args, LogErrorCountQuery) else LogErrorCountQuery.model_validate(args)
    )
    result = await client.logs_error_count(query.service, query.minutes)
    return result


async def _traces_list(client: ObsClient, args: BaseModel) -> ToolPayload:
    query = (
        args if isinstance(args, TracesListQuery) else TracesListQuery.model_validate(args)
    )
    traces = await client.traces_list(query.service, query.limit)
    return {"traces": traces, "count": len(traces)}


async def _traces_get(client: ObsClient, args: BaseModel) -> ToolPayload:
    query = (
        args if isinstance(args, TraceGetQuery) else TraceGetQuery.model_validate(args)
    )
    trace = await client.traces_get(query.trace_id)
    return trace


TOOL_SPECS = (
    ToolSpec(
        "logs_search",
        "Search logs using VictoriaLogs LogsQL query. Use filters like _time:10m, service.name:\"...\", severity:ERROR.",
        LogSearchQuery,
        _logs_search,
    ),
    ToolSpec(
        "logs_error_count",
        "Count errors by service over a time window. Returns total error count.",
        LogErrorCountQuery,
        _logs_error_count,
    ),
    ToolSpec(
        "traces_list",
        "List recent traces for a service. Returns trace IDs and span counts.",
        TracesListQuery,
        _traces_list,
    ),
    ToolSpec(
        "traces_get",
        "Get a specific trace by ID. Returns full trace with all spans.",
        TraceGetQuery,
        _traces_get,
    ),
)
TOOLS_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}
