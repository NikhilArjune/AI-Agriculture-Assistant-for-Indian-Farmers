"""
MCP client helpers for consuming external MCP servers from within agents.
"""
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


async def call_mcp_resource(server_url: str, resource_uri: str) -> Optional[str]:
    """Fetch an MCP resource from an external server."""
    try:
        from mcp import ClientSession
        from mcp.client.sse import sse_client

        async with sse_client(server_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.read_resource(resource_uri)
                if result.contents:
                    return result.contents[0].text
    except Exception as exc:
        logger.error("MCP client error for %s: %s", resource_uri, exc)
    return None


async def call_mcp_tool(server_url: str, tool_name: str, arguments: dict[str, Any]) -> Optional[str]:
    """Call a tool on an external MCP server."""
    try:
        from mcp import ClientSession
        from mcp.client.sse import sse_client

        async with sse_client(server_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                if result.content:
                    return result.content[0].text
    except Exception as exc:
        logger.error("MCP tool call error (%s / %s): %s", server_url, tool_name, exc)
    return None
