from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from mcp_server.config import get_tool_handler, list_tools

router = APIRouter()


@router.get("")
def list_available_tools():
    """
    Standard MCP discovery endpoint.
    """
    return {"tools": list_tools()}


@router.post("/{tool_name}/invoke")
def invoke_tool(tool_name: str, payload: Dict[str, Any]):
    """
    Invoke a registered MCP tool by name.
    """
    try:
        handler = get_tool_handler(tool_name)
    except ValueError:
        tool_names = ", ".join(tool["name"] for tool in list_tools())
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found. Available tools: {tool_names}",
        )

    try:
        return handler(payload or {})
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error invoking tool '{tool_name}': {exc}",
        )