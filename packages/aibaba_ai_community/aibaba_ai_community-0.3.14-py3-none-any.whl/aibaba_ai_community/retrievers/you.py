from typing import Any, List

from alibaba_ai_core.callbacks import (
    AsyncCallbackManagerForRetrieverRun,
    CallbackManagerForRetrieverRun,
)
from alibaba_ai_core.documents import Document
from alibaba_ai_core.retrievers import BaseRetriever

from aiagentsforce_community.utilities import YouSearchAPIWrapper


class YouRetriever(BaseRetriever, YouSearchAPIWrapper):
    """You.com Search API retriever.

    It wraps results() to get_relevant_documents
    It uses all YouSearchAPIWrapper arguments without any change.
    """

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
        **kwargs: Any,
    ) -> List[Document]:
        return self.results(query, run_manager=run_manager.get_child(), **kwargs)

    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: AsyncCallbackManagerForRetrieverRun,
        **kwargs: Any,
    ) -> List[Document]:
        results = await self.results_async(
            query, run_manager=run_manager.get_child(), **kwargs
        )
        return results
