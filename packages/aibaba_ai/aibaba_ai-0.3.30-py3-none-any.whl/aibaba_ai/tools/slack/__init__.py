"""Slack tools."""

from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.tools import (
        SlackGetChannel,
        SlackGetMessage,
        SlackScheduleMessage,
        SlackSendMessage,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "SlackGetChannel": "aiagentsforce_community.tools",
    "SlackGetMessage": "aiagentsforce_community.tools",
    "SlackScheduleMessage": "aiagentsforce_community.tools",
    "SlackSendMessage": "aiagentsforce_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "SlackGetChannel",
    "SlackGetMessage",
    "SlackScheduleMessage",
    "SlackSendMessage",
]
