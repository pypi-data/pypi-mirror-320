from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.tools import (
        InfoPowerBITool,
        ListPowerBITool,
        QueryPowerBITool,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "QueryPowerBITool": "aiagentsforce_community.tools",
    "InfoPowerBITool": "aiagentsforce_community.tools",
    "ListPowerBITool": "aiagentsforce_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "QueryPowerBITool",
    "InfoPowerBITool",
    "ListPowerBITool",
]
