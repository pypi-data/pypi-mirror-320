from typing import Dict, Type
from wildcard_core.tool_registry.tools.base import BaseAction

"""
Custom Tools are a WIP. Not functional yet.
"""

class DuckDuckGoSearchTool():
    def __init__(self):
        pass
    
    def run(self, query: str, max_results: int = 5):
        pass
    
class DuckDuckGoSearch(BaseAction):
    def __init__(self):
        schema = {
            "query": (str, "The query to search the web with"),
            "max_results": (int, "The maximum number of results to return"),
        }
        super().__init__(
            name="DuckDuckGo Search",
            operationId="duckduckgo.search",
            schema=schema,
            description="Search the web using DuckDuckGo"
        )

    def execute(self, **kwargs):
        query = kwargs.get("query")
        max_results = kwargs.get("max_results", 5)
        
        search_tool = DuckDuckGoSearchTool()
        results = search_tool.run(query, max_results=max_results)
        return results
        
        