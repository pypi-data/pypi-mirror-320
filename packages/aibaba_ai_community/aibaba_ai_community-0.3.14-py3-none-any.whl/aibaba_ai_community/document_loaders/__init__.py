"""**Document Loaders**  are classes to load Documents.

**Document Loaders** are usually used to load a lot of Documents in a single run.

**Class hierarchy:**

.. code-block::

    BaseLoader --> <name>Loader  # Examples: TextLoader, UnstructuredFileLoader

**Main helpers:**

.. code-block::

    Document, <name>TextSplitter
"""

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiagentsforce_community.document_loaders.acreom import (
        AcreomLoader,
    )
    from aiagentsforce_community.document_loaders.airbyte import (
        AirbyteCDKLoader,
        AirbyteGongLoader,
        AirbyteHubspotLoader,
        AirbyteSalesforceLoader,
        AirbyteShopifyLoader,
        AirbyteStripeLoader,
        AirbyteTypeformLoader,
        AirbyteZendeskSupportLoader,
    )
    from aiagentsforce_community.document_loaders.airbyte_json import (
        AirbyteJSONLoader,
    )
    from aiagentsforce_community.document_loaders.airtable import (
        AirtableLoader,
    )
    from aiagentsforce_community.document_loaders.apify_dataset import (
        ApifyDatasetLoader,
    )
    from aiagentsforce_community.document_loaders.arcgis_loader import (
        ArcGISLoader,
    )
    from aiagentsforce_community.document_loaders.arxiv import (
        ArxivLoader,
    )
    from aiagentsforce_community.document_loaders.assemblyai import (
        AssemblyAIAudioLoaderById,
        AssemblyAIAudioTranscriptLoader,
    )
    from aiagentsforce_community.document_loaders.astradb import (
        AstraDBLoader,
    )
    from aiagentsforce_community.document_loaders.async_html import (
        AsyncHtmlLoader,
    )
    from aiagentsforce_community.document_loaders.athena import (
        AthenaLoader,
    )
    from aiagentsforce_community.document_loaders.azlyrics import (
        AZLyricsLoader,
    )
    from aiagentsforce_community.document_loaders.azure_ai_data import (
        AzureAIDataLoader,
    )
    from aiagentsforce_community.document_loaders.azure_blob_storage_container import (
        AzureBlobStorageContainerLoader,
    )
    from aiagentsforce_community.document_loaders.azure_blob_storage_file import (
        AzureBlobStorageFileLoader,
    )
    from aiagentsforce_community.document_loaders.bibtex import (
        BibtexLoader,
    )
    from aiagentsforce_community.document_loaders.bigquery import (
        BigQueryLoader,
    )
    from aiagentsforce_community.document_loaders.bilibili import (
        BiliBiliLoader,
    )
    from aiagentsforce_community.document_loaders.blackboard import (
        BlackboardLoader,
    )
    from aiagentsforce_community.document_loaders.blob_loaders import (
        Blob,
        BlobLoader,
        CloudBlobLoader,
        FileSystemBlobLoader,
        YoutubeAudioLoader,
    )
    from aiagentsforce_community.document_loaders.blockchain import (
        BlockchainDocumentLoader,
    )
    from aiagentsforce_community.document_loaders.brave_search import (
        BraveSearchLoader,
    )
    from aiagentsforce_community.document_loaders.browserbase import (
        BrowserbaseLoader,
    )
    from aiagentsforce_community.document_loaders.browserless import (
        BrowserlessLoader,
    )
    from aiagentsforce_community.document_loaders.cassandra import (
        CassandraLoader,
    )
    from aiagentsforce_community.document_loaders.chatgpt import (
        ChatGPTLoader,
    )
    from aiagentsforce_community.document_loaders.chm import (
        UnstructuredCHMLoader,
    )
    from aiagentsforce_community.document_loaders.chromium import (
        AsyncChromiumLoader,
    )
    from aiagentsforce_community.document_loaders.college_confidential import (
        CollegeConfidentialLoader,
    )
    from aiagentsforce_community.document_loaders.concurrent import (
        ConcurrentLoader,
    )
    from aiagentsforce_community.document_loaders.confluence import (
        ConfluenceLoader,
    )
    from aiagentsforce_community.document_loaders.conllu import (
        CoNLLULoader,
    )
    from aiagentsforce_community.document_loaders.couchbase import (
        CouchbaseLoader,
    )
    from aiagentsforce_community.document_loaders.csv_loader import (
        CSVLoader,
        UnstructuredCSVLoader,
    )
    from aiagentsforce_community.document_loaders.cube_semantic import (
        CubeSemanticLoader,
    )
    from aiagentsforce_community.document_loaders.datadog_logs import (
        DatadogLogsLoader,
    )
    from aiagentsforce_community.document_loaders.dataframe import (
        DataFrameLoader,
    )
    from aiagentsforce_community.document_loaders.dedoc import (
        DedocAPIFileLoader,
        DedocFileLoader,
    )
    from aiagentsforce_community.document_loaders.diffbot import (
        DiffbotLoader,
    )
    from aiagentsforce_community.document_loaders.directory import (
        DirectoryLoader,
    )
    from aiagentsforce_community.document_loaders.discord import (
        DiscordChatLoader,
    )
    from aiagentsforce_community.document_loaders.doc_intelligence import (
        AzureAIDocumentIntelligenceLoader,
    )
    from aiagentsforce_community.document_loaders.docugami import (
        DocugamiLoader,
    )
    from aiagentsforce_community.document_loaders.docusaurus import (
        DocusaurusLoader,
    )
    from aiagentsforce_community.document_loaders.dropbox import (
        DropboxLoader,
    )
    from aiagentsforce_community.document_loaders.duckdb_loader import (
        DuckDBLoader,
    )
    from aiagentsforce_community.document_loaders.email import (
        OutlookMessageLoader,
        UnstructuredEmailLoader,
    )
    from aiagentsforce_community.document_loaders.epub import (
        UnstructuredEPubLoader,
    )
    from aiagentsforce_community.document_loaders.etherscan import (
        EtherscanLoader,
    )
    from aiagentsforce_community.document_loaders.evernote import (
        EverNoteLoader,
    )
    from aiagentsforce_community.document_loaders.excel import (
        UnstructuredExcelLoader,
    )
    from aiagentsforce_community.document_loaders.facebook_chat import (
        FacebookChatLoader,
    )
    from aiagentsforce_community.document_loaders.fauna import (
        FaunaLoader,
    )
    from aiagentsforce_community.document_loaders.figma import (
        FigmaFileLoader,
    )
    from aiagentsforce_community.document_loaders.firecrawl import (
        FireCrawlLoader,
    )
    from aiagentsforce_community.document_loaders.gcs_directory import (
        GCSDirectoryLoader,
    )
    from aiagentsforce_community.document_loaders.gcs_file import (
        GCSFileLoader,
    )
    from aiagentsforce_community.document_loaders.geodataframe import (
        GeoDataFrameLoader,
    )
    from aiagentsforce_community.document_loaders.git import (
        GitLoader,
    )
    from aiagentsforce_community.document_loaders.gitbook import (
        GitbookLoader,
    )
    from aiagentsforce_community.document_loaders.github import (
        GithubFileLoader,
        GitHubIssuesLoader,
    )
    from aiagentsforce_community.document_loaders.glue_catalog import (
        GlueCatalogLoader,
    )
    from aiagentsforce_community.document_loaders.google_speech_to_text import (
        GoogleSpeechToTextLoader,
    )
    from aiagentsforce_community.document_loaders.googledrive import (
        GoogleDriveLoader,
    )
    from aiagentsforce_community.document_loaders.gutenberg import (
        GutenbergLoader,
    )
    from aiagentsforce_community.document_loaders.hn import (
        HNLoader,
    )
    from aiagentsforce_community.document_loaders.html import (
        UnstructuredHTMLLoader,
    )
    from aiagentsforce_community.document_loaders.html_bs import (
        BSHTMLLoader,
    )
    from aiagentsforce_community.document_loaders.hugging_face_dataset import (
        HuggingFaceDatasetLoader,
    )
    from aiagentsforce_community.document_loaders.hugging_face_model import (
        HuggingFaceModelLoader,
    )
    from aiagentsforce_community.document_loaders.ifixit import (
        IFixitLoader,
    )
    from aiagentsforce_community.document_loaders.image import (
        UnstructuredImageLoader,
    )
    from aiagentsforce_community.document_loaders.image_captions import (
        ImageCaptionLoader,
    )
    from aiagentsforce_community.document_loaders.imsdb import (
        IMSDbLoader,
    )
    from aiagentsforce_community.document_loaders.iugu import (
        IuguLoader,
    )
    from aiagentsforce_community.document_loaders.joplin import (
        JoplinLoader,
    )
    from aiagentsforce_community.document_loaders.json_loader import (
        JSONLoader,
    )
    from aiagentsforce_community.document_loaders.kinetica_loader import KineticaLoader
    from aiagentsforce_community.document_loaders.lakefs import (
        LakeFSLoader,
    )
    from aiagentsforce_community.document_loaders.larksuite import (
        LarkSuiteDocLoader,
    )
    from aiagentsforce_community.document_loaders.llmsherpa import (
        LLMSherpaFileLoader,
    )
    from aiagentsforce_community.document_loaders.markdown import (
        UnstructuredMarkdownLoader,
    )
    from aiagentsforce_community.document_loaders.mastodon import (
        MastodonTootsLoader,
    )
    from aiagentsforce_community.document_loaders.max_compute import (
        MaxComputeLoader,
    )
    from aiagentsforce_community.document_loaders.mediawikidump import (
        MWDumpLoader,
    )
    from aiagentsforce_community.document_loaders.merge import (
        MergedDataLoader,
    )
    from aiagentsforce_community.document_loaders.mhtml import (
        MHTMLLoader,
    )
    from aiagentsforce_community.document_loaders.modern_treasury import (
        ModernTreasuryLoader,
    )
    from aiagentsforce_community.document_loaders.mongodb import (
        MongodbLoader,
    )
    from aiagentsforce_community.document_loaders.needle import (
        NeedleLoader,
    )
    from aiagentsforce_community.document_loaders.news import (
        NewsURLLoader,
    )
    from aiagentsforce_community.document_loaders.notebook import (
        NotebookLoader,
    )
    from aiagentsforce_community.document_loaders.notion import (
        NotionDirectoryLoader,
    )
    from aiagentsforce_community.document_loaders.notiondb import (
        NotionDBLoader,
    )
    from aiagentsforce_community.document_loaders.obs_directory import (
        OBSDirectoryLoader,
    )
    from aiagentsforce_community.document_loaders.obs_file import (
        OBSFileLoader,
    )
    from aiagentsforce_community.document_loaders.obsidian import (
        ObsidianLoader,
    )
    from aiagentsforce_community.document_loaders.odt import (
        UnstructuredODTLoader,
    )
    from aiagentsforce_community.document_loaders.onedrive import (
        OneDriveLoader,
    )
    from aiagentsforce_community.document_loaders.onedrive_file import (
        OneDriveFileLoader,
    )
    from aiagentsforce_community.document_loaders.open_city_data import (
        OpenCityDataLoader,
    )
    from aiagentsforce_community.document_loaders.oracleadb_loader import (
        OracleAutonomousDatabaseLoader,
    )
    from aiagentsforce_community.document_loaders.oracleai import (
        OracleDocLoader,
        OracleTextSplitter,
    )
    from aiagentsforce_community.document_loaders.org_mode import (
        UnstructuredOrgModeLoader,
    )
    from aiagentsforce_community.document_loaders.pdf import (
        AmazonTextractPDFLoader,
        DedocPDFLoader,
        MathpixPDFLoader,
        OnlinePDFLoader,
        PagedPDFSplitter,
        PDFMinerLoader,
        PDFMinerPDFasHTMLLoader,
        PDFPlumberLoader,
        PyMuPDFLoader,
        PyPDFDirectoryLoader,
        PyPDFium2Loader,
        PyPDFLoader,
        UnstructuredPDFLoader,
    )
    from aiagentsforce_community.document_loaders.pebblo import (
        PebbloSafeLoader,
        PebbloTextLoader,
    )
    from aiagentsforce_community.document_loaders.polars_dataframe import (
        PolarsDataFrameLoader,
    )
    from aiagentsforce_community.document_loaders.powerpoint import (
        UnstructuredPowerPointLoader,
    )
    from aiagentsforce_community.document_loaders.psychic import (
        PsychicLoader,
    )
    from aiagentsforce_community.document_loaders.pubmed import (
        PubMedLoader,
    )
    from aiagentsforce_community.document_loaders.pyspark_dataframe import (
        PySparkDataFrameLoader,
    )
    from aiagentsforce_community.document_loaders.python import (
        PythonLoader,
    )
    from aiagentsforce_community.document_loaders.readthedocs import (
        ReadTheDocsLoader,
    )
    from aiagentsforce_community.document_loaders.recursive_url_loader import (
        RecursiveUrlLoader,
    )
    from aiagentsforce_community.document_loaders.reddit import (
        RedditPostsLoader,
    )
    from aiagentsforce_community.document_loaders.roam import (
        RoamLoader,
    )
    from aiagentsforce_community.document_loaders.rocksetdb import (
        RocksetLoader,
    )
    from aiagentsforce_community.document_loaders.rss import (
        RSSFeedLoader,
    )
    from aiagentsforce_community.document_loaders.rst import (
        UnstructuredRSTLoader,
    )
    from aiagentsforce_community.document_loaders.rtf import (
        UnstructuredRTFLoader,
    )
    from aiagentsforce_community.document_loaders.s3_directory import (
        S3DirectoryLoader,
    )
    from aiagentsforce_community.document_loaders.s3_file import (
        S3FileLoader,
    )
    from aiagentsforce_community.document_loaders.scrapfly import (
        ScrapflyLoader,
    )
    from aiagentsforce_community.document_loaders.scrapingant import (
        ScrapingAntLoader,
    )
    from aiagentsforce_community.document_loaders.sharepoint import (
        SharePointLoader,
    )
    from aiagentsforce_community.document_loaders.sitemap import (
        SitemapLoader,
    )
    from aiagentsforce_community.document_loaders.slack_directory import (
        SlackDirectoryLoader,
    )
    from aiagentsforce_community.document_loaders.snowflake_loader import (
        SnowflakeLoader,
    )
    from aiagentsforce_community.document_loaders.spider import (
        SpiderLoader,
    )
    from aiagentsforce_community.document_loaders.spreedly import (
        SpreedlyLoader,
    )
    from aiagentsforce_community.document_loaders.sql_database import (
        SQLDatabaseLoader,
    )
    from aiagentsforce_community.document_loaders.srt import (
        SRTLoader,
    )
    from aiagentsforce_community.document_loaders.stripe import (
        StripeLoader,
    )
    from aiagentsforce_community.document_loaders.surrealdb import (
        SurrealDBLoader,
    )
    from aiagentsforce_community.document_loaders.telegram import (
        TelegramChatApiLoader,
        TelegramChatFileLoader,
        TelegramChatLoader,
    )
    from aiagentsforce_community.document_loaders.tencent_cos_directory import (
        TencentCOSDirectoryLoader,
    )
    from aiagentsforce_community.document_loaders.tencent_cos_file import (
        TencentCOSFileLoader,
    )
    from aiagentsforce_community.document_loaders.tensorflow_datasets import (
        TensorflowDatasetLoader,
    )
    from aiagentsforce_community.document_loaders.text import (
        TextLoader,
    )
    from aiagentsforce_community.document_loaders.tidb import (
        TiDBLoader,
    )
    from aiagentsforce_community.document_loaders.tomarkdown import (
        ToMarkdownLoader,
    )
    from aiagentsforce_community.document_loaders.toml import (
        TomlLoader,
    )
    from aiagentsforce_community.document_loaders.trello import (
        TrelloLoader,
    )
    from aiagentsforce_community.document_loaders.tsv import (
        UnstructuredTSVLoader,
    )
    from aiagentsforce_community.document_loaders.twitter import (
        TwitterTweetLoader,
    )
    from aiagentsforce_community.document_loaders.unstructured import (
        UnstructuredAPIFileIOLoader,
        UnstructuredAPIFileLoader,
        UnstructuredFileIOLoader,
        UnstructuredFileLoader,
    )
    from aiagentsforce_community.document_loaders.url import (
        UnstructuredURLLoader,
    )
    from aiagentsforce_community.document_loaders.url_playwright import (
        PlaywrightURLLoader,
    )
    from aiagentsforce_community.document_loaders.url_selenium import (
        SeleniumURLLoader,
    )
    from aiagentsforce_community.document_loaders.vsdx import (
        VsdxLoader,
    )
    from aiagentsforce_community.document_loaders.weather import (
        WeatherDataLoader,
    )
    from aiagentsforce_community.document_loaders.web_base import (
        WebBaseLoader,
    )
    from aiagentsforce_community.document_loaders.whatsapp_chat import (
        WhatsAppChatLoader,
    )
    from aiagentsforce_community.document_loaders.wikipedia import (
        WikipediaLoader,
    )
    from aiagentsforce_community.document_loaders.word_document import (
        Docx2txtLoader,
        UnstructuredWordDocumentLoader,
    )
    from aiagentsforce_community.document_loaders.xml import (
        UnstructuredXMLLoader,
    )
    from aiagentsforce_community.document_loaders.xorbits import (
        XorbitsLoader,
    )
    from aiagentsforce_community.document_loaders.youtube import (
        GoogleApiClient,
        GoogleApiYoutubeLoader,
        YoutubeLoader,
    )
    from aiagentsforce_community.document_loaders.yuque import (
        YuqueLoader,
    )


_module_lookup = {
    "AZLyricsLoader": "aiagentsforce_community.document_loaders.azlyrics",
    "AcreomLoader": "aiagentsforce_community.document_loaders.acreom",
    "AirbyteCDKLoader": "aiagentsforce_community.document_loaders.airbyte",
    "AirbyteGongLoader": "aiagentsforce_community.document_loaders.airbyte",
    "AirbyteHubspotLoader": "aiagentsforce_community.document_loaders.airbyte",
    "AirbyteJSONLoader": "aiagentsforce_community.document_loaders.airbyte_json",
    "AirbyteSalesforceLoader": "aiagentsforce_community.document_loaders.airbyte",
    "AirbyteShopifyLoader": "aiagentsforce_community.document_loaders.airbyte",
    "AirbyteStripeLoader": "aiagentsforce_community.document_loaders.airbyte",
    "AirbyteTypeformLoader": "aiagentsforce_community.document_loaders.airbyte",
    "AirbyteZendeskSupportLoader": "aiagentsforce_community.document_loaders.airbyte",
    "AirtableLoader": "aiagentsforce_community.document_loaders.airtable",
    "AmazonTextractPDFLoader": "aiagentsforce_community.document_loaders.pdf",
    "ApifyDatasetLoader": "aiagentsforce_community.document_loaders.apify_dataset",
    "ArcGISLoader": "aiagentsforce_community.document_loaders.arcgis_loader",
    "ArxivLoader": "aiagentsforce_community.document_loaders.arxiv",
    "AssemblyAIAudioLoaderById": "aiagentsforce_community.document_loaders.assemblyai",
    "AssemblyAIAudioTranscriptLoader": "aiagentsforce_community.document_loaders.assemblyai",  # noqa: E501
    "AstraDBLoader": "aiagentsforce_community.document_loaders.astradb",
    "AsyncChromiumLoader": "aiagentsforce_community.document_loaders.chromium",
    "AsyncHtmlLoader": "aiagentsforce_community.document_loaders.async_html",
    "AthenaLoader": "aiagentsforce_community.document_loaders.athena",
    "AzureAIDataLoader": "aiagentsforce_community.document_loaders.azure_ai_data",
    "AzureAIDocumentIntelligenceLoader": "aiagentsforce_community.document_loaders.doc_intelligence",  # noqa: E501
    "AzureBlobStorageContainerLoader": "aiagentsforce_community.document_loaders.azure_blob_storage_container",  # noqa: E501
    "AzureBlobStorageFileLoader": "aiagentsforce_community.document_loaders.azure_blob_storage_file",  # noqa: E501
    "BSHTMLLoader": "aiagentsforce_community.document_loaders.html_bs",
    "BibtexLoader": "aiagentsforce_community.document_loaders.bibtex",
    "BigQueryLoader": "aiagentsforce_community.document_loaders.bigquery",
    "BiliBiliLoader": "aiagentsforce_community.document_loaders.bilibili",
    "BlackboardLoader": "aiagentsforce_community.document_loaders.blackboard",
    "Blob": "aiagentsforce_community.document_loaders.blob_loaders",
    "BlobLoader": "aiagentsforce_community.document_loaders.blob_loaders",
    "BlockchainDocumentLoader": "aiagentsforce_community.document_loaders.blockchain",
    "BraveSearchLoader": "aiagentsforce_community.document_loaders.brave_search",
    "BrowserbaseLoader": "aiagentsforce_community.document_loaders.browserbase",
    "BrowserlessLoader": "aiagentsforce_community.document_loaders.browserless",
    "CSVLoader": "aiagentsforce_community.document_loaders.csv_loader",
    "CassandraLoader": "aiagentsforce_community.document_loaders.cassandra",
    "ChatGPTLoader": "aiagentsforce_community.document_loaders.chatgpt",
    "CloudBlobLoader": "aiagentsforce_community.document_loaders.blob_loaders",
    "CoNLLULoader": "aiagentsforce_community.document_loaders.conllu",
    "CollegeConfidentialLoader": "aiagentsforce_community.document_loaders.college_confidential",  # noqa: E501
    "ConcurrentLoader": "aiagentsforce_community.document_loaders.concurrent",
    "ConfluenceLoader": "aiagentsforce_community.document_loaders.confluence",
    "CouchbaseLoader": "aiagentsforce_community.document_loaders.couchbase",
    "CubeSemanticLoader": "aiagentsforce_community.document_loaders.cube_semantic",
    "DataFrameLoader": "aiagentsforce_community.document_loaders.dataframe",
    "DatadogLogsLoader": "aiagentsforce_community.document_loaders.datadog_logs",
    "DedocAPIFileLoader": "aiagentsforce_community.document_loaders.dedoc",
    "DedocFileLoader": "aiagentsforce_community.document_loaders.dedoc",
    "DedocPDFLoader": "aiagentsforce_community.document_loaders.pdf",
    "DiffbotLoader": "aiagentsforce_community.document_loaders.diffbot",
    "DirectoryLoader": "aiagentsforce_community.document_loaders.directory",
    "DiscordChatLoader": "aiagentsforce_community.document_loaders.discord",
    "DocugamiLoader": "aiagentsforce_community.document_loaders.docugami",
    "DocusaurusLoader": "aiagentsforce_community.document_loaders.docusaurus",
    "Docx2txtLoader": "aiagentsforce_community.document_loaders.word_document",
    "DropboxLoader": "aiagentsforce_community.document_loaders.dropbox",
    "DuckDBLoader": "aiagentsforce_community.document_loaders.duckdb_loader",
    "EtherscanLoader": "aiagentsforce_community.document_loaders.etherscan",
    "EverNoteLoader": "aiagentsforce_community.document_loaders.evernote",
    "FacebookChatLoader": "aiagentsforce_community.document_loaders.facebook_chat",
    "FaunaLoader": "aiagentsforce_community.document_loaders.fauna",
    "FigmaFileLoader": "aiagentsforce_community.document_loaders.figma",
    "FireCrawlLoader": "aiagentsforce_community.document_loaders.firecrawl",
    "FileSystemBlobLoader": "aiagentsforce_community.document_loaders.blob_loaders",
    "GCSDirectoryLoader": "aiagentsforce_community.document_loaders.gcs_directory",
    "GCSFileLoader": "aiagentsforce_community.document_loaders.gcs_file",
    "GeoDataFrameLoader": "aiagentsforce_community.document_loaders.geodataframe",
    "GitHubIssuesLoader": "aiagentsforce_community.document_loaders.github",
    "GitLoader": "aiagentsforce_community.document_loaders.git",
    "GitbookLoader": "aiagentsforce_community.document_loaders.gitbook",
    "GithubFileLoader": "aiagentsforce_community.document_loaders.github",
    "GlueCatalogLoader": "aiagentsforce_community.document_loaders.glue_catalog",
    "GoogleApiClient": "aiagentsforce_community.document_loaders.youtube",
    "GoogleApiYoutubeLoader": "aiagentsforce_community.document_loaders.youtube",
    "GoogleDriveLoader": "aiagentsforce_community.document_loaders.googledrive",
    "GoogleSpeechToTextLoader": "aiagentsforce_community.document_loaders.google_speech_to_text",  # noqa: E501
    "GutenbergLoader": "aiagentsforce_community.document_loaders.gutenberg",
    "HNLoader": "aiagentsforce_community.document_loaders.hn",
    "HuggingFaceDatasetLoader": "aiagentsforce_community.document_loaders.hugging_face_dataset",  # noqa: E501
    "HuggingFaceModelLoader": "aiagentsforce_community.document_loaders.hugging_face_model",
    "IFixitLoader": "aiagentsforce_community.document_loaders.ifixit",
    "IMSDbLoader": "aiagentsforce_community.document_loaders.imsdb",
    "ImageCaptionLoader": "aiagentsforce_community.document_loaders.image_captions",
    "IuguLoader": "aiagentsforce_community.document_loaders.iugu",
    "JSONLoader": "aiagentsforce_community.document_loaders.json_loader",
    "JoplinLoader": "aiagentsforce_community.document_loaders.joplin",
    "KineticaLoader": "aiagentsforce_community.document_loaders.kinetica_loader",
    "LakeFSLoader": "aiagentsforce_community.document_loaders.lakefs",
    "LarkSuiteDocLoader": "aiagentsforce_community.document_loaders.larksuite",
    "LLMSherpaFileLoader": "aiagentsforce_community.document_loaders.llmsherpa",
    "MHTMLLoader": "aiagentsforce_community.document_loaders.mhtml",
    "MWDumpLoader": "aiagentsforce_community.document_loaders.mediawikidump",
    "MastodonTootsLoader": "aiagentsforce_community.document_loaders.mastodon",
    "MathpixPDFLoader": "aiagentsforce_community.document_loaders.pdf",
    "MaxComputeLoader": "aiagentsforce_community.document_loaders.max_compute",
    "MergedDataLoader": "aiagentsforce_community.document_loaders.merge",
    "ModernTreasuryLoader": "aiagentsforce_community.document_loaders.modern_treasury",
    "MongodbLoader": "aiagentsforce_community.document_loaders.mongodb",
    "NeedleLoader": "aiagentsforce_community.document_loaders.needle",
    "NewsURLLoader": "aiagentsforce_community.document_loaders.news",
    "NotebookLoader": "aiagentsforce_community.document_loaders.notebook",
    "NotionDBLoader": "aiagentsforce_community.document_loaders.notiondb",
    "NotionDirectoryLoader": "aiagentsforce_community.document_loaders.notion",
    "OBSDirectoryLoader": "aiagentsforce_community.document_loaders.obs_directory",
    "OBSFileLoader": "aiagentsforce_community.document_loaders.obs_file",
    "ObsidianLoader": "aiagentsforce_community.document_loaders.obsidian",
    "OneDriveFileLoader": "aiagentsforce_community.document_loaders.onedrive_file",
    "OneDriveLoader": "aiagentsforce_community.document_loaders.onedrive",
    "OnlinePDFLoader": "aiagentsforce_community.document_loaders.pdf",
    "OpenCityDataLoader": "aiagentsforce_community.document_loaders.open_city_data",
    "OracleAutonomousDatabaseLoader": "aiagentsforce_community.document_loaders.oracleadb_loader",  # noqa: E501
    "OracleDocLoader": "aiagentsforce_community.document_loaders.oracleai",
    "OracleTextSplitter": "aiagentsforce_community.document_loaders.oracleai",
    "OutlookMessageLoader": "aiagentsforce_community.document_loaders.email",
    "PDFMinerLoader": "aiagentsforce_community.document_loaders.pdf",
    "PDFMinerPDFasHTMLLoader": "aiagentsforce_community.document_loaders.pdf",
    "PDFPlumberLoader": "aiagentsforce_community.document_loaders.pdf",
    "PagedPDFSplitter": "aiagentsforce_community.document_loaders.pdf",
    "PebbloSafeLoader": "aiagentsforce_community.document_loaders.pebblo",
    "PebbloTextLoader": "aiagentsforce_community.document_loaders.pebblo",
    "PlaywrightURLLoader": "aiagentsforce_community.document_loaders.url_playwright",
    "PolarsDataFrameLoader": "aiagentsforce_community.document_loaders.polars_dataframe",
    "PsychicLoader": "aiagentsforce_community.document_loaders.psychic",
    "PubMedLoader": "aiagentsforce_community.document_loaders.pubmed",
    "PyMuPDFLoader": "aiagentsforce_community.document_loaders.pdf",
    "PyPDFDirectoryLoader": "aiagentsforce_community.document_loaders.pdf",
    "PyPDFLoader": "aiagentsforce_community.document_loaders.pdf",
    "PyPDFium2Loader": "aiagentsforce_community.document_loaders.pdf",
    "PySparkDataFrameLoader": "aiagentsforce_community.document_loaders.pyspark_dataframe",
    "PythonLoader": "aiagentsforce_community.document_loaders.python",
    "RSSFeedLoader": "aiagentsforce_community.document_loaders.rss",
    "ReadTheDocsLoader": "aiagentsforce_community.document_loaders.readthedocs",
    "RecursiveUrlLoader": "aiagentsforce_community.document_loaders.recursive_url_loader",
    "RedditPostsLoader": "aiagentsforce_community.document_loaders.reddit",
    "RoamLoader": "aiagentsforce_community.document_loaders.roam",
    "RocksetLoader": "aiagentsforce_community.document_loaders.rocksetdb",
    "S3DirectoryLoader": "aiagentsforce_community.document_loaders.s3_directory",
    "S3FileLoader": "aiagentsforce_community.document_loaders.s3_file",
    "ScrapflyLoader": "aiagentsforce_community.document_loaders.scrapfly",
    "ScrapingAntLoader": "aiagentsforce_community.document_loaders.scrapingant",
    "SQLDatabaseLoader": "aiagentsforce_community.document_loaders.sql_database",
    "SRTLoader": "aiagentsforce_community.document_loaders.srt",
    "SeleniumURLLoader": "aiagentsforce_community.document_loaders.url_selenium",
    "SharePointLoader": "aiagentsforce_community.document_loaders.sharepoint",
    "SitemapLoader": "aiagentsforce_community.document_loaders.sitemap",
    "SlackDirectoryLoader": "aiagentsforce_community.document_loaders.slack_directory",
    "SnowflakeLoader": "aiagentsforce_community.document_loaders.snowflake_loader",
    "SpiderLoader": "aiagentsforce_community.document_loaders.spider",
    "SpreedlyLoader": "aiagentsforce_community.document_loaders.spreedly",
    "StripeLoader": "aiagentsforce_community.document_loaders.stripe",
    "SurrealDBLoader": "aiagentsforce_community.document_loaders.surrealdb",
    "TelegramChatApiLoader": "aiagentsforce_community.document_loaders.telegram",
    "TelegramChatFileLoader": "aiagentsforce_community.document_loaders.telegram",
    "TelegramChatLoader": "aiagentsforce_community.document_loaders.telegram",
    "TencentCOSDirectoryLoader": "aiagentsforce_community.document_loaders.tencent_cos_directory",  # noqa: E501
    "TencentCOSFileLoader": "aiagentsforce_community.document_loaders.tencent_cos_file",
    "TensorflowDatasetLoader": "aiagentsforce_community.document_loaders.tensorflow_datasets",  # noqa: E501
    "TextLoader": "aiagentsforce_community.document_loaders.text",
    "TiDBLoader": "aiagentsforce_community.document_loaders.tidb",
    "ToMarkdownLoader": "aiagentsforce_community.document_loaders.tomarkdown",
    "TomlLoader": "aiagentsforce_community.document_loaders.toml",
    "TrelloLoader": "aiagentsforce_community.document_loaders.trello",
    "TwitterTweetLoader": "aiagentsforce_community.document_loaders.twitter",
    "UnstructuredAPIFileIOLoader": "aiagentsforce_community.document_loaders.unstructured",
    "UnstructuredAPIFileLoader": "aiagentsforce_community.document_loaders.unstructured",
    "UnstructuredCHMLoader": "aiagentsforce_community.document_loaders.chm",
    "UnstructuredCSVLoader": "aiagentsforce_community.document_loaders.csv_loader",
    "UnstructuredEPubLoader": "aiagentsforce_community.document_loaders.epub",
    "UnstructuredEmailLoader": "aiagentsforce_community.document_loaders.email",
    "UnstructuredExcelLoader": "aiagentsforce_community.document_loaders.excel",
    "UnstructuredFileIOLoader": "aiagentsforce_community.document_loaders.unstructured",
    "UnstructuredFileLoader": "aiagentsforce_community.document_loaders.unstructured",
    "UnstructuredHTMLLoader": "aiagentsforce_community.document_loaders.html",
    "UnstructuredImageLoader": "aiagentsforce_community.document_loaders.image",
    "UnstructuredMarkdownLoader": "aiagentsforce_community.document_loaders.markdown",
    "UnstructuredODTLoader": "aiagentsforce_community.document_loaders.odt",
    "UnstructuredOrgModeLoader": "aiagentsforce_community.document_loaders.org_mode",
    "UnstructuredPDFLoader": "aiagentsforce_community.document_loaders.pdf",
    "UnstructuredPowerPointLoader": "aiagentsforce_community.document_loaders.powerpoint",
    "UnstructuredRSTLoader": "aiagentsforce_community.document_loaders.rst",
    "UnstructuredRTFLoader": "aiagentsforce_community.document_loaders.rtf",
    "UnstructuredTSVLoader": "aiagentsforce_community.document_loaders.tsv",
    "UnstructuredURLLoader": "aiagentsforce_community.document_loaders.url",
    "UnstructuredWordDocumentLoader": "aiagentsforce_community.document_loaders.word_document",  # noqa: E501
    "UnstructuredXMLLoader": "aiagentsforce_community.document_loaders.xml",
    "VsdxLoader": "aiagentsforce_community.document_loaders.vsdx",
    "WeatherDataLoader": "aiagentsforce_community.document_loaders.weather",
    "WebBaseLoader": "aiagentsforce_community.document_loaders.web_base",
    "WhatsAppChatLoader": "aiagentsforce_community.document_loaders.whatsapp_chat",
    "WikipediaLoader": "aiagentsforce_community.document_loaders.wikipedia",
    "XorbitsLoader": "aiagentsforce_community.document_loaders.xorbits",
    "YoutubeAudioLoader": "aiagentsforce_community.document_loaders.blob_loaders",
    "YoutubeLoader": "aiagentsforce_community.document_loaders.youtube",
    "YuqueLoader": "aiagentsforce_community.document_loaders.yuque",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")


__all__ = [
    "AZLyricsLoader",
    "AcreomLoader",
    "AirbyteCDKLoader",
    "AirbyteGongLoader",
    "AirbyteHubspotLoader",
    "AirbyteJSONLoader",
    "AirbyteSalesforceLoader",
    "AirbyteShopifyLoader",
    "AirbyteStripeLoader",
    "AirbyteTypeformLoader",
    "AirbyteZendeskSupportLoader",
    "AirtableLoader",
    "AmazonTextractPDFLoader",
    "ApifyDatasetLoader",
    "ArcGISLoader",
    "ArxivLoader",
    "AssemblyAIAudioLoaderById",
    "AssemblyAIAudioTranscriptLoader",
    "AstraDBLoader",
    "AsyncChromiumLoader",
    "AsyncHtmlLoader",
    "AthenaLoader",
    "AzureAIDataLoader",
    "AzureAIDocumentIntelligenceLoader",
    "AzureBlobStorageContainerLoader",
    "AzureBlobStorageFileLoader",
    "BSHTMLLoader",
    "BibtexLoader",
    "BigQueryLoader",
    "BiliBiliLoader",
    "BlackboardLoader",
    "Blob",
    "BlobLoader",
    "BlockchainDocumentLoader",
    "BraveSearchLoader",
    "BrowserbaseLoader",
    "BrowserlessLoader",
    "CSVLoader",
    "CassandraLoader",
    "ChatGPTLoader",
    "CloudBlobLoader",
    "CoNLLULoader",
    "CollegeConfidentialLoader",
    "ConcurrentLoader",
    "ConfluenceLoader",
    "CouchbaseLoader",
    "CubeSemanticLoader",
    "DataFrameLoader",
    "DatadogLogsLoader",
    "DedocAPIFileLoader",
    "DedocFileLoader",
    "DedocPDFLoader",
    "DiffbotLoader",
    "DirectoryLoader",
    "DiscordChatLoader",
    "DocugamiLoader",
    "DocusaurusLoader",
    "Docx2txtLoader",
    "DropboxLoader",
    "DuckDBLoader",
    "EtherscanLoader",
    "EverNoteLoader",
    "FacebookChatLoader",
    "FaunaLoader",
    "FigmaFileLoader",
    "FireCrawlLoader",
    "FileSystemBlobLoader",
    "GCSDirectoryLoader",
    "GlueCatalogLoader",
    "GCSFileLoader",
    "GeoDataFrameLoader",
    "GitHubIssuesLoader",
    "GitLoader",
    "GitbookLoader",
    "GithubFileLoader",
    "GoogleApiClient",
    "GoogleApiYoutubeLoader",
    "GoogleDriveLoader",
    "GoogleSpeechToTextLoader",
    "GutenbergLoader",
    "HNLoader",
    "HuggingFaceDatasetLoader",
    "HuggingFaceModelLoader",
    "IFixitLoader",
    "ImageCaptionLoader",
    "IMSDbLoader",
    "IuguLoader",
    "JoplinLoader",
    "JSONLoader",
    "KineticaLoader",
    "LakeFSLoader",
    "LarkSuiteDocLoader",
    "LLMSherpaFileLoader",
    "MastodonTootsLoader",
    "MHTMLLoader",
    "MWDumpLoader",
    "MathpixPDFLoader",
    "MaxComputeLoader",
    "MergedDataLoader",
    "ModernTreasuryLoader",
    "MongodbLoader",
    "NeedleLoader",
    "NewsURLLoader",
    "NotebookLoader",
    "NotionDBLoader",
    "NotionDirectoryLoader",
    "OBSDirectoryLoader",
    "OBSFileLoader",
    "ObsidianLoader",
    "OneDriveFileLoader",
    "OneDriveLoader",
    "OnlinePDFLoader",
    "OpenCityDataLoader",
    "OracleAutonomousDatabaseLoader",
    "OracleDocLoader",
    "OracleTextSplitter",
    "OutlookMessageLoader",
    "PDFMinerLoader",
    "PDFMinerPDFasHTMLLoader",
    "PDFPlumberLoader",
    "PagedPDFSplitter",
    "PebbloSafeLoader",
    "PebbloTextLoader",
    "PlaywrightURLLoader",
    "PolarsDataFrameLoader",
    "PsychicLoader",
    "PubMedLoader",
    "PyMuPDFLoader",
    "PyPDFDirectoryLoader",
    "PyPDFLoader",
    "PyPDFium2Loader",
    "PySparkDataFrameLoader",
    "PythonLoader",
    "RSSFeedLoader",
    "ReadTheDocsLoader",
    "RecursiveUrlLoader",
    "RedditPostsLoader",
    "RoamLoader",
    "RocksetLoader",
    "S3DirectoryLoader",
    "S3FileLoader",
    "ScrapflyLoader",
    "ScrapingAntLoader",
    "SQLDatabaseLoader",
    "SRTLoader",
    "SeleniumURLLoader",
    "SharePointLoader",
    "SitemapLoader",
    "SlackDirectoryLoader",
    "SnowflakeLoader",
    "SpiderLoader",
    "SpreedlyLoader",
    "StripeLoader",
    "SurrealDBLoader",
    "TelegramChatApiLoader",
    "TelegramChatFileLoader",
    "TelegramChatLoader",
    "TencentCOSDirectoryLoader",
    "TencentCOSFileLoader",
    "TensorflowDatasetLoader",
    "TextLoader",
    "TiDBLoader",
    "ToMarkdownLoader",
    "TomlLoader",
    "TrelloLoader",
    "TwitterTweetLoader",
    "UnstructuredAPIFileIOLoader",
    "UnstructuredAPIFileLoader",
    "UnstructuredCHMLoader",
    "UnstructuredCSVLoader",
    "UnstructuredEPubLoader",
    "UnstructuredEmailLoader",
    "UnstructuredExcelLoader",
    "UnstructuredFileIOLoader",
    "UnstructuredFileLoader",
    "UnstructuredHTMLLoader",
    "UnstructuredImageLoader",
    "UnstructuredMarkdownLoader",
    "UnstructuredODTLoader",
    "UnstructuredOrgModeLoader",
    "UnstructuredPDFLoader",
    "UnstructuredPowerPointLoader",
    "UnstructuredRSTLoader",
    "UnstructuredRTFLoader",
    "UnstructuredTSVLoader",
    "UnstructuredURLLoader",
    "UnstructuredWordDocumentLoader",
    "UnstructuredXMLLoader",
    "VsdxLoader",
    "WeatherDataLoader",
    "WebBaseLoader",
    "WhatsAppChatLoader",
    "WikipediaLoader",
    "XorbitsLoader",
    "YoutubeAudioLoader",
    "YoutubeLoader",
    "YuqueLoader",
]
