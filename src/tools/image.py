from langchain_mcp_adapters.client import MultiServerMCPClient
from src.config import config

MCP_CONFIG = {
    "excalidraw": {
        "transport": "stdio",
        "command": "node",
        "args": [config.EXCALIDRAW_PATH],
        "env": {"EXPRESS_SERVER_URL": config.EXCALIDRAW_SERVER_URL},
    }
}

_client: MultiServerMCPClient | None = None
_tools: list = []


async def get_excalidraw_tools():
    global _client, _tools
    if not _tools:
        _client = MultiServerMCPClient(MCP_CONFIG)
        _tools = await _client.get_tools()
    return _tools


def get_tool_by_name(tools, name: str):
    return next(t for t in tools if t.name == name)
