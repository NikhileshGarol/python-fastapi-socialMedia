"""
MCP server configuration and tool registry.
"""
from typing import Any, Callable, Dict, List, TypedDict

from mcp_server.tools.sentiment_tool import analyze_sentiment
from mcp_server.tools.summarize_tool import summarize_text
from mcp_server.tools.content_generator_tool import generate_content
from mcp_server.tools.chat_tool import chat_reply


class ToolDefinition(TypedDict):
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], Dict[str, Any]]


TOOL_REGISTRY: Dict[str, ToolDefinition] = {
    "summarize": ToolDefinition(
        name="summarize",
        description="Summarizes text content using the Perplexity Sonar model.",
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to summarize."},
                "context": {
                    "type": "object",
                    "description": "Optional metadata/context passed to the tool.",
                },
            },
            "required": ["text"],
        },
        handler=lambda payload: {
            "summary": summarize_text(payload.get("text", "")),
        },
    ),
    "sentiment": ToolDefinition(
        name="sentiment",
        description="Classifies sentiment of the provided text.",
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to analyze."}
            },
            "required": ["text"],
        },
        handler=lambda payload: analyze_sentiment(payload.get("text", "")),
    ),
    "content_generation": ToolDefinition(
        name="content_generation",
        description="Generates content based on the provided context.",
        input_schema={
            "type": "object",
            "properties": {
                "context": {
                    "type": "string",
                    "description": "Context to generate context from."
                }
            },
            "required": ["context"],
        },
        handler=lambda payload: generate_content(payload.get("context", "")),
    ),
    "chat": ToolDefinition(
        name="chat",
        description="General chat assistant for the app.",
        input_schema={
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "User message to send to the assistant.",
                }
            },
            "required": ["message"],
        },
        handler=lambda payload: chat_reply(payload.get("message", "")),
    ),
}


def list_tools() -> List[Dict[str, Any]]:
    """Return metadata for all registered tools (without handlers)."""
    return [
        {
            "name": tool["name"],
            "description": tool["description"],
            "inputSchema": tool["input_schema"],
        }
        for tool in TOOL_REGISTRY.values()
    ]


def get_tool_handler(name: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Fetch the callable that executes the specified tool."""
    tool = TOOL_REGISTRY.get(name)
    if not tool:
        raise ValueError(f"Tool '{name}' not found")
    return tool["handler"]
