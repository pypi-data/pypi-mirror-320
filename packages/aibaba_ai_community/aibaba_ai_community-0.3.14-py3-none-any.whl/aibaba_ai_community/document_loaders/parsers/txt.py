"""Module for parsing text files.."""

from typing import Iterator

from alibaba_ai_core.documents import Document

from aiagentsforce_community.document_loaders.base import BaseBlobParser
from aiagentsforce_community.document_loaders.blob_loaders import Blob


class TextParser(BaseBlobParser):
    """Parser for text blobs."""

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:  # type: ignore[valid-type]
        """Lazily parse the blob."""
        yield Document(page_content=blob.as_string(), metadata={"source": blob.source})  # type: ignore[attr-defined]
