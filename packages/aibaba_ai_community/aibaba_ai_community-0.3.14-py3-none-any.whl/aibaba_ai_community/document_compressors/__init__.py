import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiagentsforce_community.document_compressors.dashscope_rerank import (
        DashScopeRerank,
    )
    from aiagentsforce_community.document_compressors.flashrank_rerank import (
        FlashrankRerank,
    )
    from aiagentsforce_community.document_compressors.infinity_rerank import (
        InfinityRerank,
    )
    from aiagentsforce_community.document_compressors.jina_rerank import (
        JinaRerank,
    )
    from aiagentsforce_community.document_compressors.llmlingua_filter import (
        LLMLinguaCompressor,
    )
    from aiagentsforce_community.document_compressors.openvino_rerank import (
        OpenVINOReranker,
    )
    from aiagentsforce_community.document_compressors.rankllm_rerank import (
        RankLLMRerank,
    )
    from aiagentsforce_community.document_compressors.volcengine_rerank import (
        VolcengineRerank,
    )

_module_lookup = {
    "LLMLinguaCompressor": "aiagentsforce_community.document_compressors.llmlingua_filter",
    "OpenVINOReranker": "aiagentsforce_community.document_compressors.openvino_rerank",
    "JinaRerank": "aiagentsforce_community.document_compressors.jina_rerank",
    "RankLLMRerank": "aiagentsforce_community.document_compressors.rankllm_rerank",
    "FlashrankRerank": "aiagentsforce_community.document_compressors.flashrank_rerank",
    "DashScopeRerank": "aiagentsforce_community.document_compressors.dashscope_rerank",
    "VolcengineRerank": "aiagentsforce_community.document_compressors.volcengine_rerank",
    "InfinityRerank": "aiagentsforce_community.document_compressors.infinity_rerank",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")


__all__ = [
    "LLMLinguaCompressor",
    "OpenVINOReranker",
    "FlashrankRerank",
    "JinaRerank",
    "RankLLMRerank",
    "DashScopeRerank",
    "VolcengineRerank",
    "InfinityRerank",
]
