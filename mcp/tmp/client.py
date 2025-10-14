from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

async def main():
    async with MultiServerMCPClient(
        {
            "blockchain-knowledge": {
                # make sure you start your weather server on port 8000
                "url": "http://localhost:9011/sse",
                "transport": "sse",
            }
        }
    ) as client:
        for tool in client.get_tools():
            print(tool)

if __name__ == "__main__":
    asyncio.run(main())
