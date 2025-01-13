from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.adapters.openai import (
        Chat,
        ChatCompletion,
        ChatCompletionChunk,
        ChatCompletions,
        Choice,
        ChoiceChunk,
        Completions,
        IndexableBaseModel,
        chat,
        convert_dict_to_message,
        convert_message_to_dict,
        convert_messages_for_finetuning,
        convert_openai_messages,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
MODULE_LOOKUP = {
    "IndexableBaseModel": "aiagentsforce_community.adapters.openai",
    "Choice": "aiagentsforce_community.adapters.openai",
    "ChatCompletions": "aiagentsforce_community.adapters.openai",
    "ChoiceChunk": "aiagentsforce_community.adapters.openai",
    "ChatCompletionChunk": "aiagentsforce_community.adapters.openai",
    "convert_dict_to_message": "aiagentsforce_community.adapters.openai",
    "convert_message_to_dict": "aiagentsforce_community.adapters.openai",
    "convert_openai_messages": "aiagentsforce_community.adapters.openai",
    "ChatCompletion": "aiagentsforce_community.adapters.openai",
    "convert_messages_for_finetuning": "aiagentsforce_community.adapters.openai",
    "Completions": "aiagentsforce_community.adapters.openai",
    "Chat": "aiagentsforce_community.adapters.openai",
    "chat": "aiagentsforce_community.adapters.openai",
}

_import_attribute = create_importer(__file__, deprecated_lookups=MODULE_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "IndexableBaseModel",
    "Choice",
    "ChatCompletions",
    "ChoiceChunk",
    "ChatCompletionChunk",
    "convert_dict_to_message",
    "convert_message_to_dict",
    "convert_openai_messages",
    "ChatCompletion",
    "convert_messages_for_finetuning",
    "Completions",
    "Chat",
    "chat",
]
