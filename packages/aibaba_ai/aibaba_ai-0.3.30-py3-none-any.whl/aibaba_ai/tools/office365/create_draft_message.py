from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.tools import O365CreateDraftMessage
    from aiagentsforce_community.tools.office365.create_draft_message import (
        CreateDraftMessageSchema,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "CreateDraftMessageSchema": (
        "aiagentsforce_community.tools.office365.create_draft_message"
    ),
    "O365CreateDraftMessage": "aiagentsforce_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "CreateDraftMessageSchema",
    "O365CreateDraftMessage",
]
