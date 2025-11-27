import os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

from mcp_server.routes import resources, tools

print("DEBUG :: PERPLEXITY_API_KEY =", os.getenv("PERPLEXITY_API_KEY"))

app = FastAPI(title="MCP Demo Server")
app.include_router(resources.router, prefix="/mcp/resources")
app.include_router(tools.router, prefix="/mcp/tools")
