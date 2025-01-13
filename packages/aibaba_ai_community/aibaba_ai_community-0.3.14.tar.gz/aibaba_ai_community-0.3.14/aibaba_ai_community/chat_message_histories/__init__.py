"""**Chat message history** stores a history of the message interactions in a chat.


**Class hierarchy:**

.. code-block::

    BaseChatMessageHistory --> <name>ChatMessageHistory  # Examples: FileChatMessageHistory, PostgresChatMessageHistory

**Main helpers:**

.. code-block::

    AIMessage, HumanMessage, BaseMessage

"""  # noqa: E501

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiagentsforce_community.chat_message_histories.astradb import (
        AstraDBChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.cassandra import (
        CassandraChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.cosmos_db import (
        CosmosDBChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.dynamodb import (
        DynamoDBChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.elasticsearch import (
        ElasticsearchChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.file import (
        FileChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.firestore import (
        FirestoreChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.in_memory import (
        ChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.kafka import (
        KafkaChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.momento import (
        MomentoChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.mongodb import (
        MongoDBChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.neo4j import (
        Neo4jChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.postgres import (
        PostgresChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.redis import (
        RedisChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.rocksetdb import (
        RocksetChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.singlestoredb import (
        SingleStoreDBChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.sql import (
        SQLChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.streamlit import (
        StreamlitChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.tidb import (
        TiDBChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.upstash_redis import (
        UpstashRedisChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.xata import (
        XataChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.zep import (
        ZepChatMessageHistory,
    )
    from aiagentsforce_community.chat_message_histories.zep_cloud import (
        ZepCloudChatMessageHistory,
    )

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
    "SQLChatMessageHistory",
    "SingleStoreDBChatMessageHistory",
    "StreamlitChatMessageHistory",
    "TiDBChatMessageHistory",
    "UpstashRedisChatMessageHistory",
    "XataChatMessageHistory",
    "ZepChatMessageHistory",
    "ZepCloudChatMessageHistory",
    "KafkaChatMessageHistory",
]

_module_lookup = {
    "AstraDBChatMessageHistory": "aiagentsforce_community.chat_message_histories.astradb",
    "CassandraChatMessageHistory": "aiagentsforce_community.chat_message_histories.cassandra",  # noqa: E501
    "ChatMessageHistory": "aiagentsforce_community.chat_message_histories.in_memory",
    "CosmosDBChatMessageHistory": "aiagentsforce_community.chat_message_histories.cosmos_db",  # noqa: E501
    "DynamoDBChatMessageHistory": "aiagentsforce_community.chat_message_histories.dynamodb",
    "ElasticsearchChatMessageHistory": "aiagentsforce_community.chat_message_histories.elasticsearch",  # noqa: E501
    "FileChatMessageHistory": "aiagentsforce_community.chat_message_histories.file",
    "FirestoreChatMessageHistory": "aiagentsforce_community.chat_message_histories.firestore",  # noqa: E501
    "MomentoChatMessageHistory": "aiagentsforce_community.chat_message_histories.momento",
    "MongoDBChatMessageHistory": "aiagentsforce_community.chat_message_histories.mongodb",
    "Neo4jChatMessageHistory": "aiagentsforce_community.chat_message_histories.neo4j",
    "PostgresChatMessageHistory": "aiagentsforce_community.chat_message_histories.postgres",
    "RedisChatMessageHistory": "aiagentsforce_community.chat_message_histories.redis",
    "RocksetChatMessageHistory": "aiagentsforce_community.chat_message_histories.rocksetdb",
    "SQLChatMessageHistory": "aiagentsforce_community.chat_message_histories.sql",
    "SingleStoreDBChatMessageHistory": "aiagentsforce_community.chat_message_histories.singlestoredb",  # noqa: E501
    "StreamlitChatMessageHistory": "aiagentsforce_community.chat_message_histories.streamlit",  # noqa: E501
    "TiDBChatMessageHistory": "aiagentsforce_community.chat_message_histories.tidb",
    "UpstashRedisChatMessageHistory": "aiagentsforce_community.chat_message_histories.upstash_redis",  # noqa: E501
    "XataChatMessageHistory": "aiagentsforce_community.chat_message_histories.xata",
    "ZepChatMessageHistory": "aiagentsforce_community.chat_message_histories.zep",
    "ZepCloudChatMessageHistory": "aiagentsforce_community.chat_message_histories.zep_cloud",  # noqa: E501
    "KafkaChatMessageHistory": "aiagentsforce_community.chat_message_histories.kafka",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
