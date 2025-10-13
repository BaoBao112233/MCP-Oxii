"""
Test client for OXII MCP Server
"""
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

async def main():
    """Test the OXII MCP Server tools"""
    print("Testing OXII MCP Server...")
    
    async with MultiServerMCPClient(
        {
            "oxii-server": {
                "url": "http://localhost:9031/sse",
                "transport": "sse",
            }
        }
    ) as client:
        print("Connected to OXII server!")
        
        # List all available tools
        tools = client.get_tools()
        print(f"\nAvailable tools ({len(tools)}):")
        for i, tool in enumerate(tools, 1):
            print(f"{i}. {tool.name}: {tool.description}")
            
        print("\nOXII MCP Server is working correctly!")

if __name__ == "__main__":
    asyncio.run(main())