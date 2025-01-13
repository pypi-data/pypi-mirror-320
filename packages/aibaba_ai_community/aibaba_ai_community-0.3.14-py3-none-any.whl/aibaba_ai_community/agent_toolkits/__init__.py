"""**Toolkits** are sets of tools that can be used to interact with
various services and APIs.
"""

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiagentsforce_community.agent_toolkits.ainetwork.toolkit import (
        AINetworkToolkit,
    )
    from aiagentsforce_community.agent_toolkits.amadeus.toolkit import (
        AmadeusToolkit,
    )
    from aiagentsforce_community.agent_toolkits.azure_ai_services import (
        AzureAiServicesToolkit,
    )
    from aiagentsforce_community.agent_toolkits.azure_cognitive_services import (
        AzureCognitiveServicesToolkit,
    )
    from aiagentsforce_community.agent_toolkits.cassandra_database.toolkit import (
        CassandraDatabaseToolkit,  # noqa: F401
    )
    from aiagentsforce_community.agent_toolkits.cogniswitch.toolkit import (
        CogniswitchToolkit,
    )
    from aiagentsforce_community.agent_toolkits.connery import (
        ConneryToolkit,
    )
    from aiagentsforce_community.agent_toolkits.file_management.toolkit import (
        FileManagementToolkit,
    )
    from aiagentsforce_community.agent_toolkits.gmail.toolkit import (
        GmailToolkit,
    )
    from aiagentsforce_community.agent_toolkits.jira.toolkit import (
        JiraToolkit,
    )
    from aiagentsforce_community.agent_toolkits.json.base import (
        create_json_agent,
    )
    from aiagentsforce_community.agent_toolkits.json.toolkit import (
        JsonToolkit,
    )
    from aiagentsforce_community.agent_toolkits.multion.toolkit import (
        MultionToolkit,
    )
    from aiagentsforce_community.agent_toolkits.nasa.toolkit import (
        NasaToolkit,
    )
    from aiagentsforce_community.agent_toolkits.nla.toolkit import (
        NLAToolkit,
    )
    from aiagentsforce_community.agent_toolkits.office365.toolkit import (
        O365Toolkit,
    )
    from aiagentsforce_community.agent_toolkits.openapi.base import (
        create_openapi_agent,
    )
    from aiagentsforce_community.agent_toolkits.openapi.toolkit import (
        OpenAPIToolkit,
    )
    from aiagentsforce_community.agent_toolkits.playwright.toolkit import (
        PlayWrightBrowserToolkit,
    )
    from aiagentsforce_community.agent_toolkits.polygon.toolkit import (
        PolygonToolkit,
    )
    from aiagentsforce_community.agent_toolkits.powerbi.base import (
        create_pbi_agent,
    )
    from aiagentsforce_community.agent_toolkits.powerbi.chat_base import (
        create_pbi_chat_agent,
    )
    from aiagentsforce_community.agent_toolkits.powerbi.toolkit import (
        PowerBIToolkit,
    )
    from aiagentsforce_community.agent_toolkits.slack.toolkit import (
        SlackToolkit,
    )
    from aiagentsforce_community.agent_toolkits.spark_sql.base import (
        create_spark_sql_agent,
    )
    from aiagentsforce_community.agent_toolkits.spark_sql.toolkit import (
        SparkSQLToolkit,
    )
    from aiagentsforce_community.agent_toolkits.sql.base import (
        create_sql_agent,
    )
    from aiagentsforce_community.agent_toolkits.sql.toolkit import (
        SQLDatabaseToolkit,
    )
    from aiagentsforce_community.agent_toolkits.steam.toolkit import (
        SteamToolkit,
    )
    from aiagentsforce_community.agent_toolkits.zapier.toolkit import (
        ZapierToolkit,
    )

__all__ = [
    "AINetworkToolkit",
    "AmadeusToolkit",
    "AzureAiServicesToolkit",
    "AzureCognitiveServicesToolkit",
    "CogniswitchToolkit",
    "ConneryToolkit",
    "FileManagementToolkit",
    "GmailToolkit",
    "JiraToolkit",
    "JsonToolkit",
    "MultionToolkit",
    "NLAToolkit",
    "NasaToolkit",
    "O365Toolkit",
    "OpenAPIToolkit",
    "PlayWrightBrowserToolkit",
    "PolygonToolkit",
    "PowerBIToolkit",
    "SQLDatabaseToolkit",
    "SlackToolkit",
    "SparkSQLToolkit",
    "SteamToolkit",
    "ZapierToolkit",
    "create_json_agent",
    "create_openapi_agent",
    "create_pbi_agent",
    "create_pbi_chat_agent",
    "create_spark_sql_agent",
    "create_sql_agent",
]


_module_lookup = {
    "AINetworkToolkit": "aiagentsforce_community.agent_toolkits.ainetwork.toolkit",
    "AmadeusToolkit": "aiagentsforce_community.agent_toolkits.amadeus.toolkit",
    "AzureAiServicesToolkit": "aiagentsforce_community.agent_toolkits.azure_ai_services",
    "AzureCognitiveServicesToolkit": "aiagentsforce_community.agent_toolkits.azure_cognitive_services",  # noqa: E501
    "CogniswitchToolkit": "aiagentsforce_community.agent_toolkits.cogniswitch.toolkit",
    "ConneryToolkit": "aiagentsforce_community.agent_toolkits.connery",
    "FileManagementToolkit": "aiagentsforce_community.agent_toolkits.file_management.toolkit",  # noqa: E501
    "GmailToolkit": "aiagentsforce_community.agent_toolkits.gmail.toolkit",
    "JiraToolkit": "aiagentsforce_community.agent_toolkits.jira.toolkit",
    "JsonToolkit": "aiagentsforce_community.agent_toolkits.json.toolkit",
    "MultionToolkit": "aiagentsforce_community.agent_toolkits.multion.toolkit",
    "NLAToolkit": "aiagentsforce_community.agent_toolkits.nla.toolkit",
    "NasaToolkit": "aiagentsforce_community.agent_toolkits.nasa.toolkit",
    "O365Toolkit": "aiagentsforce_community.agent_toolkits.office365.toolkit",
    "OpenAPIToolkit": "aiagentsforce_community.agent_toolkits.openapi.toolkit",
    "PlayWrightBrowserToolkit": "aiagentsforce_community.agent_toolkits.playwright.toolkit",
    "PolygonToolkit": "aiagentsforce_community.agent_toolkits.polygon.toolkit",
    "PowerBIToolkit": "aiagentsforce_community.agent_toolkits.powerbi.toolkit",
    "SQLDatabaseToolkit": "aiagentsforce_community.agent_toolkits.sql.toolkit",
    "SlackToolkit": "aiagentsforce_community.agent_toolkits.slack.toolkit",
    "SparkSQLToolkit": "aiagentsforce_community.agent_toolkits.spark_sql.toolkit",
    "SteamToolkit": "aiagentsforce_community.agent_toolkits.steam.toolkit",
    "ZapierToolkit": "aiagentsforce_community.agent_toolkits.zapier.toolkit",
    "create_json_agent": "aiagentsforce_community.agent_toolkits.json.base",
    "create_openapi_agent": "aiagentsforce_community.agent_toolkits.openapi.base",
    "create_pbi_agent": "aiagentsforce_community.agent_toolkits.powerbi.base",
    "create_pbi_chat_agent": "aiagentsforce_community.agent_toolkits.powerbi.chat_base",
    "create_spark_sql_agent": "aiagentsforce_community.agent_toolkits.spark_sql.base",
    "create_sql_agent": "aiagentsforce_community.agent_toolkits.sql.base",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
