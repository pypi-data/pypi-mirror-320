from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.chat_message_histories import (
        AstraDBChatMessageHistory,
        CassandraChatMessageHistory,
        ChatMessageHistory,
        CosmosDBChatMessageHistory,
        DynamoDBChatMessageHistory,
        ElasticsearchChatMessageHistory,
        FileChatMessageHistory,
        FirestoreChatMessageHistory,
        MomentoChatMessageHistory,
        MongoDBChatMessageHistory,
        Neo4jChatMessageHistory,
        PostgresChatMessageHistory,
        RedisChatMessageHistory,
        RocksetChatMessageHistory,
        SingleStoreDBChatMessageHistory,
        SQLChatMessageHistory,
        StreamlitChatMessageHistory,
        UpstashRedisChatMessageHistory,
        XataChatMessageHistory,
        ZepChatMessageHistory,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "AstraDBChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "CassandraChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "ChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "CosmosDBChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "DynamoDBChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "ElasticsearchChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "FileChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "FirestoreChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "MomentoChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "MongoDBChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "Neo4jChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "PostgresChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "RedisChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "RocksetChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "SQLChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "SingleStoreDBChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "StreamlitChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "UpstashRedisChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "XataChatMessageHistory": "aiagentsforce_community.chat_message_histories",
    "ZepChatMessageHistory": "aiagentsforce_community.chat_message_histories",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "AstraDBChatMessageHistory",
    "CassandraChatMessageHistory",
    "ChatMessageHistory",
    "CosmosDBChatMessageHistory",
    "DynamoDBChatMessageHistory",
    "ElasticsearchChatMessageHistory",
    "FileChatMessageHistory",
    "FirestoreChatMessageHistory",
    "MomentoChatMessageHistory",
    "MongoDBChatMessageHistory",
    "Neo4jChatMessageHistory",
    "PostgresChatMessageHistory",
    "RedisChatMessageHistory",
    "RocksetChatMessageHistory",
    "SingleStoreDBChatMessageHistory",
    "SQLChatMessageHistory",
    "StreamlitChatMessageHistory",
    "UpstashRedisChatMessageHistory",
    "XataChatMessageHistory",
    "ZepChatMessageHistory",
]
