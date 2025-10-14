from typing import List
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Blockchain Knowledge", port=9091)

@mcp.tool()
async def get_blockchain_knowledge(location: str) -> str:
    """Get weather for location."""
    return "It's always sunny in New York"

if __name__ == "__main__":
    mcp.run(transport="sse")