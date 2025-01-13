from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.retrievers import AmazonKendraRetriever
    from aiagentsforce_community.retrievers.kendra import (
        AdditionalResultAttribute,
        AdditionalResultAttributeValue,
        DocumentAttribute,
        DocumentAttributeValue,
        Highlight,
        QueryResult,
        QueryResultItem,
        ResultItem,
        RetrieveResult,
        RetrieveResultItem,
        TextWithHighLights,
        clean_excerpt,
        combined_text,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "clean_excerpt": "aiagentsforce_community.retrievers.kendra",
    "combined_text": "aiagentsforce_community.retrievers.kendra",
    "Highlight": "aiagentsforce_community.retrievers.kendra",
    "TextWithHighLights": "aiagentsforce_community.retrievers.kendra",
    "AdditionalResultAttributeValue": "aiagentsforce_community.retrievers.kendra",
    "AdditionalResultAttribute": "aiagentsforce_community.retrievers.kendra",
    "DocumentAttributeValue": "aiagentsforce_community.retrievers.kendra",
    "DocumentAttribute": "aiagentsforce_community.retrievers.kendra",
    "ResultItem": "aiagentsforce_community.retrievers.kendra",
    "QueryResultItem": "aiagentsforce_community.retrievers.kendra",
    "RetrieveResultItem": "aiagentsforce_community.retrievers.kendra",
    "QueryResult": "aiagentsforce_community.retrievers.kendra",
    "RetrieveResult": "aiagentsforce_community.retrievers.kendra",
    "AmazonKendraRetriever": "aiagentsforce_community.retrievers",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "clean_excerpt",
    "combined_text",
    "Highlight",
    "TextWithHighLights",
    "AdditionalResultAttributeValue",
    "AdditionalResultAttribute",
    "DocumentAttributeValue",
    "DocumentAttribute",
    "ResultItem",
    "QueryResultItem",
    "RetrieveResultItem",
    "QueryResult",
    "RetrieveResult",
    "AmazonKendraRetriever",
]
