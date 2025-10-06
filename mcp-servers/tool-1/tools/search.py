import logging
from googlesearch import search
from typing import Annotated
from pydantic import Field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def google_search(
    query: Annotated[str, Field(description="Search query")]
) -> str:
        """Search Google for information"""
        try:
            logger.info(f"Searching Google for: {query}")
            
            print("Searching Google")

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
            logger.error(f"Error searching Google: {str(e)}", exc_info=True)
            import traceback
            traceback.print_exc()
            return "Error searching Google"
