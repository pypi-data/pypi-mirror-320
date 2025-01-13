# Backwards compatibility.
from aibaba-ai-core.language_models import BaseLanguageModel
from aibaba-ai-core.language_models.llms import (
    LLM,
    BaseLLM,
)

__all__ = [
    "BaseLanguageModel",
    "BaseLLM",
    "LLM",
]
