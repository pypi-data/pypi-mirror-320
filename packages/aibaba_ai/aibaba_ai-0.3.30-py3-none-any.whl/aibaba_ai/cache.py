from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.cache import (
        AstraDBCache,
        AstraDBSemanticCache,
        AzureCosmosDBSemanticCache,
        CassandraCache,
        CassandraSemanticCache,
        FullLLMCache,
        FullMd5LLMCache,
        GPTCache,
        InMemoryCache,
        MomentoCache,
        RedisCache,
        RedisSemanticCache,
        SQLAlchemyCache,
        SQLAlchemyMd5Cache,
        SQLiteCache,
        UpstashRedisCache,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "FullLLMCache": "aiagentsforce_community.cache",
    "SQLAlchemyCache": "aiagentsforce_community.cache",
    "SQLiteCache": "aiagentsforce_community.cache",
    "UpstashRedisCache": "aiagentsforce_community.cache",
    "RedisCache": "aiagentsforce_community.cache",
    "RedisSemanticCache": "aiagentsforce_community.cache",
    "GPTCache": "aiagentsforce_community.cache",
    "MomentoCache": "aiagentsforce_community.cache",
    "InMemoryCache": "aiagentsforce_community.cache",
    "CassandraCache": "aiagentsforce_community.cache",
    "CassandraSemanticCache": "aiagentsforce_community.cache",
    "FullMd5LLMCache": "aiagentsforce_community.cache",
    "SQLAlchemyMd5Cache": "aiagentsforce_community.cache",
    "AstraDBCache": "aiagentsforce_community.cache",
    "AstraDBSemanticCache": "aiagentsforce_community.cache",
    "AzureCosmosDBSemanticCache": "aiagentsforce_community.cache",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "FullLLMCache",
    "SQLAlchemyCache",
    "SQLiteCache",
    "UpstashRedisCache",
    "RedisCache",
    "RedisSemanticCache",
    "GPTCache",
    "MomentoCache",
    "InMemoryCache",
    "CassandraCache",
    "CassandraSemanticCache",
    "FullMd5LLMCache",
    "SQLAlchemyMd5Cache",
    "AstraDBCache",
    "AstraDBSemanticCache",
    "AzureCosmosDBSemanticCache",
]
