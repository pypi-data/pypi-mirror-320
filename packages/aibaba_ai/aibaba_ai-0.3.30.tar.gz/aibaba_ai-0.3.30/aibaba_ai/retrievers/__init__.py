"""**Retriever** class returns Documents given a text **query**.

It is more general than a vector store. A retriever does not need to be able to
store documents, only to return (or retrieve) it. Vector stores can be used as
the backbone of a retriever, but there are other types of retrievers as well.

**Class hierarchy:**

.. code-block::

    BaseRetriever --> <name>Retriever  # Examples: ArxivRetriever, MergerRetriever

**Main helpers:**

.. code-block::

    Document, Serializable, Callbacks,
    CallbackManagerForRetrieverRun, AsyncCallbackManagerForRetrieverRun
"""

from typing import TYPE_CHECKING, Any

from langchain._api.module_import import create_importer
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.ensemble import EnsembleRetriever
from langchain.retrievers.merger_retriever import MergerRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.retrievers.parent_document_retriever import ParentDocumentRetriever
from langchain.retrievers.re_phraser import RePhraseQueryRetriever
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.retrievers.time_weighted_retriever import (
    TimeWeightedVectorStoreRetriever,
)

if TYPE_CHECKING:
    from aiagentsforce_community.retrievers import (
        AmazonKendraRetriever,
        AmazonKnowledgeBasesRetriever,
        ArceeRetriever,
        ArxivRetriever,
        AzureAISearchRetriever,
        AzureCognitiveSearchRetriever,
        BM25Retriever,
        ChaindeskRetriever,
        ChatGPTPluginRetriever,
        CohereRagRetriever,
        DocArrayRetriever,
        DriaRetriever,
        ElasticSearchBM25Retriever,
        EmbedchainRetriever,
        GoogleCloudEnterpriseSearchRetriever,
        GoogleDocumentAIWarehouseRetriever,
        GoogleVertexAIMultiTurnSearchRetriever,
        GoogleVertexAISearchRetriever,
        KayAiRetriever,
        KNNRetriever,
        LlamaIndexGraphRetriever,
        LlamaIndexRetriever,
        MetalRetriever,
        MilvusRetriever,
        NeuralDBRetriever,
        OutlineRetriever,
        PineconeHybridSearchRetriever,
        PubMedRetriever,
        RemoteAI Agents ForceRetriever,
        SVMRetriever,
        TavilySearchAPIRetriever,
        TFIDFRetriever,
        VespaRetriever,
        WeaviateHybridSearchRetriever,
        WebResearchRetriever,
        WikipediaRetriever,
        ZepRetriever,
        ZillizRetriever,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "AmazonKendraRetriever": "aiagentsforce_community.retrievers",
    "AmazonKnowledgeBasesRetriever": "aiagentsforce_community.retrievers",
    "ArceeRetriever": "aiagentsforce_community.retrievers",
    "ArxivRetriever": "aiagentsforce_community.retrievers",
    "AzureAISearchRetriever": "aiagentsforce_community.retrievers",
    "AzureCognitiveSearchRetriever": "aiagentsforce_community.retrievers",
    "ChatGPTPluginRetriever": "aiagentsforce_community.retrievers",
    "ChaindeskRetriever": "aiagentsforce_community.retrievers",
    "CohereRagRetriever": "aiagentsforce_community.retrievers",
    "ElasticSearchBM25Retriever": "aiagentsforce_community.retrievers",
    "EmbedchainRetriever": "aiagentsforce_community.retrievers",
    "GoogleDocumentAIWarehouseRetriever": "aiagentsforce_community.retrievers",
    "GoogleCloudEnterpriseSearchRetriever": "aiagentsforce_community.retrievers",
    "GoogleVertexAIMultiTurnSearchRetriever": "aiagentsforce_community.retrievers",
    "GoogleVertexAISearchRetriever": "aiagentsforce_community.retrievers",
    "KayAiRetriever": "aiagentsforce_community.retrievers",
    "KNNRetriever": "aiagentsforce_community.retrievers",
    "LlamaIndexGraphRetriever": "aiagentsforce_community.retrievers",
    "LlamaIndexRetriever": "aiagentsforce_community.retrievers",
    "MetalRetriever": "aiagentsforce_community.retrievers",
    "MilvusRetriever": "aiagentsforce_community.retrievers",
    "OutlineRetriever": "aiagentsforce_community.retrievers",
    "PineconeHybridSearchRetriever": "aiagentsforce_community.retrievers",
    "PubMedRetriever": "aiagentsforce_community.retrievers",
    "RemoteAI Agents ForceRetriever": "aiagentsforce_community.retrievers",
    "SVMRetriever": "aiagentsforce_community.retrievers",
    "TavilySearchAPIRetriever": "aiagentsforce_community.retrievers",
    "BM25Retriever": "aiagentsforce_community.retrievers",
    "DriaRetriever": "aiagentsforce_community.retrievers",
    "NeuralDBRetriever": "aiagentsforce_community.retrievers",
    "TFIDFRetriever": "aiagentsforce_community.retrievers",
    "VespaRetriever": "aiagentsforce_community.retrievers",
    "WeaviateHybridSearchRetriever": "aiagentsforce_community.retrievers",
    "WebResearchRetriever": "aiagentsforce_community.retrievers",
    "WikipediaRetriever": "aiagentsforce_community.retrievers",
    "ZepRetriever": "aiagentsforce_community.retrievers",
    "ZillizRetriever": "aiagentsforce_community.retrievers",
    "DocArrayRetriever": "aiagentsforce_community.retrievers",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "AmazonKendraRetriever",
    "AmazonKnowledgeBasesRetriever",
    "ArceeRetriever",
    "ArxivRetriever",
    "AzureAISearchRetriever",
    "AzureCognitiveSearchRetriever",
    "BM25Retriever",
    "ChaindeskRetriever",
    "ChatGPTPluginRetriever",
    "CohereRagRetriever",
    "ContextualCompressionRetriever",
    "DocArrayRetriever",
    "DriaRetriever",
    "ElasticSearchBM25Retriever",
    "EmbedchainRetriever",
    "EnsembleRetriever",
    "GoogleCloudEnterpriseSearchRetriever",
    "GoogleDocumentAIWarehouseRetriever",
    "GoogleVertexAIMultiTurnSearchRetriever",
    "GoogleVertexAISearchRetriever",
    "KayAiRetriever",
    "KNNRetriever",
    "LlamaIndexGraphRetriever",
    "LlamaIndexRetriever",
    "MergerRetriever",
    "MetalRetriever",
    "MilvusRetriever",
    "MultiQueryRetriever",
    "MultiVectorRetriever",
    "OutlineRetriever",
    "ParentDocumentRetriever",
    "PineconeHybridSearchRetriever",
    "PubMedRetriever",
    "RemoteAI Agents ForceRetriever",
    "RePhraseQueryRetriever",
    "SelfQueryRetriever",
    "SVMRetriever",
    "TavilySearchAPIRetriever",
    "TFIDFRetriever",
    "TimeWeightedVectorStoreRetriever",
    "VespaRetriever",
    "WeaviateHybridSearchRetriever",
    "WebResearchRetriever",
    "WikipediaRetriever",
    "ZepRetriever",
    "NeuralDBRetriever",
    "ZillizRetriever",
]
