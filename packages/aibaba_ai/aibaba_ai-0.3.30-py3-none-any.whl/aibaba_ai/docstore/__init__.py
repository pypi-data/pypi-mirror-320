"""**Docstores** are classes to store and load Documents.

The **Docstore** is a simplified version of the Document Loader.

**Class hierarchy:**

.. code-block::

    Docstore --> <name> # Examples: InMemoryDocstore, Wikipedia

**Main helpers:**

.. code-block::

    Document, AddableMixin
"""

from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.docstore.arbitrary_fn import DocstoreFn
    from aiagentsforce_community.docstore.in_memory import InMemoryDocstore
    from aiagentsforce_community.docstore.wikipedia import Wikipedia

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "DocstoreFn": "aiagentsforce_community.docstore.arbitrary_fn",
    "InMemoryDocstore": "aiagentsforce_community.docstore.in_memory",
    "Wikipedia": "aiagentsforce_community.docstore.wikipedia",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "DocstoreFn",
    "InMemoryDocstore",
    "Wikipedia",
]
