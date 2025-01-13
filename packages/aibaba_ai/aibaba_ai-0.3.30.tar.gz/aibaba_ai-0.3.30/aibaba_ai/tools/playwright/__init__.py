"""Browser tools and toolkit."""

from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.tools import (
        ClickTool,
        CurrentWebPageTool,
        ExtractHyperlinksTool,
        ExtractTextTool,
        GetElementsTool,
        NavigateBackTool,
        NavigateTool,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "NavigateTool": "aiagentsforce_community.tools",
    "NavigateBackTool": "aiagentsforce_community.tools",
    "ExtractTextTool": "aiagentsforce_community.tools",
    "ExtractHyperlinksTool": "aiagentsforce_community.tools",
    "GetElementsTool": "aiagentsforce_community.tools",
    "ClickTool": "aiagentsforce_community.tools",
    "CurrentWebPageTool": "aiagentsforce_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "NavigateTool",
    "NavigateBackTool",
    "ExtractTextTool",
    "ExtractHyperlinksTool",
    "GetElementsTool",
    "ClickTool",
    "CurrentWebPageTool",
]
