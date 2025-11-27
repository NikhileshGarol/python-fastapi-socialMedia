import requests
from database import MCP_SERVER_URL

class MCPClient:
    base = MCP_SERVER_URL.rstrip("/")

    @staticmethod
    def get_resource(name: str, params: dict = None):
        url = f"{MCPClient.base}/mcp/resources/{name}"
        resp = requests.get(url, params=params or {})
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def invoke_tool(name: str, payload: dict):
        url = f"{MCPClient.base}/mcp/tools/{name}/invoke"
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()
