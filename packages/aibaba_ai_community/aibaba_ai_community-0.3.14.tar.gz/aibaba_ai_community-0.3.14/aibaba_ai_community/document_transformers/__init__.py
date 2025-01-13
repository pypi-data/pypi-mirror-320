"""**Document Transformers** are classes to transform Documents.

**Document Transformers** usually used to transform a lot of Documents in a single run.

**Class hierarchy:**

.. code-block::

    BaseDocumentTransformer --> <name>  # Examples: DoctranQATransformer, DoctranTextTranslator

**Main helpers:**

.. code-block::

    Document
"""  # noqa: E501

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiagentsforce_community.document_transformers.beautiful_soup_transformer import (
        BeautifulSoupTransformer,
    )
    from aiagentsforce_community.document_transformers.doctran_text_extract import (
        DoctranPropertyExtractor,
    )
    from aiagentsforce_community.document_transformers.doctran_text_qa import (
        DoctranQATransformer,
    )
    from aiagentsforce_community.document_transformers.doctran_text_translate import (
        DoctranTextTranslator,
    )
    from aiagentsforce_community.document_transformers.embeddings_redundant_filter import (
        EmbeddingsClusteringFilter,
        EmbeddingsRedundantFilter,
        get_stateful_documents,
    )
    from aiagentsforce_community.document_transformers.google_translate import (
        GoogleTranslateTransformer,
    )
    from aiagentsforce_community.document_transformers.html2text import (
        Html2TextTransformer,
    )
    from aiagentsforce_community.document_transformers.long_context_reorder import (
        LongContextReorder,
    )
    from aiagentsforce_community.document_transformers.markdownify import (
        MarkdownifyTransformer,
    )
    from aiagentsforce_community.document_transformers.nuclia_text_transform import (
        NucliaTextTransformer,
    )
    from aiagentsforce_community.document_transformers.openai_functions import (
        OpenAIMetadataTagger,
    )

__all__ = [
    "BeautifulSoupTransformer",
    "DoctranPropertyExtractor",
    "DoctranQATransformer",
    "DoctranTextTranslator",
    "EmbeddingsClusteringFilter",
    "EmbeddingsRedundantFilter",
    "GoogleTranslateTransformer",
    "Html2TextTransformer",
    "LongContextReorder",
    "MarkdownifyTransformer",
    "NucliaTextTransformer",
    "OpenAIMetadataTagger",
    "get_stateful_documents",
]

_module_lookup = {
    "BeautifulSoupTransformer": "aiagentsforce_community.document_transformers.beautiful_soup_transformer",  # noqa: E501
    "DoctranPropertyExtractor": "aiagentsforce_community.document_transformers.doctran_text_extract",  # noqa: E501
    "DoctranQATransformer": "aiagentsforce_community.document_transformers.doctran_text_qa",
    "DoctranTextTranslator": "aiagentsforce_community.document_transformers.doctran_text_translate",  # noqa: E501
    "EmbeddingsClusteringFilter": "aiagentsforce_community.document_transformers.embeddings_redundant_filter",  # noqa: E501
    "EmbeddingsRedundantFilter": "aiagentsforce_community.document_transformers.embeddings_redundant_filter",  # noqa: E501
    "GoogleTranslateTransformer": "aiagentsforce_community.document_transformers.google_translate",  # noqa: E501
    "Html2TextTransformer": "aiagentsforce_community.document_transformers.html2text",
    "LongContextReorder": "aiagentsforce_community.document_transformers.long_context_reorder",  # noqa: E501
    "MarkdownifyTransformer": "aiagentsforce_community.document_transformers.markdownify",
    "NucliaTextTransformer": "aiagentsforce_community.document_transformers.nuclia_text_transform",  # noqa: E501
    "OpenAIMetadataTagger": "aiagentsforce_community.document_transformers.openai_functions",  # noqa: E501
    "get_stateful_documents": "aiagentsforce_community.document_transformers.embeddings_redundant_filter",  # noqa: E501
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
