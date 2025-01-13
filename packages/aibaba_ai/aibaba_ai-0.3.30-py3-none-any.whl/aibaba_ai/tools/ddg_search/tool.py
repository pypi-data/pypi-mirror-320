from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.tools import DuckDuckGoSearchResults, DuckDuckGoSearchRun
    from aiagentsforce_community.tools.ddg_search.tool import DDGInput, DuckDuckGoSearchTool

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "DDGInput": "aiagentsforce_community.tools.ddg_search.tool",
    "DuckDuckGoSearchRun": "aiagentsforce_community.tools",
    "DuckDuckGoSearchResults": "aiagentsforce_community.tools",
    "DuckDuckGoSearchTool": "aiagentsforce_community.tools.ddg_search.tool",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "DDGInput",
    "DuckDuckGoSearchRun",
    "DuckDuckGoSearchResults",
    "DuckDuckGoSearchTool",
]
