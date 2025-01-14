
from wildcard_core.tool_registry.tools.base import BaseTool
from wildcard_core.tool_registry.tools.utils.helpers import load_actions_from_package

"""
Custom Tools are a WIP. Not functional yet.
"""

class DuckDuckGoTool(BaseTool):
    def __init__(self):
        actions = load_actions_from_package("wildcard_core.tool_registry.tools.DuckDuckGo.actions")
        super().__init__(name="DuckDuckGo", tool_id="duckduckgo", description="A tool that allows you to search the web using DuckDuckGo", actions=actions)

    