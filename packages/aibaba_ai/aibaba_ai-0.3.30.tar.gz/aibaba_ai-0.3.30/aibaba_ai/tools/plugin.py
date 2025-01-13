from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.tools import AIPluginTool
    from aiagentsforce_community.tools.plugin import AIPlugin, AIPluginToolSchema, ApiConfig

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "ApiConfig": "aiagentsforce_community.tools.plugin",
    "AIPlugin": "aiagentsforce_community.tools.plugin",
    "AIPluginToolSchema": "aiagentsforce_community.tools.plugin",
    "AIPluginTool": "aiagentsforce_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "ApiConfig",
    "AIPlugin",
    "AIPluginToolSchema",
    "AIPluginTool",
]
