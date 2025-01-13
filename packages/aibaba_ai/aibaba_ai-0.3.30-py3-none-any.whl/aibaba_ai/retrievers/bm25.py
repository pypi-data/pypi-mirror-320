from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.retrievers import BM25Retriever
    from aiagentsforce_community.retrievers.bm25 import default_preprocessing_func

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "default_preprocessing_func": "aiagentsforce_community.retrievers.bm25",
    "BM25Retriever": "aiagentsforce_community.retrievers",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "default_preprocessing_func",
    "BM25Retriever",
]
