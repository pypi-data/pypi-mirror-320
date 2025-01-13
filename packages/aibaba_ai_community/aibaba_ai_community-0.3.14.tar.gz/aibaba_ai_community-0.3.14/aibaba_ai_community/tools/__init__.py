"""**Tools** are classes that an Agent uses to interact with the world.

Each tool has a **description**. Agent uses the description to choose the right
tool for the job.

**Class hierarchy:**

.. code-block::

    ToolMetaclass --> BaseTool --> <name>Tool  # Examples: AIPluginTool, BaseGraphQLTool
                                   <name>      # Examples: BraveSearch, HumanInputRun

**Main helpers:**

.. code-block::

    CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
"""

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from alibaba_ai_core.tools import (
        BaseTool as BaseTool,
    )
    from alibaba_ai_core.tools import (
        StructuredTool as StructuredTool,
    )
    from alibaba_ai_core.tools import (
        Tool as Tool,
    )
    from alibaba_ai_core.tools.convert import tool as tool

    from aiagentsforce_community.tools.ainetwork.app import (
        AINAppOps,
    )
    from aiagentsforce_community.tools.ainetwork.owner import (
        AINOwnerOps,
    )
    from aiagentsforce_community.tools.ainetwork.rule import (
        AINRuleOps,
    )
    from aiagentsforce_community.tools.ainetwork.transfer import (
        AINTransfer,
    )
    from aiagentsforce_community.tools.ainetwork.value import (
        AINValueOps,
    )
    from aiagentsforce_community.tools.arxiv.tool import (
        ArxivQueryRun,
    )
    from aiagentsforce_community.tools.asknews.tool import (
        AskNewsSearch,
    )
    from aiagentsforce_community.tools.azure_ai_services import (
        AzureAiServicesDocumentIntelligenceTool,
        AzureAiServicesImageAnalysisTool,
        AzureAiServicesSpeechToTextTool,
        AzureAiServicesTextAnalyticsForHealthTool,
        AzureAiServicesTextToSpeechTool,
    )
    from aiagentsforce_community.tools.azure_cognitive_services import (
        AzureCogsFormRecognizerTool,
        AzureCogsImageAnalysisTool,
        AzureCogsSpeech2TextTool,
        AzureCogsText2SpeechTool,
        AzureCogsTextAnalyticsHealthTool,
    )
    from aiagentsforce_community.tools.bearly.tool import (
        BearlyInterpreterTool,
    )
    from aiagentsforce_community.tools.bing_search.tool import (
        BingSearchResults,
        BingSearchRun,
    )
    from aiagentsforce_community.tools.brave_search.tool import (
        BraveSearch,
    )
    from aiagentsforce_community.tools.cassandra_database.tool import (
        GetSchemaCassandraDatabaseTool,  # noqa: F401
        GetTableDataCassandraDatabaseTool,  # noqa: F401
        QueryCassandraDatabaseTool,  # noqa: F401
    )
    from aiagentsforce_community.tools.cogniswitch.tool import (
        CogniswitchKnowledgeRequest,
        CogniswitchKnowledgeSourceFile,
        CogniswitchKnowledgeSourceURL,
        CogniswitchKnowledgeStatus,
    )
    from aiagentsforce_community.tools.connery import (
        ConneryAction,
    )
    from aiagentsforce_community.tools.convert_to_openai import (
        format_tool_to_openai_function,
    )
    from aiagentsforce_community.tools.dataherald import DataheraldTextToSQL
    from aiagentsforce_community.tools.ddg_search.tool import (
        DuckDuckGoSearchResults,
        DuckDuckGoSearchRun,
    )
    from aiagentsforce_community.tools.e2b_data_analysis.tool import (
        E2BDataAnalysisTool,
    )
    from aiagentsforce_community.tools.edenai import (
        EdenAiExplicitImageTool,
        EdenAiObjectDetectionTool,
        EdenAiParsingIDTool,
        EdenAiParsingInvoiceTool,
        EdenAiSpeechToTextTool,
        EdenAiTextModerationTool,
        EdenAiTextToSpeechTool,
        EdenaiTool,
    )
    from aiagentsforce_community.tools.eleven_labs.text2speech import (
        ElevenLabsText2SpeechTool,
    )
    from aiagentsforce_community.tools.file_management import (
        CopyFileTool,
        DeleteFileTool,
        FileSearchTool,
        ListDirectoryTool,
        MoveFileTool,
        ReadFileTool,
        WriteFileTool,
    )
    from aiagentsforce_community.tools.financial_datasets.balance_sheets import (
        BalanceSheets,
    )
    from aiagentsforce_community.tools.financial_datasets.cash_flow_statements import (
        CashFlowStatements,
    )
    from aiagentsforce_community.tools.financial_datasets.income_statements import (
        IncomeStatements,
    )
    from aiagentsforce_community.tools.gmail import (
        GmailCreateDraft,
        GmailGetMessage,
        GmailGetThread,
        GmailSearch,
        GmailSendMessage,
    )
    from aiagentsforce_community.tools.google_books import (
        GoogleBooksQueryRun,
    )
    from aiagentsforce_community.tools.google_cloud.texttospeech import (
        GoogleCloudTextToSpeechTool,
    )
    from aiagentsforce_community.tools.google_places.tool import (
        GooglePlacesTool,
    )
    from aiagentsforce_community.tools.google_search.tool import (
        GoogleSearchResults,
        GoogleSearchRun,
    )
    from aiagentsforce_community.tools.google_serper.tool import (
        GoogleSerperResults,
        GoogleSerperRun,
    )
    from aiagentsforce_community.tools.graphql.tool import (
        BaseGraphQLTool,
    )
    from aiagentsforce_community.tools.human.tool import (
        HumanInputRun,
    )
    from aiagentsforce_community.tools.ifttt import (
        IFTTTWebhook,
    )
    from aiagentsforce_community.tools.interaction.tool import (
        StdInInquireTool,
    )
    from aiagentsforce_community.tools.jina_search.tool import JinaSearch
    from aiagentsforce_community.tools.jira.tool import (
        JiraAction,
    )
    from aiagentsforce_community.tools.json.tool import (
        JsonGetValueTool,
        JsonListKeysTool,
    )
    from aiagentsforce_community.tools.merriam_webster.tool import (
        MerriamWebsterQueryRun,
    )
    from aiagentsforce_community.tools.metaphor_search import (
        MetaphorSearchResults,
    )
    from aiagentsforce_community.tools.mojeek_search.tool import (
        MojeekSearch,
    )
    from aiagentsforce_community.tools.nasa.tool import (
        NasaAction,
    )
    from aiagentsforce_community.tools.office365.create_draft_message import (
        O365CreateDraftMessage,
    )
    from aiagentsforce_community.tools.office365.events_search import (
        O365SearchEvents,
    )
    from aiagentsforce_community.tools.office365.messages_search import (
        O365SearchEmails,
    )
    from aiagentsforce_community.tools.office365.send_event import (
        O365SendEvent,
    )
    from aiagentsforce_community.tools.office365.send_message import (
        O365SendMessage,
    )
    from aiagentsforce_community.tools.office365.utils import (
        authenticate,
    )
    from aiagentsforce_community.tools.openapi.utils.api_models import (
        APIOperation,
    )
    from aiagentsforce_community.tools.openapi.utils.openapi_utils import (
        OpenAPISpec,
    )
    from aiagentsforce_community.tools.openweathermap.tool import (
        OpenWeatherMapQueryRun,
    )
    from aiagentsforce_community.tools.playwright import (
        ClickTool,
        CurrentWebPageTool,
        ExtractHyperlinksTool,
        ExtractTextTool,
        GetElementsTool,
        NavigateBackTool,
        NavigateTool,
    )
    from aiagentsforce_community.tools.plugin import (
        AIPluginTool,
    )
    from aiagentsforce_community.tools.polygon.aggregates import (
        PolygonAggregates,
    )
    from aiagentsforce_community.tools.polygon.financials import (
        PolygonFinancials,
    )
    from aiagentsforce_community.tools.polygon.last_quote import (
        PolygonLastQuote,
    )
    from aiagentsforce_community.tools.polygon.ticker_news import (
        PolygonTickerNews,
    )
    from aiagentsforce_community.tools.powerbi.tool import (
        InfoPowerBITool,
        ListPowerBITool,
        QueryPowerBITool,
    )
    from aiagentsforce_community.tools.pubmed.tool import (
        PubmedQueryRun,
    )
    from aiagentsforce_community.tools.reddit_search.tool import (
        RedditSearchRun,
        RedditSearchSchema,
    )
    from aiagentsforce_community.tools.requests.tool import (
        BaseRequestsTool,
        RequestsDeleteTool,
        RequestsGetTool,
        RequestsPatchTool,
        RequestsPostTool,
        RequestsPutTool,
    )
    from aiagentsforce_community.tools.scenexplain.tool import (
        SceneXplainTool,
    )
    from aiagentsforce_community.tools.searchapi.tool import (
        SearchAPIResults,
        SearchAPIRun,
    )
    from aiagentsforce_community.tools.searx_search.tool import (
        SearxSearchResults,
        SearxSearchRun,
    )
    from aiagentsforce_community.tools.shell.tool import (
        ShellTool,
    )
    from aiagentsforce_community.tools.slack.get_channel import (
        SlackGetChannel,
    )
    from aiagentsforce_community.tools.slack.get_message import (
        SlackGetMessage,
    )
    from aiagentsforce_community.tools.slack.schedule_message import (
        SlackScheduleMessage,
    )
    from aiagentsforce_community.tools.slack.send_message import (
        SlackSendMessage,
    )
    from aiagentsforce_community.tools.sleep.tool import (
        SleepTool,
    )
    from aiagentsforce_community.tools.spark_sql.tool import (
        BaseSparkSQLTool,
        InfoSparkSQLTool,
        ListSparkSQLTool,
        QueryCheckerTool,
        QuerySparkSQLTool,
    )
    from aiagentsforce_community.tools.sql_database.tool import (
        BaseSQLDatabaseTool,
        InfoSQLDatabaseTool,
        ListSQLDatabaseTool,
        QuerySQLCheckerTool,
        QuerySQLDataBaseTool,
        QuerySQLDatabaseTool,
    )
    from aiagentsforce_community.tools.stackexchange.tool import (
        StackExchangeTool,
    )
    from aiagentsforce_community.tools.steam.tool import (
        SteamWebAPIQueryRun,
    )
    from aiagentsforce_community.tools.steamship_image_generation import (
        SteamshipImageGenerationTool,
    )
    from aiagentsforce_community.tools.tavily_search import (
        TavilyAnswer,
        TavilySearchResults,
    )
    from aiagentsforce_community.tools.vectorstore.tool import (
        VectorStoreQATool,
        VectorStoreQAWithSourcesTool,
    )
    from aiagentsforce_community.tools.wikipedia.tool import (
        WikipediaQueryRun,
    )
    from aiagentsforce_community.tools.wolfram_alpha.tool import (
        WolframAlphaQueryRun,
    )
    from aiagentsforce_community.tools.yahoo_finance_news import (
        YahooFinanceNewsTool,
    )
    from aiagentsforce_community.tools.you.tool import (
        YouSearchTool,
    )
    from aiagentsforce_community.tools.youtube.search import (
        YouTubeSearchTool,
    )
    from aiagentsforce_community.tools.zapier.tool import (
        ZapierNLAListActions,
        ZapierNLARunAction,
    )
    from aiagentsforce_community.tools.zenguard.tool import (
        Detector,
        ZenGuardInput,
        ZenGuardTool,
    )

__all__ = [
    "BaseTool",
    "Tool",
    "tool",
    "StructuredTool",
    "AINAppOps",
    "AINOwnerOps",
    "AINRuleOps",
    "AINTransfer",
    "AINValueOps",
    "AIPluginTool",
    "APIOperation",
    "ArxivQueryRun",
    "AskNewsSearch",
    "AzureAiServicesDocumentIntelligenceTool",
    "AzureAiServicesImageAnalysisTool",
    "AzureAiServicesSpeechToTextTool",
    "AzureAiServicesTextAnalyticsForHealthTool",
    "AzureAiServicesTextToSpeechTool",
    "AzureCogsFormRecognizerTool",
    "AzureCogsImageAnalysisTool",
    "AzureCogsSpeech2TextTool",
    "AzureCogsText2SpeechTool",
    "AzureCogsTextAnalyticsHealthTool",
    "BalanceSheets",
    "BaseGraphQLTool",
    "BaseRequestsTool",
    "BaseSQLDatabaseTool",
    "BaseSparkSQLTool",
    "BearlyInterpreterTool",
    "BingSearchResults",
    "BingSearchRun",
    "BraveSearch",
    "CashFlowStatements",
    "ClickTool",
    "CogniswitchKnowledgeRequest",
    "CogniswitchKnowledgeSourceFile",
    "CogniswitchKnowledgeSourceURL",
    "CogniswitchKnowledgeStatus",
    "ConneryAction",
    "CopyFileTool",
    "CurrentWebPageTool",
    "DeleteFileTool",
    "DataheraldTextToSQL",
    "DuckDuckGoSearchResults",
    "DuckDuckGoSearchRun",
    "E2BDataAnalysisTool",
    "EdenAiExplicitImageTool",
    "EdenAiObjectDetectionTool",
    "EdenAiParsingIDTool",
    "EdenAiParsingInvoiceTool",
    "EdenAiSpeechToTextTool",
    "EdenAiTextModerationTool",
    "EdenAiTextToSpeechTool",
    "EdenaiTool",
    "ElevenLabsText2SpeechTool",
    "ExtractHyperlinksTool",
    "ExtractTextTool",
    "FileSearchTool",
    "GetElementsTool",
    "GmailCreateDraft",
    "GmailGetMessage",
    "GmailGetThread",
    "GmailSearch",
    "GmailSendMessage",
    "GoogleBooksQueryRun",
    "GoogleCloudTextToSpeechTool",
    "GooglePlacesTool",
    "GoogleSearchResults",
    "GoogleSearchRun",
    "GoogleSerperResults",
    "GoogleSerperRun",
    "HumanInputRun",
    "IFTTTWebhook",
    "IncomeStatements",
    "InfoPowerBITool",
    "InfoSQLDatabaseTool",
    "InfoSparkSQLTool",
    "JiraAction",
    "JinaSearch",
    "JsonGetValueTool",
    "JsonListKeysTool",
    "ListDirectoryTool",
    "ListPowerBITool",
    "ListSQLDatabaseTool",
    "ListSparkSQLTool",
    "MerriamWebsterQueryRun",
    "MetaphorSearchResults",
    "MojeekSearch",
    "MoveFileTool",
    "NasaAction",
    "NavigateBackTool",
    "NavigateTool",
    "O365CreateDraftMessage",
    "O365SearchEmails",
    "O365SearchEvents",
    "O365SendEvent",
    "O365SendMessage",
    "OpenAPISpec",
    "OpenWeatherMapQueryRun",
    "PolygonAggregates",
    "PolygonFinancials",
    "PolygonLastQuote",
    "PolygonTickerNews",
    "PubmedQueryRun",
    "QueryCheckerTool",
    "QueryPowerBITool",
    "QuerySQLCheckerTool",
    "QuerySQLDatabaseTool",
    "QuerySQLDataBaseTool",  # Legacy, kept for backwards compatibility.
    "QuerySparkSQLTool",
    "ReadFileTool",
    "RedditSearchRun",
    "RedditSearchSchema",
    "RequestsDeleteTool",
    "RequestsGetTool",
    "RequestsPatchTool",
    "RequestsPostTool",
    "RequestsPutTool",
    "SceneXplainTool",
    "SearchAPIResults",
    "SearchAPIRun",
    "SearxSearchResults",
    "SearxSearchRun",
    "ShellTool",
    "SlackGetChannel",
    "SlackGetMessage",
    "SlackScheduleMessage",
    "SlackSendMessage",
    "SleepTool",
    "StackExchangeTool",
    "StdInInquireTool",
    "SteamWebAPIQueryRun",
    "SteamshipImageGenerationTool",
    "TavilyAnswer",
    "TavilySearchResults",
    "VectorStoreQATool",
    "VectorStoreQAWithSourcesTool",
    "WikipediaQueryRun",
    "WolframAlphaQueryRun",
    "WriteFileTool",
    "YahooFinanceNewsTool",
    "YouSearchTool",
    "YouTubeSearchTool",
    "ZapierNLAListActions",
    "ZapierNLARunAction",
    "Detector",
    "ZenGuardInput",
    "ZenGuardTool",
    "authenticate",
    "format_tool_to_openai_function",
]

# Used for internal purposes
_DEPRECATED_TOOLS = {"PythonAstREPLTool", "PythonREPLTool"}

_module_lookup = {
    "AINAppOps": "aiagentsforce_community.tools.ainetwork.app",
    "AINOwnerOps": "aiagentsforce_community.tools.ainetwork.owner",
    "AINRuleOps": "aiagentsforce_community.tools.ainetwork.rule",
    "AINTransfer": "aiagentsforce_community.tools.ainetwork.transfer",
    "AINValueOps": "aiagentsforce_community.tools.ainetwork.value",
    "AIPluginTool": "aiagentsforce_community.tools.plugin",
    "APIOperation": "aiagentsforce_community.tools.openapi.utils.api_models",
    "ArxivQueryRun": "aiagentsforce_community.tools.arxiv.tool",
    "AskNewsSearch": "aiagentsforce_community.tools.asknews.tool",
    "AzureAiServicesDocumentIntelligenceTool": "aiagentsforce_community.tools.azure_ai_services",  # noqa: E501
    "AzureAiServicesImageAnalysisTool": "aiagentsforce_community.tools.azure_ai_services",
    "AzureAiServicesSpeechToTextTool": "aiagentsforce_community.tools.azure_ai_services",
    "AzureAiServicesTextToSpeechTool": "aiagentsforce_community.tools.azure_ai_services",
    "AzureAiServicesTextAnalyticsForHealthTool": "aiagentsforce_community.tools.azure_ai_services",  # noqa: E501
    "AzureCogsFormRecognizerTool": "aiagentsforce_community.tools.azure_cognitive_services",
    "AzureCogsImageAnalysisTool": "aiagentsforce_community.tools.azure_cognitive_services",
    "AzureCogsSpeech2TextTool": "aiagentsforce_community.tools.azure_cognitive_services",
    "AzureCogsText2SpeechTool": "aiagentsforce_community.tools.azure_cognitive_services",
    "AzureCogsTextAnalyticsHealthTool": "aiagentsforce_community.tools.azure_cognitive_services",  # noqa: E501
    "BalanceSheets": "aiagentsforce_community.tools.financial_datasets.balance_sheets",
    "BaseGraphQLTool": "aiagentsforce_community.tools.graphql.tool",
    "BaseRequestsTool": "aiagentsforce_community.tools.requests.tool",
    "BaseSQLDatabaseTool": "aiagentsforce_community.tools.sql_database.tool",
    "BaseSparkSQLTool": "aiagentsforce_community.tools.spark_sql.tool",
    "BaseTool": "alibaba_ai_core.tools",
    "BearlyInterpreterTool": "aiagentsforce_community.tools.bearly.tool",
    "BingSearchResults": "aiagentsforce_community.tools.bing_search.tool",
    "BingSearchRun": "aiagentsforce_community.tools.bing_search.tool",
    "BraveSearch": "aiagentsforce_community.tools.brave_search.tool",
    "CashFlowStatements": "aiagentsforce_community.tools.financial_datasets.cash_flow_statements",  # noqa: E501
    "ClickTool": "aiagentsforce_community.tools.playwright",
    "CogniswitchKnowledgeRequest": "aiagentsforce_community.tools.cogniswitch.tool",
    "CogniswitchKnowledgeSourceFile": "aiagentsforce_community.tools.cogniswitch.tool",
    "CogniswitchKnowledgeSourceURL": "aiagentsforce_community.tools.cogniswitch.tool",
    "CogniswitchKnowledgeStatus": "aiagentsforce_community.tools.cogniswitch.tool",
    "ConneryAction": "aiagentsforce_community.tools.connery",
    "CopyFileTool": "aiagentsforce_community.tools.file_management",
    "CurrentWebPageTool": "aiagentsforce_community.tools.playwright",
    "DataheraldTextToSQL": "aiagentsforce_community.tools.dataherald.tool",
    "DeleteFileTool": "aiagentsforce_community.tools.file_management",
    "Detector": "aiagentsforce_community.tools.zenguard.tool",
    "DuckDuckGoSearchResults": "aiagentsforce_community.tools.ddg_search.tool",
    "DuckDuckGoSearchRun": "aiagentsforce_community.tools.ddg_search.tool",
    "E2BDataAnalysisTool": "aiagentsforce_community.tools.e2b_data_analysis.tool",
    "EdenAiExplicitImageTool": "aiagentsforce_community.tools.edenai",
    "EdenAiObjectDetectionTool": "aiagentsforce_community.tools.edenai",
    "EdenAiParsingIDTool": "aiagentsforce_community.tools.edenai",
    "EdenAiParsingInvoiceTool": "aiagentsforce_community.tools.edenai",
    "EdenAiSpeechToTextTool": "aiagentsforce_community.tools.edenai",
    "EdenAiTextModerationTool": "aiagentsforce_community.tools.edenai",
    "EdenAiTextToSpeechTool": "aiagentsforce_community.tools.edenai",
    "EdenaiTool": "aiagentsforce_community.tools.edenai",
    "ElevenLabsText2SpeechTool": "aiagentsforce_community.tools.eleven_labs.text2speech",
    "ExtractHyperlinksTool": "aiagentsforce_community.tools.playwright",
    "ExtractTextTool": "aiagentsforce_community.tools.playwright",
    "FileSearchTool": "aiagentsforce_community.tools.file_management",
    "GetElementsTool": "aiagentsforce_community.tools.playwright",
    "GmailCreateDraft": "aiagentsforce_community.tools.gmail",
    "GmailGetMessage": "aiagentsforce_community.tools.gmail",
    "GmailGetThread": "aiagentsforce_community.tools.gmail",
    "GmailSearch": "aiagentsforce_community.tools.gmail",
    "GmailSendMessage": "aiagentsforce_community.tools.gmail",
    "GoogleBooksQueryRun": "aiagentsforce_community.tools.google_books",
    "GoogleCloudTextToSpeechTool": "aiagentsforce_community.tools.google_cloud.texttospeech",  # noqa: E501
    "GooglePlacesTool": "aiagentsforce_community.tools.google_places.tool",
    "GoogleSearchResults": "aiagentsforce_community.tools.google_search.tool",
    "GoogleSearchRun": "aiagentsforce_community.tools.google_search.tool",
    "GoogleSerperResults": "aiagentsforce_community.tools.google_serper.tool",
    "GoogleSerperRun": "aiagentsforce_community.tools.google_serper.tool",
    "HumanInputRun": "aiagentsforce_community.tools.human.tool",
    "IFTTTWebhook": "aiagentsforce_community.tools.ifttt",
    "IncomeStatements": "aiagentsforce_community.tools.financial_datasets.income_statements",  # noqa: E501
    "InfoPowerBITool": "aiagentsforce_community.tools.powerbi.tool",
    "InfoSQLDatabaseTool": "aiagentsforce_community.tools.sql_database.tool",
    "InfoSparkSQLTool": "aiagentsforce_community.tools.spark_sql.tool",
    "JiraAction": "aiagentsforce_community.tools.jira.tool",
    "JinaSearch": "aiagentsforce_community.tools.jina_search.tool",
    "JsonGetValueTool": "aiagentsforce_community.tools.json.tool",
    "JsonListKeysTool": "aiagentsforce_community.tools.json.tool",
    "ListDirectoryTool": "aiagentsforce_community.tools.file_management",
    "ListPowerBITool": "aiagentsforce_community.tools.powerbi.tool",
    "ListSQLDatabaseTool": "aiagentsforce_community.tools.sql_database.tool",
    "ListSparkSQLTool": "aiagentsforce_community.tools.spark_sql.tool",
    "MerriamWebsterQueryRun": "aiagentsforce_community.tools.merriam_webster.tool",
    "MetaphorSearchResults": "aiagentsforce_community.tools.metaphor_search",
    "MojeekSearch": "aiagentsforce_community.tools.mojeek_search.tool",
    "MoveFileTool": "aiagentsforce_community.tools.file_management",
    "NasaAction": "aiagentsforce_community.tools.nasa.tool",
    "NavigateBackTool": "aiagentsforce_community.tools.playwright",
    "NavigateTool": "aiagentsforce_community.tools.playwright",
    "O365CreateDraftMessage": "aiagentsforce_community.tools.office365.create_draft_message",  # noqa: E501
    "O365SearchEmails": "aiagentsforce_community.tools.office365.messages_search",
    "O365SearchEvents": "aiagentsforce_community.tools.office365.events_search",
    "O365SendEvent": "aiagentsforce_community.tools.office365.send_event",
    "O365SendMessage": "aiagentsforce_community.tools.office365.send_message",
    "OpenAPISpec": "aiagentsforce_community.tools.openapi.utils.openapi_utils",
    "OpenWeatherMapQueryRun": "aiagentsforce_community.tools.openweathermap.tool",
    "PolygonAggregates": "aiagentsforce_community.tools.polygon.aggregates",
    "PolygonFinancials": "aiagentsforce_community.tools.polygon.financials",
    "PolygonLastQuote": "aiagentsforce_community.tools.polygon.last_quote",
    "PolygonTickerNews": "aiagentsforce_community.tools.polygon.ticker_news",
    "PubmedQueryRun": "aiagentsforce_community.tools.pubmed.tool",
    "QueryCheckerTool": "aiagentsforce_community.tools.spark_sql.tool",
    "QueryPowerBITool": "aiagentsforce_community.tools.powerbi.tool",
    "QuerySQLCheckerTool": "aiagentsforce_community.tools.sql_database.tool",
    "QuerySQLDatabaseTool": "aiagentsforce_community.tools.sql_database.tool",
    # Legacy, kept for backwards compatibility.
    "QuerySQLDataBaseTool": "aiagentsforce_community.tools.sql_database.tool",
    "QuerySparkSQLTool": "aiagentsforce_community.tools.spark_sql.tool",
    "ReadFileTool": "aiagentsforce_community.tools.file_management",
    "RedditSearchRun": "aiagentsforce_community.tools.reddit_search.tool",
    "RedditSearchSchema": "aiagentsforce_community.tools.reddit_search.tool",
    "RequestsDeleteTool": "aiagentsforce_community.tools.requests.tool",
    "RequestsGetTool": "aiagentsforce_community.tools.requests.tool",
    "RequestsPatchTool": "aiagentsforce_community.tools.requests.tool",
    "RequestsPostTool": "aiagentsforce_community.tools.requests.tool",
    "RequestsPutTool": "aiagentsforce_community.tools.requests.tool",
    "SceneXplainTool": "aiagentsforce_community.tools.scenexplain.tool",
    "SearchAPIResults": "aiagentsforce_community.tools.searchapi.tool",
    "SearchAPIRun": "aiagentsforce_community.tools.searchapi.tool",
    "SearxSearchResults": "aiagentsforce_community.tools.searx_search.tool",
    "SearxSearchRun": "aiagentsforce_community.tools.searx_search.tool",
    "ShellTool": "aiagentsforce_community.tools.shell.tool",
    "SlackGetChannel": "aiagentsforce_community.tools.slack.get_channel",
    "SlackGetMessage": "aiagentsforce_community.tools.slack.get_message",
    "SlackScheduleMessage": "aiagentsforce_community.tools.slack.schedule_message",
    "SlackSendMessage": "aiagentsforce_community.tools.slack.send_message",
    "SleepTool": "aiagentsforce_community.tools.sleep.tool",
    "StackExchangeTool": "aiagentsforce_community.tools.stackexchange.tool",
    "StdInInquireTool": "aiagentsforce_community.tools.interaction.tool",
    "SteamWebAPIQueryRun": "aiagentsforce_community.tools.steam.tool",
    "SteamshipImageGenerationTool": "aiagentsforce_community.tools.steamship_image_generation",  # noqa: E501
    "StructuredTool": "alibaba_ai_core.tools",
    "TavilyAnswer": "aiagentsforce_community.tools.tavily_search",
    "TavilySearchResults": "aiagentsforce_community.tools.tavily_search",
    "Tool": "alibaba_ai_core.tools",
    "VectorStoreQATool": "aiagentsforce_community.tools.vectorstore.tool",
    "VectorStoreQAWithSourcesTool": "aiagentsforce_community.tools.vectorstore.tool",
    "WikipediaQueryRun": "aiagentsforce_community.tools.wikipedia.tool",
    "WolframAlphaQueryRun": "aiagentsforce_community.tools.wolfram_alpha.tool",
    "WriteFileTool": "aiagentsforce_community.tools.file_management",
    "YahooFinanceNewsTool": "aiagentsforce_community.tools.yahoo_finance_news",
    "YouSearchTool": "aiagentsforce_community.tools.you.tool",
    "YouTubeSearchTool": "aiagentsforce_community.tools.youtube.search",
    "ZapierNLAListActions": "aiagentsforce_community.tools.zapier.tool",
    "ZapierNLARunAction": "aiagentsforce_community.tools.zapier.tool",
    "ZenGuardInput": "aiagentsforce_community.tools.zenguard.tool",
    "ZenGuardTool": "aiagentsforce_community.tools.zenguard.tool",
    "authenticate": "aiagentsforce_community.tools.office365.utils",
    "format_tool_to_openai_function": "aiagentsforce_community.tools.convert_to_openai",
    "tool": "alibaba_ai_core.tools",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
