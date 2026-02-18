from langchain_core.tools import tool
from src.config import config
from tavily import TavilyClient

client = TavilyClient(api_key=config.TAVILY_API_KEY)


@tool
def web_search(query: str) -> str:
    """Search the web for current information about a topic.
    Use this to find recent articles, documentation, and technical resources.
    Returns titles, URLs, and content summaries."""
    results = client.search(query=query, max_results=5)
    formatted = []
    for r in results["results"]:
        formatted.append(
            f"Title: {r['title']}\n"
            f"Source_Url: {r['url']}\n"
            f"Content: {r['content']}"
        )
    return "\n\n---\n\n".join(formatted)
