"""**Embedding models**  are wrappers around embedding models
from different APIs and services.

**Embedding models** can be LLMs or not.

**Class hierarchy:**

.. code-block::

    Embeddings --> <name>Embeddings  # Examples: OpenAIEmbeddings, HuggingFaceEmbeddings
"""

import importlib
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiagentsforce_community.embeddings.aleph_alpha import (
        AlephAlphaAsymmetricSemanticEmbedding,
        AlephAlphaSymmetricSemanticEmbedding,
    )
    from aiagentsforce_community.embeddings.anyscale import (
        AnyscaleEmbeddings,
    )
    from aiagentsforce_community.embeddings.ascend import (
        AscendEmbeddings,
    )
    from aiagentsforce_community.embeddings.awa import (
        AwaEmbeddings,
    )
    from aiagentsforce_community.embeddings.azure_openai import (
        AzureOpenAIEmbeddings,
    )
    from aiagentsforce_community.embeddings.baichuan import (
        BaichuanTextEmbeddings,
    )
    from aiagentsforce_community.embeddings.baidu_qianfan_endpoint import (
        QianfanEmbeddingsEndpoint,
    )
    from aiagentsforce_community.embeddings.bedrock import (
        BedrockEmbeddings,
    )
    from aiagentsforce_community.embeddings.bookend import (
        BookendEmbeddings,
    )
    from aiagentsforce_community.embeddings.clarifai import (
        ClarifaiEmbeddings,
    )
    from aiagentsforce_community.embeddings.clova import (
        ClovaEmbeddings,
    )
    from aiagentsforce_community.embeddings.cohere import (
        CohereEmbeddings,
    )
    from aiagentsforce_community.embeddings.dashscope import (
        DashScopeEmbeddings,
    )
    from aiagentsforce_community.embeddings.databricks import (
        DatabricksEmbeddings,
    )
    from aiagentsforce_community.embeddings.deepinfra import (
        DeepInfraEmbeddings,
    )
    from aiagentsforce_community.embeddings.edenai import (
        EdenAiEmbeddings,
    )
    from aiagentsforce_community.embeddings.elasticsearch import (
        ElasticsearchEmbeddings,
    )
    from aiagentsforce_community.embeddings.embaas import (
        EmbaasEmbeddings,
    )
    from aiagentsforce_community.embeddings.ernie import (
        ErnieEmbeddings,
    )
    from aiagentsforce_community.embeddings.fake import (
        DeterministicFakeEmbedding,
        FakeEmbeddings,
    )
    from aiagentsforce_community.embeddings.fastembed import (
        FastEmbedEmbeddings,
    )
    from aiagentsforce_community.embeddings.gigachat import (
        GigaChatEmbeddings,
    )
    from aiagentsforce_community.embeddings.google_palm import (
        GooglePalmEmbeddings,
    )
    from aiagentsforce_community.embeddings.gpt4all import (
        GPT4AllEmbeddings,
    )
    from aiagentsforce_community.embeddings.gradient_ai import (
        GradientEmbeddings,
    )
    from aiagentsforce_community.embeddings.huggingface import (
        HuggingFaceBgeEmbeddings,
        HuggingFaceEmbeddings,
        HuggingFaceInferenceAPIEmbeddings,
        HuggingFaceInstructEmbeddings,
    )
    from aiagentsforce_community.embeddings.huggingface_hub import (
        HuggingFaceHubEmbeddings,
    )
    from aiagentsforce_community.embeddings.hunyuan import (
        HunyuanEmbeddings,
    )
    from aiagentsforce_community.embeddings.infinity import (
        InfinityEmbeddings,
    )
    from aiagentsforce_community.embeddings.infinity_local import (
        InfinityEmbeddingsLocal,
    )
    from aiagentsforce_community.embeddings.ipex_llm import IpexLLMBgeEmbeddings
    from aiagentsforce_community.embeddings.itrex import (
        QuantizedBgeEmbeddings,
    )
    from aiagentsforce_community.embeddings.javelin_ai_gateway import (
        JavelinAIGatewayEmbeddings,
    )
    from aiagentsforce_community.embeddings.jina import (
        JinaEmbeddings,
    )
    from aiagentsforce_community.embeddings.johnsnowlabs import (
        JohnSnowLabsEmbeddings,
    )
    from aiagentsforce_community.embeddings.laser import (
        LaserEmbeddings,
    )
    from aiagentsforce_community.embeddings.llamacpp import (
        LlamaCppEmbeddings,
    )
    from aiagentsforce_community.embeddings.llamafile import (
        LlamafileEmbeddings,
    )
    from aiagentsforce_community.embeddings.llm_rails import (
        LLMRailsEmbeddings,
    )
    from aiagentsforce_community.embeddings.localai import (
        LocalAIEmbeddings,
    )
    from aiagentsforce_community.embeddings.minimax import (
        MiniMaxEmbeddings,
    )
    from aiagentsforce_community.embeddings.mlflow import (
        MlflowCohereEmbeddings,
        MlflowEmbeddings,
    )
    from aiagentsforce_community.embeddings.mlflow_gateway import (
        MlflowAIGatewayEmbeddings,
    )
    from aiagentsforce_community.embeddings.model2vec import (
        Model2vecEmbeddings,
    )
    from aiagentsforce_community.embeddings.modelscope_hub import (
        ModelScopeEmbeddings,
    )
    from aiagentsforce_community.embeddings.mosaicml import (
        MosaicMLInstructorEmbeddings,
    )
    from aiagentsforce_community.embeddings.naver import (
        ClovaXEmbeddings,
    )
    from aiagentsforce_community.embeddings.nemo import (
        NeMoEmbeddings,
    )
    from aiagentsforce_community.embeddings.nlpcloud import (
        NLPCloudEmbeddings,
    )
    from aiagentsforce_community.embeddings.oci_generative_ai import (
        OCIGenAIEmbeddings,
    )
    from aiagentsforce_community.embeddings.octoai_embeddings import (
        OctoAIEmbeddings,
    )
    from aiagentsforce_community.embeddings.ollama import (
        OllamaEmbeddings,
    )
    from aiagentsforce_community.embeddings.openai import (
        OpenAIEmbeddings,
    )
    from aiagentsforce_community.embeddings.openvino import (
        OpenVINOBgeEmbeddings,
        OpenVINOEmbeddings,
    )
    from aiagentsforce_community.embeddings.optimum_intel import (
        QuantizedBiEncoderEmbeddings,
    )
    from aiagentsforce_community.embeddings.oracleai import (
        OracleEmbeddings,
    )
    from aiagentsforce_community.embeddings.ovhcloud import (
        OVHCloudEmbeddings,
    )
    from aiagentsforce_community.embeddings.premai import (
        PremAIEmbeddings,
    )
    from aiagentsforce_community.embeddings.sagemaker_endpoint import (
        SagemakerEndpointEmbeddings,
    )
    from aiagentsforce_community.embeddings.sambanova import (
        SambaStudioEmbeddings,
    )
    from aiagentsforce_community.embeddings.self_hosted import (
        SelfHostedEmbeddings,
    )
    from aiagentsforce_community.embeddings.self_hosted_hugging_face import (
        SelfHostedHuggingFaceEmbeddings,
        SelfHostedHuggingFaceInstructEmbeddings,
    )
    from aiagentsforce_community.embeddings.sentence_transformer import (
        SentenceTransformerEmbeddings,
    )
    from aiagentsforce_community.embeddings.solar import (
        SolarEmbeddings,
    )
    from aiagentsforce_community.embeddings.spacy_embeddings import (
        SpacyEmbeddings,
    )
    from aiagentsforce_community.embeddings.sparkllm import (
        SparkLLMTextEmbeddings,
    )
    from aiagentsforce_community.embeddings.tensorflow_hub import (
        TensorflowHubEmbeddings,
    )
    from aiagentsforce_community.embeddings.textembed import (
        TextEmbedEmbeddings,
    )
    from aiagentsforce_community.embeddings.titan_takeoff import (
        TitanTakeoffEmbed,
    )
    from aiagentsforce_community.embeddings.vertexai import (
        VertexAIEmbeddings,
    )
    from aiagentsforce_community.embeddings.volcengine import (
        VolcanoEmbeddings,
    )
    from aiagentsforce_community.embeddings.voyageai import (
        VoyageEmbeddings,
    )
    from aiagentsforce_community.embeddings.xinference import (
        XinferenceEmbeddings,
    )
    from aiagentsforce_community.embeddings.yandex import (
        YandexGPTEmbeddings,
    )
    from aiagentsforce_community.embeddings.zhipuai import (
        ZhipuAIEmbeddings,
    )

__all__ = [
    "AlephAlphaAsymmetricSemanticEmbedding",
    "AlephAlphaSymmetricSemanticEmbedding",
    "AnyscaleEmbeddings",
    "AscendEmbeddings",
    "AwaEmbeddings",
    "AzureOpenAIEmbeddings",
    "BaichuanTextEmbeddings",
    "BedrockEmbeddings",
    "BookendEmbeddings",
    "ClarifaiEmbeddings",
    "ClovaEmbeddings",
    "ClovaXEmbeddings",
    "CohereEmbeddings",
    "DashScopeEmbeddings",
    "DatabricksEmbeddings",
    "DeepInfraEmbeddings",
    "DeterministicFakeEmbedding",
    "EdenAiEmbeddings",
    "ElasticsearchEmbeddings",
    "EmbaasEmbeddings",
    "ErnieEmbeddings",
    "FakeEmbeddings",
    "FastEmbedEmbeddings",
    "GPT4AllEmbeddings",
    "GigaChatEmbeddings",
    "GooglePalmEmbeddings",
    "GradientEmbeddings",
    "HuggingFaceBgeEmbeddings",
    "HuggingFaceEmbeddings",
    "HuggingFaceHubEmbeddings",
    "HuggingFaceInferenceAPIEmbeddings",
    "HuggingFaceInstructEmbeddings",
    "InfinityEmbeddings",
    "InfinityEmbeddingsLocal",
    "IpexLLMBgeEmbeddings",
    "JavelinAIGatewayEmbeddings",
    "JinaEmbeddings",
    "JohnSnowLabsEmbeddings",
    "LLMRailsEmbeddings",
    "LaserEmbeddings",
    "LlamaCppEmbeddings",
    "LlamafileEmbeddings",
    "LocalAIEmbeddings",
    "MiniMaxEmbeddings",
    "MlflowAIGatewayEmbeddings",
    "MlflowCohereEmbeddings",
    "MlflowEmbeddings",
    "Model2vecEmbeddings",
    "ModelScopeEmbeddings",
    "MosaicMLInstructorEmbeddings",
    "NLPCloudEmbeddings",
    "NeMoEmbeddings",
    "OCIGenAIEmbeddings",
    "OctoAIEmbeddings",
    "OllamaEmbeddings",
    "OpenAIEmbeddings",
    "OpenVINOBgeEmbeddings",
    "OpenVINOEmbeddings",
    "OracleEmbeddings",
    "OVHCloudEmbeddings",
    "PremAIEmbeddings",
    "QianfanEmbeddingsEndpoint",
    "QuantizedBgeEmbeddings",
    "QuantizedBiEncoderEmbeddings",
    "SagemakerEndpointEmbeddings",
    "SambaStudioEmbeddings",
    "SelfHostedEmbeddings",
    "SelfHostedHuggingFaceEmbeddings",
    "SelfHostedHuggingFaceInstructEmbeddings",
    "SentenceTransformerEmbeddings",
    "SolarEmbeddings",
    "SpacyEmbeddings",
    "SparkLLMTextEmbeddings",
    "TensorflowHubEmbeddings",
    "TextEmbedEmbeddings",
    "TitanTakeoffEmbed",
    "VertexAIEmbeddings",
    "VolcanoEmbeddings",
    "VoyageEmbeddings",
    "XinferenceEmbeddings",
    "YandexGPTEmbeddings",
    "ZhipuAIEmbeddings",
    "HunyuanEmbeddings",
]

_module_lookup = {
    "AlephAlphaAsymmetricSemanticEmbedding": "aiagentsforce_community.embeddings.aleph_alpha",  # noqa: E501
    "AlephAlphaSymmetricSemanticEmbedding": "aiagentsforce_community.embeddings.aleph_alpha",  # noqa: E501
    "AnyscaleEmbeddings": "aiagentsforce_community.embeddings.anyscale",
    "AwaEmbeddings": "aiagentsforce_community.embeddings.awa",
    "AzureOpenAIEmbeddings": "aiagentsforce_community.embeddings.azure_openai",
    "BaichuanTextEmbeddings": "aiagentsforce_community.embeddings.baichuan",
    "BedrockEmbeddings": "aiagentsforce_community.embeddings.bedrock",
    "BookendEmbeddings": "aiagentsforce_community.embeddings.bookend",
    "ClarifaiEmbeddings": "aiagentsforce_community.embeddings.clarifai",
    "ClovaEmbeddings": "aiagentsforce_community.embeddings.clova",
    "ClovaXEmbeddings": "aiagentsforce_community.embeddings.naver",
    "CohereEmbeddings": "aiagentsforce_community.embeddings.cohere",
    "DashScopeEmbeddings": "aiagentsforce_community.embeddings.dashscope",
    "DatabricksEmbeddings": "aiagentsforce_community.embeddings.databricks",
    "DeepInfraEmbeddings": "aiagentsforce_community.embeddings.deepinfra",
    "DeterministicFakeEmbedding": "aiagentsforce_community.embeddings.fake",
    "EdenAiEmbeddings": "aiagentsforce_community.embeddings.edenai",
    "ElasticsearchEmbeddings": "aiagentsforce_community.embeddings.elasticsearch",
    "EmbaasEmbeddings": "aiagentsforce_community.embeddings.embaas",
    "ErnieEmbeddings": "aiagentsforce_community.embeddings.ernie",
    "FakeEmbeddings": "aiagentsforce_community.embeddings.fake",
    "FastEmbedEmbeddings": "aiagentsforce_community.embeddings.fastembed",
    "GPT4AllEmbeddings": "aiagentsforce_community.embeddings.gpt4all",
    "GooglePalmEmbeddings": "aiagentsforce_community.embeddings.google_palm",
    "GradientEmbeddings": "aiagentsforce_community.embeddings.gradient_ai",
    "GigaChatEmbeddings": "aiagentsforce_community.embeddings.gigachat",
    "HuggingFaceBgeEmbeddings": "aiagentsforce_community.embeddings.huggingface",
    "HuggingFaceEmbeddings": "aiagentsforce_community.embeddings.huggingface",
    "HuggingFaceHubEmbeddings": "aiagentsforce_community.embeddings.huggingface_hub",
    "HuggingFaceInferenceAPIEmbeddings": "aiagentsforce_community.embeddings.huggingface",
    "HuggingFaceInstructEmbeddings": "aiagentsforce_community.embeddings.huggingface",
    "InfinityEmbeddings": "aiagentsforce_community.embeddings.infinity",
    "InfinityEmbeddingsLocal": "aiagentsforce_community.embeddings.infinity_local",
    "IpexLLMBgeEmbeddings": "aiagentsforce_community.embeddings.ipex_llm",
    "JavelinAIGatewayEmbeddings": "aiagentsforce_community.embeddings.javelin_ai_gateway",
    "JinaEmbeddings": "aiagentsforce_community.embeddings.jina",
    "JohnSnowLabsEmbeddings": "aiagentsforce_community.embeddings.johnsnowlabs",
    "LLMRailsEmbeddings": "aiagentsforce_community.embeddings.llm_rails",
    "LaserEmbeddings": "aiagentsforce_community.embeddings.laser",
    "LlamaCppEmbeddings": "aiagentsforce_community.embeddings.llamacpp",
    "LlamafileEmbeddings": "aiagentsforce_community.embeddings.llamafile",
    "LocalAIEmbeddings": "aiagentsforce_community.embeddings.localai",
    "MiniMaxEmbeddings": "aiagentsforce_community.embeddings.minimax",
    "MlflowAIGatewayEmbeddings": "aiagentsforce_community.embeddings.mlflow_gateway",
    "MlflowCohereEmbeddings": "aiagentsforce_community.embeddings.mlflow",
    "MlflowEmbeddings": "aiagentsforce_community.embeddings.mlflow",
    "Model2vecEmbeddings": "aiagentsforce_community.embeddings.model2vec",
    "ModelScopeEmbeddings": "aiagentsforce_community.embeddings.modelscope_hub",
    "MosaicMLInstructorEmbeddings": "aiagentsforce_community.embeddings.mosaicml",
    "NLPCloudEmbeddings": "aiagentsforce_community.embeddings.nlpcloud",
    "NeMoEmbeddings": "aiagentsforce_community.embeddings.nemo",
    "OCIGenAIEmbeddings": "aiagentsforce_community.embeddings.oci_generative_ai",
    "OctoAIEmbeddings": "aiagentsforce_community.embeddings.octoai_embeddings",
    "OllamaEmbeddings": "aiagentsforce_community.embeddings.ollama",
    "OpenAIEmbeddings": "aiagentsforce_community.embeddings.openai",
    "OpenVINOEmbeddings": "aiagentsforce_community.embeddings.openvino",
    "OpenVINOBgeEmbeddings": "aiagentsforce_community.embeddings.openvino",
    "QianfanEmbeddingsEndpoint": "aiagentsforce_community.embeddings.baidu_qianfan_endpoint",  # noqa: E501
    "QuantizedBgeEmbeddings": "aiagentsforce_community.embeddings.itrex",
    "QuantizedBiEncoderEmbeddings": "aiagentsforce_community.embeddings.optimum_intel",
    "OracleEmbeddings": "aiagentsforce_community.embeddings.oracleai",
    "OVHCloudEmbeddings": "aiagentsforce_community.embeddings.ovhcloud",
    "SagemakerEndpointEmbeddings": "aiagentsforce_community.embeddings.sagemaker_endpoint",
    "SambaStudioEmbeddings": "aiagentsforce_community.embeddings.sambanova",
    "SelfHostedEmbeddings": "aiagentsforce_community.embeddings.self_hosted",
    "SelfHostedHuggingFaceEmbeddings": "aiagentsforce_community.embeddings.self_hosted_hugging_face",  # noqa: E501
    "SelfHostedHuggingFaceInstructEmbeddings": "aiagentsforce_community.embeddings.self_hosted_hugging_face",  # noqa: E501
    "SentenceTransformerEmbeddings": "aiagentsforce_community.embeddings.sentence_transformer",  # noqa: E501
    "SolarEmbeddings": "aiagentsforce_community.embeddings.solar",
    "SpacyEmbeddings": "aiagentsforce_community.embeddings.spacy_embeddings",
    "SparkLLMTextEmbeddings": "aiagentsforce_community.embeddings.sparkllm",
    "TensorflowHubEmbeddings": "aiagentsforce_community.embeddings.tensorflow_hub",
    "VertexAIEmbeddings": "aiagentsforce_community.embeddings.vertexai",
    "VolcanoEmbeddings": "aiagentsforce_community.embeddings.volcengine",
    "VoyageEmbeddings": "aiagentsforce_community.embeddings.voyageai",
    "XinferenceEmbeddings": "aiagentsforce_community.embeddings.xinference",
    "TextEmbedEmbeddings": "aiagentsforce_community.embeddings.textembed",
    "TitanTakeoffEmbed": "aiagentsforce_community.embeddings.titan_takeoff",
    "PremAIEmbeddings": "aiagentsforce_community.embeddings.premai",
    "YandexGPTEmbeddings": "aiagentsforce_community.embeddings.yandex",
    "AscendEmbeddings": "aiagentsforce_community.embeddings.ascend",
    "ZhipuAIEmbeddings": "aiagentsforce_community.embeddings.zhipuai",
    "HunyuanEmbeddings": "aiagentsforce_community.embeddings.hunyuan",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")


logger = logging.getLogger(__name__)


# TODO: this is in here to maintain backwards compatibility
class HypotheticalDocumentEmbedder:
    def __init__(self, *args: Any, **kwargs: Any):
        logger.warning(
            "Using a deprecated class. Please use "
            "`from langchain.chains import HypotheticalDocumentEmbedder` instead"
        )
        from langchain.chains.hyde.base import HypotheticalDocumentEmbedder as H

        return H(*args, **kwargs)  # type: ignore

    @classmethod
    def from_llm(cls, *args: Any, **kwargs: Any) -> Any:
        logger.warning(
            "Using a deprecated class. Please use "
            "`from langchain.chains import HypotheticalDocumentEmbedder` instead"
        )
        from langchain.chains.hyde.base import HypotheticalDocumentEmbedder as H

        return H.from_llm(*args, **kwargs)
