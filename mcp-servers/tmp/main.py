from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


def main():
    print("Hello from template!")
    mcp = FastMCP("blockchain_knowledge", port=9001)
    load_dotenv()

    mcp.run(transport="sse")


if __name__ == "__main__":
    main()


