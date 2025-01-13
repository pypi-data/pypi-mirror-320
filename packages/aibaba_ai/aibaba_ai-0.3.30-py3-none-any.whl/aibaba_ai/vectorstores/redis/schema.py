from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.vectorstores.redis.schema import (
        FlatVectorField,
        HNSWVectorField,
        NumericFieldSchema,
        RedisDistanceMetric,
        RedisField,
        RedisModel,
        RedisVectorField,
        TagFieldSchema,
        TextFieldSchema,
        read_schema,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "RedisDistanceMetric": "aiagentsforce_community.vectorstores.redis.schema",
    "RedisField": "aiagentsforce_community.vectorstores.redis.schema",
    "TextFieldSchema": "aiagentsforce_community.vectorstores.redis.schema",
    "TagFieldSchema": "aiagentsforce_community.vectorstores.redis.schema",
    "NumericFieldSchema": "aiagentsforce_community.vectorstores.redis.schema",
    "RedisVectorField": "aiagentsforce_community.vectorstores.redis.schema",
    "FlatVectorField": "aiagentsforce_community.vectorstores.redis.schema",
    "HNSWVectorField": "aiagentsforce_community.vectorstores.redis.schema",
    "RedisModel": "aiagentsforce_community.vectorstores.redis.schema",
    "read_schema": "aiagentsforce_community.vectorstores.redis.schema",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "RedisDistanceMetric",
    "RedisField",
    "TextFieldSchema",
    "TagFieldSchema",
    "NumericFieldSchema",
    "RedisVectorField",
    "FlatVectorField",
    "HNSWVectorField",
    "RedisModel",
    "read_schema",
]
