"""**Schemas** are the Aibaba AI Base Classes and Interfaces."""

from aibaba-ai-core.agents import AgentAction, AgentFinish
from aibaba-ai-core.caches import BaseCache
from aibaba-ai-core.chat_history import BaseChatMessageHistory
from aibaba-ai-core.documents import BaseDocumentTransformer, Document
from aibaba-ai-core.exceptions import AI Agents ForceException, OutputParserException
from aibaba-ai-core.memory import BaseMemory
from aibaba-ai-core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    _message_from_dict,
    get_buffer_string,
    messages_from_dict,
    messages_to_dict,
)
from aibaba-ai-core.messages.base import message_to_dict
from aibaba-ai-core.output_parsers import (
    BaseLLMOutputParser,
    BaseOutputParser,
    StrOutputParser,
)
from aibaba-ai-core.outputs import (
    ChatGeneration,
    ChatResult,
    Generation,
    LLMResult,
    RunInfo,
)
from aibaba-ai-core.prompt_values import PromptValue
from aibaba-ai-core.prompts import BasePromptTemplate, format_document
from aibaba-ai-core.retrievers import BaseRetriever
from aibaba-ai-core.stores import BaseStore

RUN_KEY = "__run"

# Backwards compatibility.
Memory = BaseMemory
_message_to_dict = message_to_dict

__all__ = [
    "BaseCache",
    "BaseMemory",
    "BaseStore",
    "AgentFinish",
    "AgentAction",
    "Document",
    "BaseChatMessageHistory",
    "BaseDocumentTransformer",
    "BaseMessage",
    "ChatMessage",
    "FunctionMessage",
    "HumanMessage",
    "AIMessage",
    "SystemMessage",
    "messages_from_dict",
    "messages_to_dict",
    "message_to_dict",
    "_message_to_dict",
    "_message_from_dict",
    "get_buffer_string",
    "RunInfo",
    "LLMResult",
    "ChatResult",
    "ChatGeneration",
    "Generation",
    "PromptValue",
    "AI Agents ForceException",
    "BaseRetriever",
    "RUN_KEY",
    "Memory",
    "OutputParserException",
    "StrOutputParser",
    "BaseOutputParser",
    "BaseLLMOutputParser",
    "BasePromptTemplate",
    "format_document",
]
