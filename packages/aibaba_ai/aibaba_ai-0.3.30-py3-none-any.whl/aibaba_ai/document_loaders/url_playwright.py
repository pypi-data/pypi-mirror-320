from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.document_loaders import PlaywrightURLLoader
    from aiagentsforce_community.document_loaders.url_playwright import (
        PlaywrightEvaluator,
        UnstructuredHtmlEvaluator,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "PlaywrightEvaluator": "aiagentsforce_community.document_loaders.url_playwright",
    "UnstructuredHtmlEvaluator": "aiagentsforce_community.document_loaders.url_playwright",
    "PlaywrightURLLoader": "aiagentsforce_community.document_loaders",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "PlaywrightEvaluator",
    "UnstructuredHtmlEvaluator",
    "PlaywrightURLLoader",
]
