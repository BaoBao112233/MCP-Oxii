import traceback
from typing import Annotated

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from tools.degenlimo import get_kols_token
from tools.dexscreener import (
    get_bubble_map_token,
    get_bundle_token,
    get_contract_address_from_pairID,
    get_contract_address_from_ticker,
    get_info_token,
)
from tools.search import search
from tools.similar_token import get_similar_token_v2
from tools.twitter.twitter import search as twitter_search


def refine_twitter_search(
    contract_address: Annotated[
        str, Field(default="", description="A blockchain contract address")
    ],
):
    """Search Twitter for tweets about a specific topic"""
    try:
        print(f"Searching Twitter for: {contract_address}")
        tweets, _ = twitter_search(
            raw_query=contract_address,
            count=20,
            product="Top",
            query_source="",
            cursor=None,
        )
        print("Get Tweets")

        if not tweets:
            return "No tweets found."

        results = []
        for i, t in enumerate(tweets):
            cleaned_content = t.content.replace("\n", " ").replace("\r", " ")
            results.append(
                f"Post {i + 1}:\n{cleaned_content}\n(Tweet ID: {t.tweet_id})"
            )

        result = "\n".join(results)

        if len(results) == 0:
            print("No tweets found.")
            return "No tweets found."

        result = f"List of tweets:\n{result}"
        print("Tim tweets found.")
        print(result)
        return result
    except Exception as e:
        print(f"Error searching Twitter: {str(e)}")
        traceback.print_exc()
        return "Error searching Twitter"


def refine_google_search(
    query: Annotated[
        str,
        Field(description="Search query, type what you want to search here",),
    ],
) -> str:
    """Search Google for more information."""
    try:
        print(f"Searching Google for: {query}")

        results = search(query, advanced=True, num_results=5)
        formatted_results = []

        for r in results:
            formatted_results.append(f"{r.title} - {r.description}")

        if not formatted_results:
            print("Google search: No results found.")
            return "No results found."
        print("Google search: results found.")
        return "\n".join(formatted_results)
    except Exception as e:
        print(f"Error searching Google: {str(e)}")
        import traceback

        traceback.print_exc()
        return "Error searching Google"


def main():
    print("Hello from tool-2!")
    mcp = FastMCP("blockchain_knowledge", port=9021)
    load_dotenv()
    tools = [
        get_contract_address_from_ticker,
        get_contract_address_from_pairID,
        get_info_token,
        get_bundle_token,
        get_bubble_map_token,
        get_similar_token_v2,
        get_kols_token,
        refine_google_search,
        refine_twitter_search,
    ]

    for tool in tools:
        mcp.add_tool(tool)

    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
