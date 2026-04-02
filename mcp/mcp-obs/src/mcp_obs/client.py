"""HTTP client for VictoriaLogs and VictoriaTraces APIs."""

from __future__ import annotations

import httpx


class ObsClient:
    """Client for querying observability backends."""

    def __init__(self, victorialogs_url: str, victoriatraces_url: str) -> None:
        self.victorialogs_url = victorialogs_url.rstrip("/")
        self.victoriatraces_url = victoriatraces_url.rstrip("/")
        self._http = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.aclose()

    async def logs_search(
        self, query: str, limit: int = 100
    ) -> list[dict]:
        """Search logs using VictoriaLogs LogsQL query."""
        url = f"{self.victorialogs_url}/select/logsql/query"
        params = {"query": query, "limit": str(limit)}
        response = await self._http.get(url, params=params)
        response.raise_for_status()
        # VictoriaLogs returns newline-delimited JSON
        lines = response.text.strip().split("\n")
        return [httpx.Response.json(type("FakeResp", (), {"text": l})()) for l in lines if l]

    async def logs_error_count(
        self, service: str | None = None, minutes: int = 60
    ) -> dict:
        """Count errors by service over a time window."""
        time_filter = f"_time:{minutes}m"
        service_filter = f'service.name:"{service}"' if service else ""
        query = f"{time_filter} {service_filter} severity:ERROR".strip()
        
        url = f"{self.victorialogs_url}/select/logsql/stats_query"
        params = {"query": query}
        try:
            response = await self._http.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception:
            # Fallback: count from search results
            results = await self.logs_search(query, limit=1000)
            return {"total_errors": len(results), "query": query}

    async def traces_list(
        self, service: str | None = None, limit: int = 10
    ) -> list[dict]:
        """List recent traces for a service."""
        url = f"{self.victoriatraces_url}/select/jaeger/api/traces"
        params = {"limit": str(limit)}
        if service:
            params["service"] = service
        response = await self._http.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])

    async def traces_get(self, trace_id: str) -> dict:
        """Get a specific trace by ID."""
        url = f"{self.victoriatraces_url}/select/jaeger/api/traces/{trace_id}"
        response = await self._http.get(url)
        response.raise_for_status()
        data = response.json()
        traces = data.get("data", [])
        return traces[0] if traces else {}
