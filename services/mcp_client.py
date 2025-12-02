import os
from typing import Any, Dict, List, Optional

import httpx


class MCPClientError(RuntimeError):
    """Raised when the MCP server cannot fulfill a request."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class MCPClient:
    """
    Minimal HTTP client for the MCP server with shared connection pooling.
    """

    _client: Optional[httpx.Client] = None
    _base_url = os.getenv("MCP_SERVER_URL", "http://localhost:9000").rstrip("/")
    _timeout = float(os.getenv("MCP_HTTP_TIMEOUT", "10"))

    @classmethod
    def _get_client(cls) -> httpx.Client:
        if cls._client is None:
            cls._client = httpx.Client(timeout=cls._timeout)
        return cls._client

    @classmethod
    def _url(cls, path: str) -> str:
        return f"{cls._base_url}{path}"

    @classmethod
    def list_tools(cls) -> List[Dict[str, Any]]:
        try:
            resp = cls._get_client().get(cls._url("/mcp/tools"))
            resp.raise_for_status()
            data = resp.json()
            return data.get("tools", []) if isinstance(data, dict) else data
        except httpx.HTTPStatusError as exc:
            raise MCPClientError(
                f"MCP tools listing failed with {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.RequestError as exc:
            raise MCPClientError(f"MCP tools listing request failed: {exc}") from exc

    @classmethod
    def get_resource(cls, name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            resp = cls._get_client().get(
                cls._url(f"/mcp/resources/{name}"),
                params=params or {},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            raise MCPClientError(
                f"MCP resource '{name}' failed with {exc.response.status_code}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.RequestError as exc:
            raise MCPClientError(f"MCP resource '{name}' request failed: {exc}") from exc

    @classmethod
    def invoke_tool(cls, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resp = cls._get_client().post(
                cls._url(f"/mcp/tools/{name}/invoke"),
                json=payload or {},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            raise MCPClientError(
                f"MCP tool '{name}' failed with {exc.response.status_code}: {exc.response.text}",
                status_code=exc.response.status_code,
            ) from exc
        except httpx.RequestError as exc:
            raise MCPClientError(f"MCP tool '{name}' request failed: {exc}") from exc


def reset_mcp_client() -> None:
    """Dispose shared httpx client (useful for tests)."""
    if MCPClient._client:
        MCPClient._client.close()
        MCPClient._client = None
