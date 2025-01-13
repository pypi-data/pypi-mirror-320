from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.document_transformers import (
        EmbeddingsClusteringFilter,
        EmbeddingsRedundantFilter,
        get_stateful_documents,
    )
    from aiagentsforce_community.document_transformers.embeddings_redundant_filter import (
        _DocumentWithState,
        _filter_similar_embeddings,
        _get_embeddings_from_stateful_docs,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "EmbeddingsRedundantFilter": "aiagentsforce_community.document_transformers",
    "EmbeddingsClusteringFilter": "aiagentsforce_community.document_transformers",
    "_DocumentWithState": (
        "aiagentsforce_community.document_transformers.embeddings_redundant_filter"
    ),
    "get_stateful_documents": "aiagentsforce_community.document_transformers",
    "_get_embeddings_from_stateful_docs": (
        "aiagentsforce_community.document_transformers.embeddings_redundant_filter"
    ),
    "_filter_similar_embeddings": (
        "aiagentsforce_community.document_transformers.embeddings_redundant_filter"
    ),
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "EmbeddingsRedundantFilter",
    "EmbeddingsClusteringFilter",
    "_DocumentWithState",
    "get_stateful_documents",
    "_get_embeddings_from_stateful_docs",
    "_filter_similar_embeddings",
]
