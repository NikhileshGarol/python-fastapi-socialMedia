# chat_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.mcp_client import MCPClient, MCPClientError

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat_ai(request: ChatRequest):
    """
    Chat endpoint that delegates to the MCP `chat` tool.
    """
    try:
        result = MCPClient.invoke_tool("chat", {"message": request.message})
        # MCP chat tool returns {"reply": ...}
        return result
    except MCPClientError as exc:
        raise HTTPException(status_code=exc.status_code or 502, detail=str(exc))
