# ruff: noqa: E402
"""Main entrypoint into package."""

import warnings
from importlib import metadata
from typing import Any, Optional

from aibaba-ai-core._api.deprecation import surface_aiagentforce_deprecation_warnings

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)


def _warn_on_import(name: str, replacement: Optional[str] = None) -> None:
    """Warn on import of deprecated module."""
    from langchain._api.interactive_env import is_interactive_env

    if is_interactive_env():
        # No warnings for interactive environments.
        # This is done to avoid polluting the output of interactive environments
        # where users rely on auto-complete and may trigger this warning
        # even if they are not using any deprecated modules
        return

    if replacement:
        warnings.warn(
            f"Importing {name} from langchain root module is no longer supported. "
            f"Please use {replacement} instead."
        )
    else:
        warnings.warn(
            f"Importing {name} from langchain root module is no longer supported."
        )


# Surfaces Deprecation and Pending Deprecation warnings from langchain.
surface_aiagentforce_deprecation_warnings()


def __getattr__(name: str) -> Any:
    if name == "MRKLChain":
        from langchain.agents import MRKLChain

        _warn_on_import(name, replacement="langchain.agents.MRKLChain")

        return MRKLChain
    elif name == "ReActChain":
        from langchain.agents import ReActChain

        _warn_on_import(name, replacement="langchain.agents.ReActChain")

        return ReActChain
    elif name == "SelfAskWithSearchChain":
        from langchain.agents import SelfAskWithSearchChain

        _warn_on_import(name, replacement="langchain.agents.SelfAskWithSearchChain")

        return SelfAskWithSearchChain
    elif name == "ConversationChain":
        from langchain.chains import ConversationChain

        _warn_on_import(name, replacement="langchain.chains.ConversationChain")

        return ConversationChain
    elif name == "LLMBashChain":
        raise ImportError(
            "This module has been moved to langchain-experimental. "
            "For more details: "
            "https://github.com/aibaba-ai/aibaba-ai/discussions/11352."
            "To access this code, install it with `pip install langchain-experimental`."
            "`from langchain_experimental.llm_bash.base "
            "import LLMBashChain`"
        )

    elif name == "LLMChain":
        from langchain.chains import LLMChain

        _warn_on_import(name, replacement="langchain.chains.LLMChain")

        return LLMChain
    elif name == "LLMCheckerChain":
        from langchain.chains import LLMCheckerChain

        _warn_on_import(name, replacement="langchain.chains.LLMCheckerChain")

        return LLMCheckerChain
    elif name == "LLMMathChain":
        from langchain.chains import LLMMathChain

        _warn_on_import(name, replacement="langchain.chains.LLMMathChain")

        return LLMMathChain
    elif name == "QAWithSourcesChain":
        from langchain.chains import QAWithSourcesChain

        _warn_on_import(name, replacement="langchain.chains.QAWithSourcesChain")

        return QAWithSourcesChain
    elif name == "VectorDBQA":
        from langchain.chains import VectorDBQA

        _warn_on_import(name, replacement="langchain.chains.VectorDBQA")

        return VectorDBQA
    elif name == "VectorDBQAWithSourcesChain":
        from langchain.chains import VectorDBQAWithSourcesChain

        _warn_on_import(name, replacement="langchain.chains.VectorDBQAWithSourcesChain")

        return VectorDBQAWithSourcesChain
    elif name == "InMemoryDocstore":
        from aiagentsforce_community.docstore import InMemoryDocstore

        _warn_on_import(name, replacement="langchain.docstore.InMemoryDocstore")

        return InMemoryDocstore
    elif name == "Wikipedia":
        from aiagentsforce_community.docstore import Wikipedia

        _warn_on_import(name, replacement="langchain.docstore.Wikipedia")

        return Wikipedia
    elif name == "Anthropic":
        from aiagentsforce_community.llms import Anthropic

        _warn_on_import(name, replacement="aiagentsforce_community.llms.Anthropic")

        return Anthropic
    elif name == "Banana":
        from aiagentsforce_community.llms import Banana

        _warn_on_import(name, replacement="aiagentsforce_community.llms.Banana")

        return Banana
    elif name == "CerebriumAI":
        from aiagentsforce_community.llms import CerebriumAI

        _warn_on_import(name, replacement="aiagentsforce_community.llms.CerebriumAI")

        return CerebriumAI
    elif name == "Cohere":
        from aiagentsforce_community.llms import Cohere

        _warn_on_import(name, replacement="aiagentsforce_community.llms.Cohere")

        return Cohere
    elif name == "ForefrontAI":
        from aiagentsforce_community.llms import ForefrontAI

        _warn_on_import(name, replacement="aiagentsforce_community.llms.ForefrontAI")

        return ForefrontAI
    elif name == "GooseAI":
        from aiagentsforce_community.llms import GooseAI

        _warn_on_import(name, replacement="aiagentsforce_community.llms.GooseAI")

        return GooseAI
    elif name == "HuggingFaceHub":
        from aiagentsforce_community.llms import HuggingFaceHub

        _warn_on_import(name, replacement="aiagentsforce_community.llms.HuggingFaceHub")

        return HuggingFaceHub
    elif name == "HuggingFaceTextGenInference":
        from aiagentsforce_community.llms import HuggingFaceTextGenInference

        _warn_on_import(
            name, replacement="aiagentsforce_community.llms.HuggingFaceTextGenInference"
        )

        return HuggingFaceTextGenInference
    elif name == "LlamaCpp":
        from aiagentsforce_community.llms import LlamaCpp

        _warn_on_import(name, replacement="aiagentsforce_community.llms.LlamaCpp")

        return LlamaCpp
    elif name == "Modal":
        from aiagentsforce_community.llms import Modal

        _warn_on_import(name, replacement="aiagentsforce_community.llms.Modal")

        return Modal
    elif name == "OpenAI":
        from aiagentsforce_community.llms import OpenAI

        _warn_on_import(name, replacement="aiagentsforce_community.llms.OpenAI")

        return OpenAI
    elif name == "Petals":
        from aiagentsforce_community.llms import Petals

        _warn_on_import(name, replacement="aiagentsforce_community.llms.Petals")

        return Petals
    elif name == "PipelineAI":
        from aiagentsforce_community.llms import PipelineAI

        _warn_on_import(name, replacement="aiagentsforce_community.llms.PipelineAI")

        return PipelineAI
    elif name == "SagemakerEndpoint":
        from aiagentsforce_community.llms import SagemakerEndpoint

        _warn_on_import(name, replacement="aiagentsforce_community.llms.SagemakerEndpoint")

        return SagemakerEndpoint
    elif name == "StochasticAI":
        from aiagentsforce_community.llms import StochasticAI

        _warn_on_import(name, replacement="aiagentsforce_community.llms.StochasticAI")

        return StochasticAI
    elif name == "Writer":
        from aiagentsforce_community.llms import Writer

        _warn_on_import(name, replacement="aiagentsforce_community.llms.Writer")

        return Writer
    elif name == "HuggingFacePipeline":
        from aiagentsforce_community.llms.huggingface_pipeline import HuggingFacePipeline

        _warn_on_import(
            name,
            replacement="aiagentsforce_community.llms.huggingface_pipeline.HuggingFacePipeline",
        )

        return HuggingFacePipeline
    elif name == "FewShotPromptTemplate":
        from aibaba-ai-core.prompts import FewShotPromptTemplate

        _warn_on_import(
            name, replacement="aibaba-ai-core.prompts.FewShotPromptTemplate"
        )

        return FewShotPromptTemplate
    elif name == "Prompt":
        from aibaba-ai-core.prompts import PromptTemplate

        _warn_on_import(name, replacement="aibaba-ai-core.prompts.PromptTemplate")

        # it's renamed as prompt template anyways
        # this is just for backwards compat
        return PromptTemplate
    elif name == "PromptTemplate":
        from aibaba-ai-core.prompts import PromptTemplate

        _warn_on_import(name, replacement="aibaba-ai-core.prompts.PromptTemplate")

        return PromptTemplate
    elif name == "BasePromptTemplate":
        from aibaba-ai-core.prompts import BasePromptTemplate

        _warn_on_import(name, replacement="aibaba-ai-core.prompts.BasePromptTemplate")

        return BasePromptTemplate
    elif name == "ArxivAPIWrapper":
        from aiagentsforce_community.utilities import ArxivAPIWrapper

        _warn_on_import(
            name, replacement="aiagentsforce_community.utilities.ArxivAPIWrapper"
        )

        return ArxivAPIWrapper
    elif name == "GoldenQueryAPIWrapper":
        from aiagentsforce_community.utilities import GoldenQueryAPIWrapper

        _warn_on_import(
            name, replacement="aiagentsforce_community.utilities.GoldenQueryAPIWrapper"
        )

        return GoldenQueryAPIWrapper
    elif name == "GoogleSearchAPIWrapper":
        from aiagentsforce_community.utilities import GoogleSearchAPIWrapper

        _warn_on_import(
            name, replacement="aiagentsforce_community.utilities.GoogleSearchAPIWrapper"
        )

        return GoogleSearchAPIWrapper
    elif name == "GoogleSerperAPIWrapper":
        from aiagentsforce_community.utilities import GoogleSerperAPIWrapper

        _warn_on_import(
            name, replacement="aiagentsforce_community.utilities.GoogleSerperAPIWrapper"
        )

        return GoogleSerperAPIWrapper
    elif name == "PowerBIDataset":
        from aiagentsforce_community.utilities import PowerBIDataset

        _warn_on_import(
            name, replacement="aiagentsforce_community.utilities.PowerBIDataset"
        )

        return PowerBIDataset
    elif name == "SearxSearchWrapper":
        from aiagentsforce_community.utilities import SearxSearchWrapper

        _warn_on_import(
            name, replacement="aiagentsforce_community.utilities.SearxSearchWrapper"
        )

        return SearxSearchWrapper
    elif name == "WikipediaAPIWrapper":
        from aiagentsforce_community.utilities import WikipediaAPIWrapper

        _warn_on_import(
            name, replacement="aiagentsforce_community.utilities.WikipediaAPIWrapper"
        )

        return WikipediaAPIWrapper
    elif name == "WolframAlphaAPIWrapper":
        from aiagentsforce_community.utilities import WolframAlphaAPIWrapper

        _warn_on_import(
            name, replacement="aiagentsforce_community.utilities.WolframAlphaAPIWrapper"
        )

        return WolframAlphaAPIWrapper
    elif name == "SQLDatabase":
        from aiagentsforce_community.utilities import SQLDatabase

        _warn_on_import(name, replacement="aiagentsforce_community.utilities.SQLDatabase")

        return SQLDatabase
    elif name == "FAISS":
        from aiagentsforce_community.vectorstores import FAISS

        _warn_on_import(name, replacement="aiagentsforce_community.vectorstores.FAISS")

        return FAISS
    elif name == "ElasticVectorSearch":
        from aiagentsforce_community.vectorstores import ElasticVectorSearch

        _warn_on_import(
            name, replacement="aiagentsforce_community.vectorstores.ElasticVectorSearch"
        )

        return ElasticVectorSearch
    # For backwards compatibility
    elif name == "SerpAPIChain" or name == "SerpAPIWrapper":
        from aiagentsforce_community.utilities import SerpAPIWrapper

        _warn_on_import(
            name, replacement="aiagentsforce_community.utilities.SerpAPIWrapper"
        )

        return SerpAPIWrapper
    elif name == "verbose":
        from langchain.globals import _verbose

        _warn_on_import(
            name,
            replacement=(
                "langchain.globals.set_verbose() / langchain.globals.get_verbose()"
            ),
        )

        return _verbose
    elif name == "debug":
        from langchain.globals import _debug

        _warn_on_import(
            name,
            replacement=(
                "langchain.globals.set_debug() / langchain.globals.get_debug()"
            ),
        )

        return _debug
    elif name == "llm_cache":
        from langchain.globals import _llm_cache

        _warn_on_import(
            name,
            replacement=(
                "langchain.globals.set_llm_cache() / langchain.globals.get_llm_cache()"
            ),
        )

        return _llm_cache
    else:
        raise AttributeError(f"Could not find: {name}")


__all__ = [
    "LLMChain",
    "LLMCheckerChain",
    "LLMMathChain",
    "ArxivAPIWrapper",
    "GoldenQueryAPIWrapper",
    "SelfAskWithSearchChain",
    "SerpAPIWrapper",
    "SerpAPIChain",
    "SearxSearchWrapper",
    "GoogleSearchAPIWrapper",
    "GoogleSerperAPIWrapper",
    "WolframAlphaAPIWrapper",
    "WikipediaAPIWrapper",
    "Anthropic",
    "Banana",
    "CerebriumAI",
    "Cohere",
    "ForefrontAI",
    "GooseAI",
    "Modal",
    "OpenAI",
    "Petals",
    "PipelineAI",
    "StochasticAI",
    "Writer",
    "BasePromptTemplate",
    "Prompt",
    "FewShotPromptTemplate",
    "PromptTemplate",
    "ReActChain",
    "Wikipedia",
    "HuggingFaceHub",
    "SagemakerEndpoint",
    "HuggingFacePipeline",
    "SQLDatabase",
    "PowerBIDataset",
    "FAISS",
    "MRKLChain",
    "VectorDBQA",
    "ElasticVectorSearch",
    "InMemoryDocstore",
    "ConversationChain",
    "VectorDBQAWithSourcesChain",
    "QAWithSourcesChain",
    "LlamaCpp",
    "HuggingFaceTextGenInference",
]
