"""**Graphs** provide a natural language interface to graph databases."""

from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.graphs import (
        ArangoGraph,
        FalkorDBGraph,
        HugeGraph,
        KuzuGraph,
        MemgraphGraph,
        NebulaGraph,
        Neo4jGraph,
        NeptuneGraph,
        NetworkxEntityGraph,
        RdfGraph,
    )


# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "MemgraphGraph": "aiagentsforce_community.graphs",
    "NetworkxEntityGraph": "aiagentsforce_community.graphs",
    "Neo4jGraph": "aiagentsforce_community.graphs",
    "NebulaGraph": "aiagentsforce_community.graphs",
    "NeptuneGraph": "aiagentsforce_community.graphs",
    "KuzuGraph": "aiagentsforce_community.graphs",
    "HugeGraph": "aiagentsforce_community.graphs",
    "RdfGraph": "aiagentsforce_community.graphs",
    "ArangoGraph": "aiagentsforce_community.graphs",
    "FalkorDBGraph": "aiagentsforce_community.graphs",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "MemgraphGraph",
    "NetworkxEntityGraph",
    "Neo4jGraph",
    "NebulaGraph",
    "NeptuneGraph",
    "KuzuGraph",
    "HugeGraph",
    "RdfGraph",
    "ArangoGraph",
    "FalkorDBGraph",
]
