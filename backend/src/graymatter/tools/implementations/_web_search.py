from os import getenv
from typing import Literal

from pydantic import Field
from tavily import TavilyClient

from graymatter.tools.exceptions import NoSearchResultFound, ToolError
from graymatter.tools.tool import Tool


class WebSearch(Tool):
    """Retrieve relevant web search results for a specific query and topic"""

    query: str = Field(
        description="A natural language search string that "
        "clearly describes what the user wants to know. It should be complete "
        "and specific enough for an internet search engine to return "
        "relevant results."
    )
    topic: Literal["general", "news", "finance"] = Field(
        description="The broad category that best fits the search intent."
        "Use 'general' for open-ended or uncategorized queries, 'news' for "
        "current events or headlines, and 'finance' for topics related to "
        "markets, economics, or money."
    )

    def resolve(self):
        return self._search()

    def _search(self) -> str:
        try:
            client = TavilyClient(getenv("TAVILY_API_KEY"))
            response: dict[str, any] = client.search(
                query=self.query,
                topic=self.topic,
                max_results=5,
                include_answer="basic",
                include_raw_content="markdown",
            )
            if not len(response["results"]):
                raise NoSearchResultFound(self["query"])
            base = "## WEB SEARCH RESULTS\n"
            return base + "\n\n".join(
                [
                    f"{result['title']} ({result['url']})\n---\n{result['content']}"
                    for result in response["results"]
                ]
            )
        except Exception as e:
            raise ToolError(f"Websearch tool failed. Cause: {e}")
