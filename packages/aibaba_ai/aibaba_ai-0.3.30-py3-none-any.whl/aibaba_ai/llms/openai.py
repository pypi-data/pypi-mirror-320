from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.llms import AzureOpenAI, OpenAI, OpenAIChat
    from aiagentsforce_community.llms.openai import BaseOpenAI

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "BaseOpenAI": "aiagentsforce_community.llms.openai",
    "OpenAI": "aiagentsforce_community.llms",
    "AzureOpenAI": "aiagentsforce_community.llms",
    "OpenAIChat": "aiagentsforce_community.llms",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "BaseOpenAI",
    "OpenAI",
    "AzureOpenAI",
    "OpenAIChat",
]
