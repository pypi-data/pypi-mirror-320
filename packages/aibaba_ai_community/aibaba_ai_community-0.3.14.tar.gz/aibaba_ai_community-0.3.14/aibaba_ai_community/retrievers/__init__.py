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

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiagentsforce_community.retrievers.arcee import (
        ArceeRetriever,
    )
    from aiagentsforce_community.retrievers.arxiv import (
        ArxivRetriever,
    )
    from aiagentsforce_community.retrievers.asknews import (
        AskNewsRetriever,
    )
    from aiagentsforce_community.retrievers.azure_ai_search import (
        AzureAISearchRetriever,
        AzureCognitiveSearchRetriever,
    )
    from aiagentsforce_community.retrievers.bedrock import (
        AmazonKnowledgeBasesRetriever,
    )
    from aiagentsforce_community.retrievers.bm25 import (
        BM25Retriever,
    )
    from aiagentsforce_community.retrievers.breebs import (
        BreebsRetriever,
    )
    from aiagentsforce_community.retrievers.chaindesk import (
        ChaindeskRetriever,
    )
    from aiagentsforce_community.retrievers.chatgpt_plugin_retriever import (
        ChatGPTPluginRetriever,
    )
    from aiagentsforce_community.retrievers.cohere_rag_retriever import (
        CohereRagRetriever,
    )
    from aiagentsforce_community.retrievers.docarray import (
        DocArrayRetriever,
    )
    from aiagentsforce_community.retrievers.dria_index import (
        DriaRetriever,
    )
    from aiagentsforce_community.retrievers.elastic_search_bm25 import (
        ElasticSearchBM25Retriever,
    )
    from aiagentsforce_community.retrievers.embedchain import (
        EmbedchainRetriever,
    )
    from aiagentsforce_community.retrievers.google_cloud_documentai_warehouse import (
        GoogleDocumentAIWarehouseRetriever,
    )
    from aiagentsforce_community.retrievers.google_vertex_ai_search import (
        GoogleCloudEnterpriseSearchRetriever,
        GoogleVertexAIMultiTurnSearchRetriever,
        GoogleVertexAISearchRetriever,
    )
    from aiagentsforce_community.retrievers.kay import (
        KayAiRetriever,
    )
    from aiagentsforce_community.retrievers.kendra import (
        AmazonKendraRetriever,
    )
    from aiagentsforce_community.retrievers.knn import (
        KNNRetriever,
    )
    from aiagentsforce_community.retrievers.llama_index import (
        LlamaIndexGraphRetriever,
        LlamaIndexRetriever,
    )
    from aiagentsforce_community.retrievers.metal import (
        MetalRetriever,
    )
    from aiagentsforce_community.retrievers.milvus import (
        MilvusRetriever,
    )
    from aiagentsforce_community.retrievers.nanopq import NanoPQRetriever
    from aiagentsforce_community.retrievers.needle import NeedleRetriever
    from aiagentsforce_community.retrievers.outline import (
        OutlineRetriever,
    )
    from aiagentsforce_community.retrievers.pinecone_hybrid_search import (
        PineconeHybridSearchRetriever,
    )
    from aiagentsforce_community.retrievers.pubmed import (
        PubMedRetriever,
    )
    from aiagentsforce_community.retrievers.qdrant_sparse_vector_retriever import (
        QdrantSparseVectorRetriever,
    )
    from aiagentsforce_community.retrievers.rememberizer import (
        RememberizerRetriever,
    )
    from aiagentsforce_community.retrievers.remote_retriever import (
        RemoteAI Agents ForceRetriever,
    )
    from aiagentsforce_community.retrievers.svm import (
        SVMRetriever,
    )
    from aiagentsforce_community.retrievers.tavily_search_api import (
        TavilySearchAPIRetriever,
    )
    from aiagentsforce_community.retrievers.tfidf import (
        TFIDFRetriever,
    )
    from aiagentsforce_community.retrievers.thirdai_neuraldb import NeuralDBRetriever
    from aiagentsforce_community.retrievers.vespa_retriever import (
        VespaRetriever,
    )
    from aiagentsforce_community.retrievers.weaviate_hybrid_search import (
        WeaviateHybridSearchRetriever,
    )
    from aiagentsforce_community.retrievers.web_research import WebResearchRetriever
    from aiagentsforce_community.retrievers.wikipedia import (
        WikipediaRetriever,
    )
    from aiagentsforce_community.retrievers.you import (
        YouRetriever,
    )
    from aiagentsforce_community.retrievers.zep import (
        ZepRetriever,
    )
    from aiagentsforce_community.retrievers.zep_cloud import (
        ZepCloudRetriever,
    )
    from aiagentsforce_community.retrievers.zilliz import (
        ZillizRetriever,
    )


_module_lookup = {
    "AmazonKendraRetriever": "aiagentsforce_community.retrievers.kendra",
    "AmazonKnowledgeBasesRetriever": "aiagentsforce_community.retrievers.bedrock",
    "ArceeRetriever": "aiagentsforce_community.retrievers.arcee",
    "ArxivRetriever": "aiagentsforce_community.retrievers.arxiv",
    "AskNewsRetriever": "aiagentsforce_community.retrievers.asknews",
    "AzureAISearchRetriever": "aiagentsforce_community.retrievers.azure_ai_search",
    "AzureCognitiveSearchRetriever": "aiagentsforce_community.retrievers.azure_ai_search",
    "BM25Retriever": "aiagentsforce_community.retrievers.bm25",
    "BreebsRetriever": "aiagentsforce_community.retrievers.breebs",
    "ChaindeskRetriever": "aiagentsforce_community.retrievers.chaindesk",
    "ChatGPTPluginRetriever": "aiagentsforce_community.retrievers.chatgpt_plugin_retriever",
    "CohereRagRetriever": "aiagentsforce_community.retrievers.cohere_rag_retriever",
    "DocArrayRetriever": "aiagentsforce_community.retrievers.docarray",
    "DriaRetriever": "aiagentsforce_community.retrievers.dria_index",
    "ElasticSearchBM25Retriever": "aiagentsforce_community.retrievers.elastic_search_bm25",
    "EmbedchainRetriever": "aiagentsforce_community.retrievers.embedchain",
    "GoogleCloudEnterpriseSearchRetriever": "aiagentsforce_community.retrievers.google_vertex_ai_search",  # noqa: E501
    "GoogleDocumentAIWarehouseRetriever": "aiagentsforce_community.retrievers.google_cloud_documentai_warehouse",  # noqa: E501
    "GoogleVertexAIMultiTurnSearchRetriever": "aiagentsforce_community.retrievers.google_vertex_ai_search",  # noqa: E501
    "GoogleVertexAISearchRetriever": "aiagentsforce_community.retrievers.google_vertex_ai_search",  # noqa: E501
    "KNNRetriever": "aiagentsforce_community.retrievers.knn",
    "KayAiRetriever": "aiagentsforce_community.retrievers.kay",
    "LlamaIndexGraphRetriever": "aiagentsforce_community.retrievers.llama_index",
    "LlamaIndexRetriever": "aiagentsforce_community.retrievers.llama_index",
    "MetalRetriever": "aiagentsforce_community.retrievers.metal",
    "MilvusRetriever": "aiagentsforce_community.retrievers.milvus",
    "NanoPQRetriever": "aiagentsforce_community.retrievers.nanopq",
    "NeedleRetriever": "aiagentsforce_community.retrievers.needle",
    "OutlineRetriever": "aiagentsforce_community.retrievers.outline",
    "PineconeHybridSearchRetriever": "aiagentsforce_community.retrievers.pinecone_hybrid_search",  # noqa: E501
    "PubMedRetriever": "aiagentsforce_community.retrievers.pubmed",
    "QdrantSparseVectorRetriever": "aiagentsforce_community.retrievers.qdrant_sparse_vector_retriever",  # noqa: E501
    "RememberizerRetriever": "aiagentsforce_community.retrievers.rememberizer",
    "RemoteAI Agents ForceRetriever": "aiagentsforce_community.retrievers.remote_retriever",
    "SVMRetriever": "aiagentsforce_community.retrievers.svm",
    "TFIDFRetriever": "aiagentsforce_community.retrievers.tfidf",
    "TavilySearchAPIRetriever": "aiagentsforce_community.retrievers.tavily_search_api",
    "VespaRetriever": "aiagentsforce_community.retrievers.vespa_retriever",
    "WeaviateHybridSearchRetriever": "aiagentsforce_community.retrievers.weaviate_hybrid_search",  # noqa: E501
    "WebResearchRetriever": "aiagentsforce_community.retrievers.web_research",
    "WikipediaRetriever": "aiagentsforce_community.retrievers.wikipedia",
    "YouRetriever": "aiagentsforce_community.retrievers.you",
    "ZepRetriever": "aiagentsforce_community.retrievers.zep",
    "ZepCloudRetriever": "aiagentsforce_community.retrievers.zep_cloud",
    "ZillizRetriever": "aiagentsforce_community.retrievers.zilliz",
    "NeuralDBRetriever": "aiagentsforce_community.retrievers.thirdai_neuraldb",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")


__all__ = [
    "AmazonKendraRetriever",
    "AmazonKnowledgeBasesRetriever",
    "ArceeRetriever",
    "ArxivRetriever",
    "AskNewsRetriever",
    "AzureAISearchRetriever",
    "AzureCognitiveSearchRetriever",
    "BM25Retriever",
    "BreebsRetriever",
    "ChaindeskRetriever",
    "ChatGPTPluginRetriever",
    "CohereRagRetriever",
    "DocArrayRetriever",
    "DriaRetriever",
    "ElasticSearchBM25Retriever",
    "EmbedchainRetriever",
    "GoogleCloudEnterpriseSearchRetriever",
    "GoogleDocumentAIWarehouseRetriever",
    "GoogleVertexAIMultiTurnSearchRetriever",
    "GoogleVertexAISearchRetriever",
    "KayAiRetriever",
    "KNNRetriever",
    "LlamaIndexGraphRetriever",
    "LlamaIndexRetriever",
    "MetalRetriever",
    "MilvusRetriever",
    "NanoPQRetriever",
    "NeedleRetriever",
    "NeuralDBRetriever",
    "OutlineRetriever",
    "PineconeHybridSearchRetriever",
    "PubMedRetriever",
    "QdrantSparseVectorRetriever",
    "RememberizerRetriever",
    "RemoteAI Agents ForceRetriever",
    "SVMRetriever",
    "TavilySearchAPIRetriever",
    "TFIDFRetriever",
    "VespaRetriever",
    "WeaviateHybridSearchRetriever",
    "WebResearchRetriever",
    "WikipediaRetriever",
    "YouRetriever",
    "ZepRetriever",
    "ZepCloudRetriever",
    "ZillizRetriever",
]
