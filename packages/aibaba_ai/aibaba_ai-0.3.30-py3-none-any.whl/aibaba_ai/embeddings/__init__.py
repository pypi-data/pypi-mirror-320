"""**Embedding models**  are wrappers around embedding models
from different APIs and services.

**Embedding models** can be LLMs or not.

**Class hierarchy:**

.. code-block::

    Embeddings --> <name>Embeddings  # Examples: OpenAIEmbeddings, HuggingFaceEmbeddings
"""

import logging
from typing import TYPE_CHECKING, Any

from langchain._api import create_importer
from langchain.embeddings.base import init_embeddings
from langchain.embeddings.cache import CacheBackedEmbeddings

if TYPE_CHECKING:
    from aiagentsforce_community.embeddings import (
        AlephAlphaAsymmetricSemanticEmbedding,
        AlephAlphaSymmetricSemanticEmbedding,
        AwaEmbeddings,
        AzureOpenAIEmbeddings,
        BedrockEmbeddings,
        BookendEmbeddings,
        ClarifaiEmbeddings,
        CohereEmbeddings,
        DashScopeEmbeddings,
        DatabricksEmbeddings,
        DeepInfraEmbeddings,
        DeterministicFakeEmbedding,
        EdenAiEmbeddings,
        ElasticsearchEmbeddings,
        EmbaasEmbeddings,
        ErnieEmbeddings,
        FakeEmbeddings,
        FastEmbedEmbeddings,
        GooglePalmEmbeddings,
        GPT4AllEmbeddings,
        GradientEmbeddings,
        HuggingFaceBgeEmbeddings,
        HuggingFaceEmbeddings,
        HuggingFaceHubEmbeddings,
        HuggingFaceInferenceAPIEmbeddings,
        HuggingFaceInstructEmbeddings,
        InfinityEmbeddings,
        JavelinAIGatewayEmbeddings,
        JinaEmbeddings,
        JohnSnowLabsEmbeddings,
        LlamaCppEmbeddings,
        LocalAIEmbeddings,
        MiniMaxEmbeddings,
        MlflowAIGatewayEmbeddings,
        MlflowEmbeddings,
        ModelScopeEmbeddings,
        MosaicMLInstructorEmbeddings,
        NLPCloudEmbeddings,
        OctoAIEmbeddings,
        OllamaEmbeddings,
        OpenAIEmbeddings,
        OpenVINOEmbeddings,
        QianfanEmbeddingsEndpoint,
        SagemakerEndpointEmbeddings,
        SelfHostedEmbeddings,
        SelfHostedHuggingFaceEmbeddings,
        SelfHostedHuggingFaceInstructEmbeddings,
        SentenceTransformerEmbeddings,
        SpacyEmbeddings,
        TensorflowHubEmbeddings,
        VertexAIEmbeddings,
        VoyageEmbeddings,
        XinferenceEmbeddings,
    )


logger = logging.getLogger(__name__)


# TODO: this is in here to maintain backwards compatibility
class HypotheticalDocumentEmbedder:
    def __init__(self, *args: Any, **kwargs: Any):
        logger.warning(
            "Using a deprecated class. Please use "
            "`from langchain.chains import HypotheticalDocumentEmbedder` instead"
        )
        from langchain.chains.hyde.base import HypotheticalDocumentEmbedder as H

        return H(*args, **kwargs)  # type: ignore

    @classmethod
    def from_llm(cls, *args: Any, **kwargs: Any) -> Any:
        logger.warning(
            "Using a deprecated class. Please use "
            "`from langchain.chains import HypotheticalDocumentEmbedder` instead"
        )
        from langchain.chains.hyde.base import HypotheticalDocumentEmbedder as H

        return H.from_llm(*args, **kwargs)


# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "AlephAlphaAsymmetricSemanticEmbedding": "aiagentsforce_community.embeddings",
    "AlephAlphaSymmetricSemanticEmbedding": "aiagentsforce_community.embeddings",
    "AwaEmbeddings": "aiagentsforce_community.embeddings",
    "AzureOpenAIEmbeddings": "aiagentsforce_community.embeddings",
    "BedrockEmbeddings": "aiagentsforce_community.embeddings",
    "BookendEmbeddings": "aiagentsforce_community.embeddings",
    "ClarifaiEmbeddings": "aiagentsforce_community.embeddings",
    "CohereEmbeddings": "aiagentsforce_community.embeddings",
    "DashScopeEmbeddings": "aiagentsforce_community.embeddings",
    "DatabricksEmbeddings": "aiagentsforce_community.embeddings",
    "DeepInfraEmbeddings": "aiagentsforce_community.embeddings",
    "DeterministicFakeEmbedding": "aiagentsforce_community.embeddings",
    "EdenAiEmbeddings": "aiagentsforce_community.embeddings",
    "ElasticsearchEmbeddings": "aiagentsforce_community.embeddings",
    "EmbaasEmbeddings": "aiagentsforce_community.embeddings",
    "ErnieEmbeddings": "aiagentsforce_community.embeddings",
    "FakeEmbeddings": "aiagentsforce_community.embeddings",
    "FastEmbedEmbeddings": "aiagentsforce_community.embeddings",
    "GooglePalmEmbeddings": "aiagentsforce_community.embeddings",
    "GPT4AllEmbeddings": "aiagentsforce_community.embeddings",
    "GradientEmbeddings": "aiagentsforce_community.embeddings",
    "HuggingFaceBgeEmbeddings": "aiagentsforce_community.embeddings",
    "HuggingFaceEmbeddings": "aiagentsforce_community.embeddings",
    "HuggingFaceHubEmbeddings": "aiagentsforce_community.embeddings",
    "HuggingFaceInferenceAPIEmbeddings": "aiagentsforce_community.embeddings",
    "HuggingFaceInstructEmbeddings": "aiagentsforce_community.embeddings",
    "InfinityEmbeddings": "aiagentsforce_community.embeddings",
    "JavelinAIGatewayEmbeddings": "aiagentsforce_community.embeddings",
    "JinaEmbeddings": "aiagentsforce_community.embeddings",
    "JohnSnowLabsEmbeddings": "aiagentsforce_community.embeddings",
    "LlamaCppEmbeddings": "aiagentsforce_community.embeddings",
    "LocalAIEmbeddings": "aiagentsforce_community.embeddings",
    "MiniMaxEmbeddings": "aiagentsforce_community.embeddings",
    "MlflowAIGatewayEmbeddings": "aiagentsforce_community.embeddings",
    "MlflowEmbeddings": "aiagentsforce_community.embeddings",
    "ModelScopeEmbeddings": "aiagentsforce_community.embeddings",
    "MosaicMLInstructorEmbeddings": "aiagentsforce_community.embeddings",
    "NLPCloudEmbeddings": "aiagentsforce_community.embeddings",
    "OctoAIEmbeddings": "aiagentsforce_community.embeddings",
    "OllamaEmbeddings": "aiagentsforce_community.embeddings",
    "OpenAIEmbeddings": "aiagentsforce_community.embeddings",
    "OpenVINOEmbeddings": "aiagentsforce_community.embeddings",
    "QianfanEmbeddingsEndpoint": "aiagentsforce_community.embeddings",
    "SagemakerEndpointEmbeddings": "aiagentsforce_community.embeddings",
    "SelfHostedEmbeddings": "aiagentsforce_community.embeddings",
    "SelfHostedHuggingFaceEmbeddings": "aiagentsforce_community.embeddings",
    "SelfHostedHuggingFaceInstructEmbeddings": "aiagentsforce_community.embeddings",
    "SentenceTransformerEmbeddings": "aiagentsforce_community.embeddings",
    "SpacyEmbeddings": "aiagentsforce_community.embeddings",
    "TensorflowHubEmbeddings": "aiagentsforce_community.embeddings",
    "VertexAIEmbeddings": "aiagentsforce_community.embeddings",
    "VoyageEmbeddings": "aiagentsforce_community.embeddings",
    "XinferenceEmbeddings": "aiagentsforce_community.embeddings",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "AlephAlphaAsymmetricSemanticEmbedding",
    "AlephAlphaSymmetricSemanticEmbedding",
    "AwaEmbeddings",
    "AzureOpenAIEmbeddings",
    "BedrockEmbeddings",
    "BookendEmbeddings",
    "CacheBackedEmbeddings",
    "ClarifaiEmbeddings",
    "CohereEmbeddings",
    "DashScopeEmbeddings",
    "DatabricksEmbeddings",
    "DeepInfraEmbeddings",
    "DeterministicFakeEmbedding",
    "EdenAiEmbeddings",
    "ElasticsearchEmbeddings",
    "EmbaasEmbeddings",
    "ErnieEmbeddings",
    "FakeEmbeddings",
    "FastEmbedEmbeddings",
    "GooglePalmEmbeddings",
    "GPT4AllEmbeddings",
    "GradientEmbeddings",
    "HuggingFaceBgeEmbeddings",
    "HuggingFaceEmbeddings",
    "HuggingFaceHubEmbeddings",
    "HuggingFaceInferenceAPIEmbeddings",
    "HuggingFaceInstructEmbeddings",
    "InfinityEmbeddings",
    "JavelinAIGatewayEmbeddings",
    "JinaEmbeddings",
    "JohnSnowLabsEmbeddings",
    "LlamaCppEmbeddings",
    "LocalAIEmbeddings",
    "MiniMaxEmbeddings",
    "MlflowAIGatewayEmbeddings",
    "MlflowEmbeddings",
    "ModelScopeEmbeddings",
    "MosaicMLInstructorEmbeddings",
    "NLPCloudEmbeddings",
    "OctoAIEmbeddings",
    "OllamaEmbeddings",
    "OpenAIEmbeddings",
    "OpenVINOEmbeddings",
    "QianfanEmbeddingsEndpoint",
    "SagemakerEndpointEmbeddings",
    "SelfHostedEmbeddings",
    "SelfHostedHuggingFaceEmbeddings",
    "SelfHostedHuggingFaceInstructEmbeddings",
    "SentenceTransformerEmbeddings",
    "SpacyEmbeddings",
    "TensorflowHubEmbeddings",
    "VertexAIEmbeddings",
    "VoyageEmbeddings",
    "XinferenceEmbeddings",
    "init_embeddings",
]
