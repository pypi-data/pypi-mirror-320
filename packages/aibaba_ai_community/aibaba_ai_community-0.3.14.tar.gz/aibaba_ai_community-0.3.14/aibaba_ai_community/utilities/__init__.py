"""**Utilities** are the integrations with third-part systems and packages.

Other Aibaba AI classes use **Utilities** to interact with third-part systems
and packages.
"""

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiagentsforce_community.utilities.alpha_vantage import (
        AlphaVantageAPIWrapper,
    )
    from aiagentsforce_community.utilities.apify import (
        ApifyWrapper,
    )
    from aiagentsforce_community.utilities.arcee import (
        ArceeWrapper,
    )
    from aiagentsforce_community.utilities.arxiv import (
        ArxivAPIWrapper,
    )
    from aiagentsforce_community.utilities.asknews import (
        AskNewsAPIWrapper,
    )
    from aiagentsforce_community.utilities.awslambda import (
        LambdaWrapper,
    )
    from aiagentsforce_community.utilities.bibtex import (
        BibtexparserWrapper,
    )
    from aiagentsforce_community.utilities.bing_search import (
        BingSearchAPIWrapper,
    )
    from aiagentsforce_community.utilities.brave_search import (
        BraveSearchWrapper,
    )
    from aiagentsforce_community.utilities.dataherald import DataheraldAPIWrapper
    from aiagentsforce_community.utilities.dria_index import (
        DriaAPIWrapper,
    )
    from aiagentsforce_community.utilities.duckduckgo_search import (
        DuckDuckGoSearchAPIWrapper,
    )
    from aiagentsforce_community.utilities.golden_query import (
        GoldenQueryAPIWrapper,
    )
    from aiagentsforce_community.utilities.google_books import (
        GoogleBooksAPIWrapper,
    )
    from aiagentsforce_community.utilities.google_finance import (
        GoogleFinanceAPIWrapper,
    )
    from aiagentsforce_community.utilities.google_jobs import (
        GoogleJobsAPIWrapper,
    )
    from aiagentsforce_community.utilities.google_lens import (
        GoogleLensAPIWrapper,
    )
    from aiagentsforce_community.utilities.google_places_api import (
        GooglePlacesAPIWrapper,
    )
    from aiagentsforce_community.utilities.google_scholar import (
        GoogleScholarAPIWrapper,
    )
    from aiagentsforce_community.utilities.google_search import (
        GoogleSearchAPIWrapper,
    )
    from aiagentsforce_community.utilities.google_serper import (
        GoogleSerperAPIWrapper,
    )
    from aiagentsforce_community.utilities.google_trends import (
        GoogleTrendsAPIWrapper,
    )
    from aiagentsforce_community.utilities.graphql import (
        GraphQLAPIWrapper,
    )
    from aiagentsforce_community.utilities.infobip import (
        InfobipAPIWrapper,
    )
    from aiagentsforce_community.utilities.jira import (
        JiraAPIWrapper,
    )
    from aiagentsforce_community.utilities.max_compute import (
        MaxComputeAPIWrapper,
    )
    from aiagentsforce_community.utilities.merriam_webster import (
        MerriamWebsterAPIWrapper,
    )
    from aiagentsforce_community.utilities.metaphor_search import (
        MetaphorSearchAPIWrapper,
    )
    from aiagentsforce_community.utilities.mojeek_search import (
        MojeekSearchAPIWrapper,
    )
    from aiagentsforce_community.utilities.nasa import (
        NasaAPIWrapper,
    )
    from aiagentsforce_community.utilities.nvidia_riva import (
        AudioStream,
        NVIDIARivaASR,
        NVIDIARivaStream,
        NVIDIARivaTTS,
        RivaASR,
        RivaTTS,
    )
    from aiagentsforce_community.utilities.openweathermap import (
        OpenWeatherMapAPIWrapper,
    )
    from aiagentsforce_community.utilities.oracleai import (
        OracleSummary,
    )
    from aiagentsforce_community.utilities.outline import (
        OutlineAPIWrapper,
    )
    from aiagentsforce_community.utilities.passio_nutrition_ai import (
        NutritionAIAPI,
    )
    from aiagentsforce_community.utilities.portkey import (
        Portkey,
    )
    from aiagentsforce_community.utilities.powerbi import (
        PowerBIDataset,
    )
    from aiagentsforce_community.utilities.pubmed import (
        PubMedAPIWrapper,
    )
    from aiagentsforce_community.utilities.rememberizer import RememberizerAPIWrapper
    from aiagentsforce_community.utilities.requests import (
        Requests,
        RequestsWrapper,
        TextRequestsWrapper,
    )
    from aiagentsforce_community.utilities.scenexplain import (
        SceneXplainAPIWrapper,
    )
    from aiagentsforce_community.utilities.searchapi import (
        SearchApiAPIWrapper,
    )
    from aiagentsforce_community.utilities.searx_search import (
        SearxSearchWrapper,
    )
    from aiagentsforce_community.utilities.serpapi import (
        SerpAPIWrapper,
    )
    from aiagentsforce_community.utilities.spark_sql import (
        SparkSQL,
    )
    from aiagentsforce_community.utilities.sql_database import (
        SQLDatabase,
    )
    from aiagentsforce_community.utilities.stackexchange import (
        StackExchangeAPIWrapper,
    )
    from aiagentsforce_community.utilities.steam import (
        SteamWebAPIWrapper,
    )
    from aiagentsforce_community.utilities.tensorflow_datasets import (
        TensorflowDatasets,
    )
    from aiagentsforce_community.utilities.twilio import (
        TwilioAPIWrapper,
    )
    from aiagentsforce_community.utilities.wikipedia import (
        WikipediaAPIWrapper,
    )
    from aiagentsforce_community.utilities.wolfram_alpha import (
        WolframAlphaAPIWrapper,
    )
    from aiagentsforce_community.utilities.you import (
        YouSearchAPIWrapper,
    )
    from aiagentsforce_community.utilities.zapier import (
        ZapierNLAWrapper,
    )

__all__ = [
    "AlphaVantageAPIWrapper",
    "ApifyWrapper",
    "ArceeWrapper",
    "ArxivAPIWrapper",
    "AskNewsAPIWrapper",
    "AudioStream",
    "BibtexparserWrapper",
    "BingSearchAPIWrapper",
    "BraveSearchWrapper",
    "DataheraldAPIWrapper",
    "DriaAPIWrapper",
    "DuckDuckGoSearchAPIWrapper",
    "GoldenQueryAPIWrapper",
    "GoogleBooksAPIWrapper",
    "GoogleFinanceAPIWrapper",
    "GoogleJobsAPIWrapper",
    "GoogleLensAPIWrapper",
    "GooglePlacesAPIWrapper",
    "GoogleScholarAPIWrapper",
    "GoogleSearchAPIWrapper",
    "GoogleSerperAPIWrapper",
    "GoogleTrendsAPIWrapper",
    "GraphQLAPIWrapper",
    "InfobipAPIWrapper",
    "JiraAPIWrapper",
    "LambdaWrapper",
    "MaxComputeAPIWrapper",
    "MerriamWebsterAPIWrapper",
    "MetaphorSearchAPIWrapper",
    "MojeekSearchAPIWrapper",
    "NVIDIARivaASR",
    "NVIDIARivaStream",
    "NVIDIARivaTTS",
    "NasaAPIWrapper",
    "NutritionAIAPI",
    "OpenWeatherMapAPIWrapper",
    "OracleSummary",
    "OutlineAPIWrapper",
    "Portkey",
    "PowerBIDataset",
    "PubMedAPIWrapper",
    "RememberizerAPIWrapper",
    "Requests",
    "RequestsWrapper",
    "RivaASR",
    "RivaTTS",
    "SceneXplainAPIWrapper",
    "SearchApiAPIWrapper",
    "SQLDatabase",
    "SearxSearchWrapper",
    "SerpAPIWrapper",
    "SparkSQL",
    "StackExchangeAPIWrapper",
    "SteamWebAPIWrapper",
    "TensorflowDatasets",
    "TextRequestsWrapper",
    "TwilioAPIWrapper",
    "WikipediaAPIWrapper",
    "WolframAlphaAPIWrapper",
    "YouSearchAPIWrapper",
    "ZapierNLAWrapper",
]

_module_lookup = {
    "AlphaVantageAPIWrapper": "aiagentsforce_community.utilities.alpha_vantage",
    "ApifyWrapper": "aiagentsforce_community.utilities.apify",
    "ArceeWrapper": "aiagentsforce_community.utilities.arcee",
    "ArxivAPIWrapper": "aiagentsforce_community.utilities.arxiv",
    "AskNewsAPIWrapper": "aiagentsforce_community.utilities.asknews",
    "AudioStream": "aiagentsforce_community.utilities.nvidia_riva",
    "BibtexparserWrapper": "aiagentsforce_community.utilities.bibtex",
    "BingSearchAPIWrapper": "aiagentsforce_community.utilities.bing_search",
    "BraveSearchWrapper": "aiagentsforce_community.utilities.brave_search",
    "DataheraldAPIWrapper": "aiagentsforce_community.utilities.dataherald",
    "DriaAPIWrapper": "aiagentsforce_community.utilities.dria_index",
    "DuckDuckGoSearchAPIWrapper": "aiagentsforce_community.utilities.duckduckgo_search",
    "GoldenQueryAPIWrapper": "aiagentsforce_community.utilities.golden_query",
    "GoogleBooksAPIWrapper": "aiagentsforce_community.utilities.google_books",
    "GoogleFinanceAPIWrapper": "aiagentsforce_community.utilities.google_finance",
    "GoogleJobsAPIWrapper": "aiagentsforce_community.utilities.google_jobs",
    "GoogleLensAPIWrapper": "aiagentsforce_community.utilities.google_lens",
    "GooglePlacesAPIWrapper": "aiagentsforce_community.utilities.google_places_api",
    "GoogleScholarAPIWrapper": "aiagentsforce_community.utilities.google_scholar",
    "GoogleSearchAPIWrapper": "aiagentsforce_community.utilities.google_search",
    "GoogleSerperAPIWrapper": "aiagentsforce_community.utilities.google_serper",
    "GoogleTrendsAPIWrapper": "aiagentsforce_community.utilities.google_trends",
    "GraphQLAPIWrapper": "aiagentsforce_community.utilities.graphql",
    "InfobipAPIWrapper": "aiagentsforce_community.utilities.infobip",
    "JiraAPIWrapper": "aiagentsforce_community.utilities.jira",
    "LambdaWrapper": "aiagentsforce_community.utilities.awslambda",
    "MaxComputeAPIWrapper": "aiagentsforce_community.utilities.max_compute",
    "MerriamWebsterAPIWrapper": "aiagentsforce_community.utilities.merriam_webster",
    "MetaphorSearchAPIWrapper": "aiagentsforce_community.utilities.metaphor_search",
    "MojeekSearchAPIWrapper": "aiagentsforce_community.utilities.mojeek_search",
    "NVIDIARivaASR": "aiagentsforce_community.utilities.nvidia_riva",
    "NVIDIARivaStream": "aiagentsforce_community.utilities.nvidia_riva",
    "NVIDIARivaTTS": "aiagentsforce_community.utilities.nvidia_riva",
    "NasaAPIWrapper": "aiagentsforce_community.utilities.nasa",
    "NutritionAIAPI": "aiagentsforce_community.utilities.passio_nutrition_ai",
    "OpenWeatherMapAPIWrapper": "aiagentsforce_community.utilities.openweathermap",
    "OracleSummary": "aiagentsforce_community.utilities.oracleai",
    "OutlineAPIWrapper": "aiagentsforce_community.utilities.outline",
    "Portkey": "aiagentsforce_community.utilities.portkey",
    "PowerBIDataset": "aiagentsforce_community.utilities.powerbi",
    "PubMedAPIWrapper": "aiagentsforce_community.utilities.pubmed",
    "RememberizerAPIWrapper": "aiagentsforce_community.utilities.rememberizer",
    "Requests": "aiagentsforce_community.utilities.requests",
    "RequestsWrapper": "aiagentsforce_community.utilities.requests",
    "RivaASR": "aiagentsforce_community.utilities.nvidia_riva",
    "RivaTTS": "aiagentsforce_community.utilities.nvidia_riva",
    "SQLDatabase": "aiagentsforce_community.utilities.sql_database",
    "SceneXplainAPIWrapper": "aiagentsforce_community.utilities.scenexplain",
    "SearchApiAPIWrapper": "aiagentsforce_community.utilities.searchapi",
    "SearxSearchWrapper": "aiagentsforce_community.utilities.searx_search",
    "SerpAPIWrapper": "aiagentsforce_community.utilities.serpapi",
    "SparkSQL": "aiagentsforce_community.utilities.spark_sql",
    "StackExchangeAPIWrapper": "aiagentsforce_community.utilities.stackexchange",
    "SteamWebAPIWrapper": "aiagentsforce_community.utilities.steam",
    "TensorflowDatasets": "aiagentsforce_community.utilities.tensorflow_datasets",
    "TextRequestsWrapper": "aiagentsforce_community.utilities.requests",
    "TwilioAPIWrapper": "aiagentsforce_community.utilities.twilio",
    "WikipediaAPIWrapper": "aiagentsforce_community.utilities.wikipedia",
    "WolframAlphaAPIWrapper": "aiagentsforce_community.utilities.wolfram_alpha",
    "YouSearchAPIWrapper": "aiagentsforce_community.utilities.you",
    "ZapierNLAWrapper": "aiagentsforce_community.utilities.zapier",
}

REMOVED = {
    "PythonREPL": (
        "PythonREPL has been deprecated from aiagentsforce_community "
        "due to being flagged by security scanners. See: "
        "https://github.com/aibaba-ai/aibaba-ai/issues/14345 "
        "If you need to use it, please use the version "
        "from langchain_experimental. "
        "from langchain_experimental.utilities.python import PythonREPL."
    )
}


def __getattr__(name: str) -> Any:
    if name in REMOVED:
        raise AssertionError(REMOVED[name])
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
