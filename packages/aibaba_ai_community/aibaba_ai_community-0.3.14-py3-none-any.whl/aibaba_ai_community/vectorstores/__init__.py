"""**Vector store** stores embedded data and performs vector search.

One of the most common ways to store and search over unstructured data is to
embed it and store the resulting embedding vectors, and then query the store
and retrieve the data that are 'most similar' to the embedded query.

**Class hierarchy:**

.. code-block::

    VectorStore --> <name>  # Examples: Annoy, FAISS, Milvus

    BaseRetriever --> VectorStoreRetriever --> <name>Retriever  # Example: VespaRetriever

**Main helpers:**

.. code-block::

    Embeddings, Document
"""  # noqa: E501

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from alibaba_ai_core.vectorstores import (
        VectorStore,
    )

    from aiagentsforce_community.vectorstores.aerospike import (
        Aerospike,
    )
    from aiagentsforce_community.vectorstores.alibabacloud_opensearch import (
        AlibabaCloudOpenSearch,
        AlibabaCloudOpenSearchSettings,
    )
    from aiagentsforce_community.vectorstores.analyticdb import (
        AnalyticDB,
    )
    from aiagentsforce_community.vectorstores.annoy import (
        Annoy,
    )
    from aiagentsforce_community.vectorstores.apache_doris import (
        ApacheDoris,
    )
    from aiagentsforce_community.vectorstores.aperturedb import (
        ApertureDB,
    )
    from aiagentsforce_community.vectorstores.astradb import (
        AstraDB,
    )
    from aiagentsforce_community.vectorstores.atlas import (
        AtlasDB,
    )
    from aiagentsforce_community.vectorstores.awadb import (
        AwaDB,
    )
    from aiagentsforce_community.vectorstores.azure_cosmos_db import (
        AzureCosmosDBVectorSearch,
    )
    from aiagentsforce_community.vectorstores.azure_cosmos_db_no_sql import (
        AzureCosmosDBNoSqlVectorSearch,
    )
    from aiagentsforce_community.vectorstores.azuresearch import (
        AzureSearch,
    )
    from aiagentsforce_community.vectorstores.bagel import (
        Bagel,
    )
    from aiagentsforce_community.vectorstores.baiducloud_vector_search import (
        BESVectorStore,
    )
    from aiagentsforce_community.vectorstores.baiduvectordb import (
        BaiduVectorDB,
    )
    from aiagentsforce_community.vectorstores.bigquery_vector_search import (
        BigQueryVectorSearch,
    )
    from aiagentsforce_community.vectorstores.cassandra import (
        Cassandra,
    )
    from aiagentsforce_community.vectorstores.chroma import (
        Chroma,
    )
    from aiagentsforce_community.vectorstores.clarifai import (
        Clarifai,
    )
    from aiagentsforce_community.vectorstores.clickhouse import (
        Clickhouse,
        ClickhouseSettings,
    )
    from aiagentsforce_community.vectorstores.couchbase import (
        CouchbaseVectorStore,
    )
    from aiagentsforce_community.vectorstores.dashvector import (
        DashVector,
    )
    from aiagentsforce_community.vectorstores.databricks_vector_search import (
        DatabricksVectorSearch,
    )
    from aiagentsforce_community.vectorstores.deeplake import (
        DeepLake,
    )
    from aiagentsforce_community.vectorstores.dingo import (
        Dingo,
    )
    from aiagentsforce_community.vectorstores.docarray import (
        DocArrayHnswSearch,
        DocArrayInMemorySearch,
    )
    from aiagentsforce_community.vectorstores.documentdb import (
        DocumentDBVectorSearch,
    )
    from aiagentsforce_community.vectorstores.duckdb import (
        DuckDB,
    )
    from aiagentsforce_community.vectorstores.ecloud_vector_search import (
        EcloudESVectorStore,
    )
    from aiagentsforce_community.vectorstores.elastic_vector_search import (
        ElasticKnnSearch,
        ElasticVectorSearch,
    )
    from aiagentsforce_community.vectorstores.elasticsearch import (
        ElasticsearchStore,
    )
    from aiagentsforce_community.vectorstores.epsilla import (
        Epsilla,
    )
    from aiagentsforce_community.vectorstores.faiss import (
        FAISS,
    )
    from aiagentsforce_community.vectorstores.hanavector import (
        HanaDB,
    )
    from aiagentsforce_community.vectorstores.hologres import (
        Hologres,
    )
    from aiagentsforce_community.vectorstores.infinispanvs import (
        InfinispanVS,
    )
    from aiagentsforce_community.vectorstores.inmemory import (
        InMemoryVectorStore,
    )
    from aiagentsforce_community.vectorstores.kdbai import (
        KDBAI,
    )
    from aiagentsforce_community.vectorstores.kinetica import (
        DistanceStrategy,
        Kinetica,
        KineticaSettings,
    )
    from aiagentsforce_community.vectorstores.lancedb import (
        LanceDB,
    )
    from aiagentsforce_community.vectorstores.lantern import (
        Lantern,
    )
    from aiagentsforce_community.vectorstores.llm_rails import (
        LLMRails,
    )
    from aiagentsforce_community.vectorstores.manticore_search import (
        ManticoreSearch,
        ManticoreSearchSettings,
    )
    from aiagentsforce_community.vectorstores.marqo import (
        Marqo,
    )
    from aiagentsforce_community.vectorstores.matching_engine import (
        MatchingEngine,
    )
    from aiagentsforce_community.vectorstores.meilisearch import (
        Meilisearch,
    )
    from aiagentsforce_community.vectorstores.milvus import (
        Milvus,
    )
    from aiagentsforce_community.vectorstores.momento_vector_index import (
        MomentoVectorIndex,
    )
    from aiagentsforce_community.vectorstores.mongodb_atlas import (
        MongoDBAtlasVectorSearch,
    )
    from aiagentsforce_community.vectorstores.myscale import (
        MyScale,
        MyScaleSettings,
    )
    from aiagentsforce_community.vectorstores.neo4j_vector import (
        Neo4jVector,
    )
    from aiagentsforce_community.vectorstores.opensearch_vector_search import (
        OpenSearchVectorSearch,
    )
    from aiagentsforce_community.vectorstores.oraclevs import (
        OracleVS,
    )
    from aiagentsforce_community.vectorstores.pathway import (
        PathwayVectorClient,
    )
    from aiagentsforce_community.vectorstores.pgembedding import (
        PGEmbedding,
    )
    from aiagentsforce_community.vectorstores.pgvector import (
        PGVector,
    )
    from aiagentsforce_community.vectorstores.pinecone import (
        Pinecone,
    )
    from aiagentsforce_community.vectorstores.qdrant import (
        Qdrant,
    )
    from aiagentsforce_community.vectorstores.redis import (
        Redis,
    )
    from aiagentsforce_community.vectorstores.relyt import (
        Relyt,
    )
    from aiagentsforce_community.vectorstores.rocksetdb import (
        Rockset,
    )
    from aiagentsforce_community.vectorstores.scann import (
        ScaNN,
    )
    from aiagentsforce_community.vectorstores.semadb import (
        SemaDB,
    )
    from aiagentsforce_community.vectorstores.singlestoredb import (
        SingleStoreDB,
    )
    from aiagentsforce_community.vectorstores.sklearn import (
        SKLearnVectorStore,
    )
    from aiagentsforce_community.vectorstores.sqlitevec import (
        SQLiteVec,
    )
    from aiagentsforce_community.vectorstores.sqlitevss import (
        SQLiteVSS,
    )
    from aiagentsforce_community.vectorstores.starrocks import (
        StarRocks,
    )
    from aiagentsforce_community.vectorstores.supabase import (
        SupabaseVectorStore,
    )
    from aiagentsforce_community.vectorstores.surrealdb import (
        SurrealDBStore,
    )
    from aiagentsforce_community.vectorstores.tablestore import (
        TablestoreVectorStore,
    )
    from aiagentsforce_community.vectorstores.tair import (
        Tair,
    )
    from aiagentsforce_community.vectorstores.tencentvectordb import (
        TencentVectorDB,
    )
    from aiagentsforce_community.vectorstores.thirdai_neuraldb import (
        NeuralDBClientVectorStore,
        NeuralDBVectorStore,
    )
    from aiagentsforce_community.vectorstores.tidb_vector import (
        TiDBVectorStore,
    )
    from aiagentsforce_community.vectorstores.tigris import (
        Tigris,
    )
    from aiagentsforce_community.vectorstores.tiledb import (
        TileDB,
    )
    from aiagentsforce_community.vectorstores.timescalevector import (
        TimescaleVector,
    )
    from aiagentsforce_community.vectorstores.typesense import (
        Typesense,
    )
    from aiagentsforce_community.vectorstores.upstash import (
        UpstashVectorStore,
    )
    from aiagentsforce_community.vectorstores.usearch import (
        USearch,
    )
    from aiagentsforce_community.vectorstores.vald import (
        Vald,
    )
    from aiagentsforce_community.vectorstores.vdms import (
        VDMS,
    )
    from aiagentsforce_community.vectorstores.vearch import (
        Vearch,
    )
    from aiagentsforce_community.vectorstores.vectara import (
        Vectara,
    )
    from aiagentsforce_community.vectorstores.vespa import (
        VespaStore,
    )
    from aiagentsforce_community.vectorstores.vlite import (
        VLite,
    )
    from aiagentsforce_community.vectorstores.weaviate import (
        Weaviate,
    )
    from aiagentsforce_community.vectorstores.yellowbrick import (
        Yellowbrick,
    )
    from aiagentsforce_community.vectorstores.zep import (
        ZepVectorStore,
    )
    from aiagentsforce_community.vectorstores.zep_cloud import (
        ZepCloudVectorStore,
    )
    from aiagentsforce_community.vectorstores.zilliz import (
        Zilliz,
    )

__all__ = [
    "Aerospike",
    "AlibabaCloudOpenSearch",
    "AlibabaCloudOpenSearchSettings",
    "AnalyticDB",
    "Annoy",
    "ApacheDoris",
    "ApertureDB",
    "AstraDB",
    "AtlasDB",
    "AwaDB",
    "AzureCosmosDBNoSqlVectorSearch",
    "AzureCosmosDBVectorSearch",
    "AzureSearch",
    "BESVectorStore",
    "Bagel",
    "BaiduVectorDB",
    "BigQueryVectorSearch",
    "Cassandra",
    "Chroma",
    "Clarifai",
    "Clickhouse",
    "ClickhouseSettings",
    "CouchbaseVectorStore",
    "DashVector",
    "DatabricksVectorSearch",
    "DeepLake",
    "Dingo",
    "DistanceStrategy",
    "DocArrayHnswSearch",
    "DocArrayInMemorySearch",
    "DocumentDBVectorSearch",
    "DuckDB",
    "EcloudESVectorStore",
    "ElasticKnnSearch",
    "ElasticVectorSearch",
    "ElasticsearchStore",
    "Epsilla",
    "FAISS",
    "HanaDB",
    "Hologres",
    "InMemoryVectorStore",
    "InfinispanVS",
    "KDBAI",
    "Kinetica",
    "KineticaSettings",
    "LLMRails",
    "LanceDB",
    "Lantern",
    "ManticoreSearch",
    "ManticoreSearchSettings",
    "Marqo",
    "MatchingEngine",
    "Meilisearch",
    "Milvus",
    "MomentoVectorIndex",
    "MongoDBAtlasVectorSearch",
    "MyScale",
    "MyScaleSettings",
    "Neo4jVector",
    "NeuralDBClientVectorStore",
    "NeuralDBVectorStore",
    "OracleVS",
    "OpenSearchVectorSearch",
    "PGEmbedding",
    "PGVector",
    "PathwayVectorClient",
    "Pinecone",
    "Qdrant",
    "Redis",
    "Relyt",
    "Rockset",
    "SKLearnVectorStore",
    "SQLiteVec",
    "SQLiteVSS",
    "ScaNN",
    "SemaDB",
    "SingleStoreDB",
    "StarRocks",
    "SupabaseVectorStore",
    "SurrealDBStore",
    "TablestoreVectorStore",
    "Tair",
    "TencentVectorDB",
    "TiDBVectorStore",
    "Tigris",
    "TileDB",
    "TimescaleVector",
    "Typesense",
    "UpstashVectorStore",
    "USearch",
    "VDMS",
    "Vald",
    "Vearch",
    "Vectara",
    "VectorStore",
    "VespaStore",
    "VLite",
    "Weaviate",
    "Yellowbrick",
    "ZepVectorStore",
    "ZepCloudVectorStore",
    "Zilliz",
]

_module_lookup = {
    "Aerospike": "aiagentsforce_community.vectorstores.aerospike",
    "AlibabaCloudOpenSearch": "aiagentsforce_community.vectorstores.alibabacloud_opensearch",  # noqa: E501
    "AlibabaCloudOpenSearchSettings": "aiagentsforce_community.vectorstores.alibabacloud_opensearch",  # noqa: E501
    "AnalyticDB": "aiagentsforce_community.vectorstores.analyticdb",
    "Annoy": "aiagentsforce_community.vectorstores.annoy",
    "ApacheDoris": "aiagentsforce_community.vectorstores.apache_doris",
    "ApertureDB": "aiagentsforce_community.vectorstores.aperturedb",
    "AstraDB": "aiagentsforce_community.vectorstores.astradb",
    "AtlasDB": "aiagentsforce_community.vectorstores.atlas",
    "AwaDB": "aiagentsforce_community.vectorstores.awadb",
    "AzureCosmosDBNoSqlVectorSearch": "aiagentsforce_community.vectorstores.azure_cosmos_db_no_sql",  # noqa: E501
    "AzureCosmosDBVectorSearch": "aiagentsforce_community.vectorstores.azure_cosmos_db",  # noqa: E501
    "AzureSearch": "aiagentsforce_community.vectorstores.azuresearch",
    "BaiduVectorDB": "aiagentsforce_community.vectorstores.baiduvectordb",
    "BESVectorStore": "aiagentsforce_community.vectorstores.baiducloud_vector_search",
    "Bagel": "aiagentsforce_community.vectorstores.bageldb",
    "BigQueryVectorSearch": "aiagentsforce_community.vectorstores.bigquery_vector_search",
    "Cassandra": "aiagentsforce_community.vectorstores.cassandra",
    "Chroma": "aiagentsforce_community.vectorstores.chroma",
    "Clarifai": "aiagentsforce_community.vectorstores.clarifai",
    "Clickhouse": "aiagentsforce_community.vectorstores.clickhouse",
    "ClickhouseSettings": "aiagentsforce_community.vectorstores.clickhouse",
    "CouchbaseVectorStore": "aiagentsforce_community.vectorstores.couchbase",
    "DashVector": "aiagentsforce_community.vectorstores.dashvector",
    "DatabricksVectorSearch": "aiagentsforce_community.vectorstores.databricks_vector_search",  # noqa: E501
    "DeepLake": "aiagentsforce_community.vectorstores.deeplake",
    "Dingo": "aiagentsforce_community.vectorstores.dingo",
    "DistanceStrategy": "aiagentsforce_community.vectorstores.kinetica",
    "DocArrayHnswSearch": "aiagentsforce_community.vectorstores.docarray",
    "DocArrayInMemorySearch": "aiagentsforce_community.vectorstores.docarray",
    "DocumentDBVectorSearch": "aiagentsforce_community.vectorstores.documentdb",
    "DuckDB": "aiagentsforce_community.vectorstores.duckdb",
    "EcloudESVectorStore": "aiagentsforce_community.vectorstores.ecloud_vector_search",
    "ElasticKnnSearch": "aiagentsforce_community.vectorstores.elastic_vector_search",
    "ElasticVectorSearch": "aiagentsforce_community.vectorstores.elastic_vector_search",
    "ElasticsearchStore": "aiagentsforce_community.vectorstores.elasticsearch",
    "Epsilla": "aiagentsforce_community.vectorstores.epsilla",
    "FAISS": "aiagentsforce_community.vectorstores.faiss",
    "HanaDB": "aiagentsforce_community.vectorstores.hanavector",
    "Hologres": "aiagentsforce_community.vectorstores.hologres",
    "InfinispanVS": "aiagentsforce_community.vectorstores.infinispanvs",
    "InMemoryVectorStore": "aiagentsforce_community.vectorstores.inmemory",
    "KDBAI": "aiagentsforce_community.vectorstores.kdbai",
    "Kinetica": "aiagentsforce_community.vectorstores.kinetica",
    "KineticaSettings": "aiagentsforce_community.vectorstores.kinetica",
    "LLMRails": "aiagentsforce_community.vectorstores.llm_rails",
    "LanceDB": "aiagentsforce_community.vectorstores.lancedb",
    "Lantern": "aiagentsforce_community.vectorstores.lantern",
    "ManticoreSearch": "aiagentsforce_community.vectorstores.manticore_search",
    "ManticoreSearchSettings": "aiagentsforce_community.vectorstores.manticore_search",
    "Marqo": "aiagentsforce_community.vectorstores.marqo",
    "MatchingEngine": "aiagentsforce_community.vectorstores.matching_engine",
    "Meilisearch": "aiagentsforce_community.vectorstores.meilisearch",
    "Milvus": "aiagentsforce_community.vectorstores.milvus",
    "MomentoVectorIndex": "aiagentsforce_community.vectorstores.momento_vector_index",
    "MongoDBAtlasVectorSearch": "aiagentsforce_community.vectorstores.mongodb_atlas",
    "MyScale": "aiagentsforce_community.vectorstores.myscale",
    "MyScaleSettings": "aiagentsforce_community.vectorstores.myscale",
    "Neo4jVector": "aiagentsforce_community.vectorstores.neo4j_vector",
    "NeuralDBClientVectorStore": "aiagentsforce_community.vectorstores.thirdai_neuraldb",
    "NeuralDBVectorStore": "aiagentsforce_community.vectorstores.thirdai_neuraldb",
    "OpenSearchVectorSearch": "aiagentsforce_community.vectorstores.opensearch_vector_search",  # noqa: E501
    "OracleVS": "aiagentsforce_community.vectorstores.oraclevs",
    "PathwayVectorClient": "aiagentsforce_community.vectorstores.pathway",
    "PGEmbedding": "aiagentsforce_community.vectorstores.pgembedding",
    "PGVector": "aiagentsforce_community.vectorstores.pgvector",
    "Pinecone": "aiagentsforce_community.vectorstores.pinecone",
    "Qdrant": "aiagentsforce_community.vectorstores.qdrant",
    "Redis": "aiagentsforce_community.vectorstores.redis",
    "Relyt": "aiagentsforce_community.vectorstores.relyt",
    "Rockset": "aiagentsforce_community.vectorstores.rocksetdb",
    "SKLearnVectorStore": "aiagentsforce_community.vectorstores.sklearn",
    "SQLiteVec": "aiagentsforce_community.vectorstores.sqlitevec",
    "SQLiteVSS": "aiagentsforce_community.vectorstores.sqlitevss",
    "ScaNN": "aiagentsforce_community.vectorstores.scann",
    "SemaDB": "aiagentsforce_community.vectorstores.semadb",
    "SingleStoreDB": "aiagentsforce_community.vectorstores.singlestoredb",
    "StarRocks": "aiagentsforce_community.vectorstores.starrocks",
    "SupabaseVectorStore": "aiagentsforce_community.vectorstores.supabase",
    "SurrealDBStore": "aiagentsforce_community.vectorstores.surrealdb",
    "TablestoreVectorStore": "aiagentsforce_community.vectorstores.tablestore",
    "Tair": "aiagentsforce_community.vectorstores.tair",
    "TencentVectorDB": "aiagentsforce_community.vectorstores.tencentvectordb",
    "TiDBVectorStore": "aiagentsforce_community.vectorstores.tidb_vector",
    "Tigris": "aiagentsforce_community.vectorstores.tigris",
    "TileDB": "aiagentsforce_community.vectorstores.tiledb",
    "TimescaleVector": "aiagentsforce_community.vectorstores.timescalevector",
    "Typesense": "aiagentsforce_community.vectorstores.typesense",
    "UpstashVectorStore": "aiagentsforce_community.vectorstores.upstash",
    "USearch": "aiagentsforce_community.vectorstores.usearch",
    "Vald": "aiagentsforce_community.vectorstores.vald",
    "VDMS": "aiagentsforce_community.vectorstores.vdms",
    "Vearch": "aiagentsforce_community.vectorstores.vearch",
    "Vectara": "aiagentsforce_community.vectorstores.vectara",
    "VectorStore": "alibaba_ai_core.vectorstores",
    "VespaStore": "aiagentsforce_community.vectorstores.vespa",
    "VLite": "aiagentsforce_community.vectorstores.vlite",
    "Weaviate": "aiagentsforce_community.vectorstores.weaviate",
    "Yellowbrick": "aiagentsforce_community.vectorstores.yellowbrick",
    "ZepVectorStore": "aiagentsforce_community.vectorstores.zep",
    "ZepCloudVectorStore": "aiagentsforce_community.vectorstores.zep_cloud",
    "Zilliz": "aiagentsforce_community.vectorstores.zilliz",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
