import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiagentsforce_community.document_loaders.parsers.audio import (
        OpenAIWhisperParser,
    )
    from aiagentsforce_community.document_loaders.parsers.doc_intelligence import (
        AzureAIDocumentIntelligenceParser,
    )
    from aiagentsforce_community.document_loaders.parsers.docai import (
        DocAIParser,
    )
    from aiagentsforce_community.document_loaders.parsers.grobid import (
        GrobidParser,
    )
    from aiagentsforce_community.document_loaders.parsers.html import (
        BS4HTMLParser,
    )
    from aiagentsforce_community.document_loaders.parsers.language import (
        LanguageParser,
    )
    from aiagentsforce_community.document_loaders.parsers.pdf import (
        PDFMinerParser,
        PDFPlumberParser,
        PyMuPDFParser,
        PyPDFium2Parser,
        PyPDFParser,
    )
    from aiagentsforce_community.document_loaders.parsers.vsdx import (
        VsdxParser,
    )


_module_lookup = {
    "AzureAIDocumentIntelligenceParser": "aiagentsforce_community.document_loaders.parsers.doc_intelligence",  # noqa: E501
    "BS4HTMLParser": "aiagentsforce_community.document_loaders.parsers.html",
    "DocAIParser": "aiagentsforce_community.document_loaders.parsers.docai",
    "GrobidParser": "aiagentsforce_community.document_loaders.parsers.grobid",
    "LanguageParser": "aiagentsforce_community.document_loaders.parsers.language",
    "OpenAIWhisperParser": "aiagentsforce_community.document_loaders.parsers.audio",
    "PDFMinerParser": "aiagentsforce_community.document_loaders.parsers.pdf",
    "PDFPlumberParser": "aiagentsforce_community.document_loaders.parsers.pdf",
    "PyMuPDFParser": "aiagentsforce_community.document_loaders.parsers.pdf",
    "PyPDFParser": "aiagentsforce_community.document_loaders.parsers.pdf",
    "PyPDFium2Parser": "aiagentsforce_community.document_loaders.parsers.pdf",
    "VsdxParser": "aiagentsforce_community.document_loaders.parsers.vsdx",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")


__all__ = [
    "AzureAIDocumentIntelligenceParser",
    "BS4HTMLParser",
    "DocAIParser",
    "GrobidParser",
    "LanguageParser",
    "OpenAIWhisperParser",
    "PDFMinerParser",
    "PDFPlumberParser",
    "PyMuPDFParser",
    "PyPDFParser",
    "PyPDFium2Parser",
    "VsdxParser",
]
