"""File Management Tools."""

from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.tools import (
        CopyFileTool,
        DeleteFileTool,
        FileSearchTool,
        ListDirectoryTool,
        MoveFileTool,
        ReadFileTool,
        WriteFileTool,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "CopyFileTool": "aiagentsforce_community.tools",
    "DeleteFileTool": "aiagentsforce_community.tools",
    "FileSearchTool": "aiagentsforce_community.tools",
    "MoveFileTool": "aiagentsforce_community.tools",
    "ReadFileTool": "aiagentsforce_community.tools",
    "WriteFileTool": "aiagentsforce_community.tools",
    "ListDirectoryTool": "aiagentsforce_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "CopyFileTool",
    "DeleteFileTool",
    "FileSearchTool",
    "MoveFileTool",
    "ReadFileTool",
    "WriteFileTool",
    "ListDirectoryTool",
]
