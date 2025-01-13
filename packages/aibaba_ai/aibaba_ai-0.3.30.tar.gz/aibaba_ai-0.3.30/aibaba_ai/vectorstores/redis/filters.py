from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.vectorstores.redis.filters import (
        RedisFilter,
        RedisFilterExpression,
        RedisFilterField,
        RedisFilterOperator,
        RedisNum,
        RedisTag,
        RedisText,
        check_operator_misuse,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "RedisFilterOperator": "aiagentsforce_community.vectorstores.redis.filters",
    "RedisFilter": "aiagentsforce_community.vectorstores.redis.filters",
    "RedisFilterField": "aiagentsforce_community.vectorstores.redis.filters",
    "check_operator_misuse": "aiagentsforce_community.vectorstores.redis.filters",
    "RedisTag": "aiagentsforce_community.vectorstores.redis.filters",
    "RedisNum": "aiagentsforce_community.vectorstores.redis.filters",
    "RedisText": "aiagentsforce_community.vectorstores.redis.filters",
    "RedisFilterExpression": "aiagentsforce_community.vectorstores.redis.filters",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "RedisFilterOperator",
    "RedisFilter",
    "RedisFilterField",
    "check_operator_misuse",
    "RedisTag",
    "RedisNum",
    "RedisText",
    "RedisFilterExpression",
]
