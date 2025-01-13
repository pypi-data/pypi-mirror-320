from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.document_loaders import (
        UnstructuredAPIFileIOLoader,
        UnstructuredAPIFileLoader,
        UnstructuredFileIOLoader,
        UnstructuredFileLoader,
    )
    from aiagentsforce_community.document_loaders.unstructured import (
        UnstructuredBaseLoader,
        get_elements_from_api,
        satisfies_min_unstructured_version,
        validate_unstructured_version,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "satisfies_min_unstructured_version": (
        "aiagentsforce_community.document_loaders.unstructured"
    ),
    "validate_unstructured_version": (
        "aiagentsforce_community.document_loaders.unstructured"
    ),
    "UnstructuredBaseLoader": "aiagentsforce_community.document_loaders.unstructured",
    "UnstructuredFileLoader": "aiagentsforce_community.document_loaders",
    "get_elements_from_api": "aiagentsforce_community.document_loaders.unstructured",
    "UnstructuredAPIFileLoader": "aiagentsforce_community.document_loaders",
    "UnstructuredFileIOLoader": "aiagentsforce_community.document_loaders",
    "UnstructuredAPIFileIOLoader": "aiagentsforce_community.document_loaders",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "satisfies_min_unstructured_version",
    "validate_unstructured_version",
    "UnstructuredBaseLoader",
    "UnstructuredFileLoader",
    "get_elements_from_api",
    "UnstructuredAPIFileLoader",
    "UnstructuredFileIOLoader",
    "UnstructuredAPIFileIOLoader",
]
