from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.vectorstores import ElasticsearchStore
    from aiagentsforce_community.vectorstores.elasticsearch import (
        ApproxRetrievalStrategy,
        BaseRetrievalStrategy,
        ExactRetrievalStrategy,
        SparseRetrievalStrategy,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "BaseRetrievalStrategy": "aiagentsforce_community.vectorstores.elasticsearch",
    "ApproxRetrievalStrategy": "aiagentsforce_community.vectorstores.elasticsearch",
    "ExactRetrievalStrategy": "aiagentsforce_community.vectorstores.elasticsearch",
    "SparseRetrievalStrategy": "aiagentsforce_community.vectorstores.elasticsearch",
    "ElasticsearchStore": "aiagentsforce_community.vectorstores",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "BaseRetrievalStrategy",
    "ApproxRetrievalStrategy",
    "ExactRetrievalStrategy",
    "SparseRetrievalStrategy",
    "ElasticsearchStore",
]
