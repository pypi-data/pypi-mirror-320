"""**Chat Models** are a variation on language models.

While Chat Models use language models under the hood, the interface they expose
is a bit different. Rather than expose a "text in, text out" API, they expose
an interface where "chat messages" are the inputs and outputs.

**Class hierarchy:**

.. code-block::

    BaseLanguageModel --> BaseChatModel --> <name>  # Examples: ChatOpenAI, ChatGooglePalm

**Main helpers:**

.. code-block::

    AIMessage, BaseMessage, HumanMessage
"""  # noqa: E501

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiagentsforce_community.chat_models.anthropic import (
        ChatAnthropic,
    )
    from aiagentsforce_community.chat_models.anyscale import (
        ChatAnyscale,
    )
    from aiagentsforce_community.chat_models.azure_openai import (
        AzureChatOpenAI,
    )
    from aiagentsforce_community.chat_models.baichuan import (
        ChatBaichuan,
    )
    from aiagentsforce_community.chat_models.baidu_qianfan_endpoint import (
        QianfanChatEndpoint,
    )
    from aiagentsforce_community.chat_models.bedrock import (
        BedrockChat,
    )
    from aiagentsforce_community.chat_models.cohere import (
        ChatCohere,
    )
    from aiagentsforce_community.chat_models.coze import (
        ChatCoze,
    )
    from aiagentsforce_community.chat_models.databricks import (
        ChatDatabricks,
    )
    from aiagentsforce_community.chat_models.deepinfra import (
        ChatDeepInfra,
    )
    from aiagentsforce_community.chat_models.edenai import ChatEdenAI
    from aiagentsforce_community.chat_models.ernie import (
        ErnieBotChat,
    )
    from aiagentsforce_community.chat_models.everlyai import (
        ChatEverlyAI,
    )
    from aiagentsforce_community.chat_models.fake import (
        FakeListChatModel,
    )
    from aiagentsforce_community.chat_models.fireworks import (
        ChatFireworks,
    )
    from aiagentsforce_community.chat_models.friendli import (
        ChatFriendli,
    )
    from aiagentsforce_community.chat_models.gigachat import (
        GigaChat,
    )
    from aiagentsforce_community.chat_models.google_palm import (
        ChatGooglePalm,
    )
    from aiagentsforce_community.chat_models.gpt_router import (
        GPTRouter,
    )
    from aiagentsforce_community.chat_models.huggingface import (
        ChatHuggingFace,
    )
    from aiagentsforce_community.chat_models.human import (
        HumanInputChatModel,
    )
    from aiagentsforce_community.chat_models.hunyuan import (
        ChatHunyuan,
    )
    from aiagentsforce_community.chat_models.javelin_ai_gateway import (
        ChatJavelinAIGateway,
    )
    from aiagentsforce_community.chat_models.jinachat import (
        JinaChat,
    )
    from aiagentsforce_community.chat_models.kinetica import (
        ChatKinetica,
    )
    from aiagentsforce_community.chat_models.konko import (
        ChatKonko,
    )
    from aiagentsforce_community.chat_models.litellm import (
        ChatLiteLLM,
    )
    from aiagentsforce_community.chat_models.litellm_router import (
        ChatLiteLLMRouter,
    )
    from aiagentsforce_community.chat_models.llama_edge import (
        LlamaEdgeChatService,
    )
    from aiagentsforce_community.chat_models.llamacpp import ChatLlamaCpp
    from aiagentsforce_community.chat_models.maritalk import (
        ChatMaritalk,
    )
    from aiagentsforce_community.chat_models.minimax import (
        MiniMaxChat,
    )
    from aiagentsforce_community.chat_models.mlflow import (
        ChatMlflow,
    )
    from aiagentsforce_community.chat_models.mlflow_ai_gateway import (
        ChatMLflowAIGateway,
    )
    from aiagentsforce_community.chat_models.mlx import (
        ChatMLX,
    )
    from aiagentsforce_community.chat_models.moonshot import (
        MoonshotChat,
    )
    from aiagentsforce_community.chat_models.naver import (
        ChatClovaX,
    )
    from aiagentsforce_community.chat_models.oci_data_science import (
        ChatOCIModelDeployment,
        ChatOCIModelDeploymentTGI,
        ChatOCIModelDeploymentVLLM,
    )
    from aiagentsforce_community.chat_models.oci_generative_ai import (
        ChatOCIGenAI,  # noqa: F401
    )
    from aiagentsforce_community.chat_models.octoai import ChatOctoAI
    from aiagentsforce_community.chat_models.ollama import (
        ChatOllama,
    )
    from aiagentsforce_community.chat_models.openai import (
        ChatOpenAI,
    )
    from aiagentsforce_community.chat_models.outlines import ChatOutlines
    from aiagentsforce_community.chat_models.pai_eas_endpoint import (
        PaiEasChatEndpoint,
    )
    from aiagentsforce_community.chat_models.perplexity import (
        ChatPerplexity,
    )
    from aiagentsforce_community.chat_models.premai import (
        ChatPremAI,
    )
    from aiagentsforce_community.chat_models.promptlayer_openai import (
        PromptLayerChatOpenAI,
    )
    from aiagentsforce_community.chat_models.reka import (
        ChatReka,
    )
    from aiagentsforce_community.chat_models.sambanova import (
        ChatSambaNovaCloud,
        ChatSambaStudio,
    )
    from aiagentsforce_community.chat_models.snowflake import (
        ChatSnowflakeCortex,
    )
    from aiagentsforce_community.chat_models.solar import (
        SolarChat,
    )
    from aiagentsforce_community.chat_models.sparkllm import (
        ChatSparkLLM,
    )
    from aiagentsforce_community.chat_models.symblai_nebula import ChatNebula
    from aiagentsforce_community.chat_models.tongyi import (
        ChatTongyi,
    )
    from aiagentsforce_community.chat_models.vertexai import (
        ChatVertexAI,
    )
    from aiagentsforce_community.chat_models.volcengine_maas import (
        VolcEngineMaasChat,
    )
    from aiagentsforce_community.chat_models.yandex import (
        ChatYandexGPT,
    )
    from aiagentsforce_community.chat_models.yi import (
        ChatYi,
    )
    from aiagentsforce_community.chat_models.yuan2 import (
        ChatYuan2,
    )
    from aiagentsforce_community.chat_models.zhipuai import (
        ChatZhipuAI,
    )
__all__ = [
    "AzureChatOpenAI",
    "BedrockChat",
    "ChatAnthropic",
    "ChatAnyscale",
    "ChatBaichuan",
    "ChatClovaX",
    "ChatCohere",
    "ChatCoze",
    "ChatOctoAI",
    "ChatDatabricks",
    "ChatDeepInfra",
    "ChatEdenAI",
    "ChatEverlyAI",
    "ChatFireworks",
    "ChatFriendli",
    "ChatGooglePalm",
    "ChatHuggingFace",
    "ChatHunyuan",
    "ChatJavelinAIGateway",
    "ChatKinetica",
    "ChatKonko",
    "ChatLiteLLM",
    "ChatLiteLLMRouter",
    "ChatMLX",
    "ChatMLflowAIGateway",
    "ChatMaritalk",
    "ChatMlflow",
    "ChatNebula",
    "ChatOCIGenAI",
    "ChatOCIModelDeployment",
    "ChatOCIModelDeploymentVLLM",
    "ChatOCIModelDeploymentTGI",
    "ChatOllama",
    "ChatOpenAI",
    "ChatOutlines",
    "ChatPerplexity",
    "ChatReka",
    "ChatPremAI",
    "ChatSambaNovaCloud",
    "ChatSambaStudio",
    "ChatSparkLLM",
    "ChatSnowflakeCortex",
    "ChatTongyi",
    "ChatVertexAI",
    "ChatYandexGPT",
    "ChatYuan2",
    "ChatZhipuAI",
    "ChatLlamaCpp",
    "ErnieBotChat",
    "FakeListChatModel",
    "GPTRouter",
    "GigaChat",
    "HumanInputChatModel",
    "JinaChat",
    "LlamaEdgeChatService",
    "MiniMaxChat",
    "MoonshotChat",
    "PaiEasChatEndpoint",
    "PromptLayerChatOpenAI",
    "QianfanChatEndpoint",
    "SolarChat",
    "VolcEngineMaasChat",
    "ChatYi",
]


_module_lookup = {
    "AzureChatOpenAI": "aiagentsforce_community.chat_models.azure_openai",
    "BedrockChat": "aiagentsforce_community.chat_models.bedrock",
    "ChatAnthropic": "aiagentsforce_community.chat_models.anthropic",
    "ChatAnyscale": "aiagentsforce_community.chat_models.anyscale",
    "ChatBaichuan": "aiagentsforce_community.chat_models.baichuan",
    "ChatClovaX": "aiagentsforce_community.chat_models.naver",
    "ChatCohere": "aiagentsforce_community.chat_models.cohere",
    "ChatCoze": "aiagentsforce_community.chat_models.coze",
    "ChatDatabricks": "aiagentsforce_community.chat_models.databricks",
    "ChatDeepInfra": "aiagentsforce_community.chat_models.deepinfra",
    "ChatEverlyAI": "aiagentsforce_community.chat_models.everlyai",
    "ChatEdenAI": "aiagentsforce_community.chat_models.edenai",
    "ChatFireworks": "aiagentsforce_community.chat_models.fireworks",
    "ChatFriendli": "aiagentsforce_community.chat_models.friendli",
    "ChatGooglePalm": "aiagentsforce_community.chat_models.google_palm",
    "ChatHuggingFace": "aiagentsforce_community.chat_models.huggingface",
    "ChatHunyuan": "aiagentsforce_community.chat_models.hunyuan",
    "ChatJavelinAIGateway": "aiagentsforce_community.chat_models.javelin_ai_gateway",
    "ChatKinetica": "aiagentsforce_community.chat_models.kinetica",
    "ChatKonko": "aiagentsforce_community.chat_models.konko",
    "ChatLiteLLM": "aiagentsforce_community.chat_models.litellm",
    "ChatLiteLLMRouter": "aiagentsforce_community.chat_models.litellm_router",
    "ChatMLflowAIGateway": "aiagentsforce_community.chat_models.mlflow_ai_gateway",
    "ChatMLX": "aiagentsforce_community.chat_models.mlx",
    "ChatMaritalk": "aiagentsforce_community.chat_models.maritalk",
    "ChatMlflow": "aiagentsforce_community.chat_models.mlflow",
    "ChatNebula": "aiagentsforce_community.chat_models.symblai_nebula",
    "ChatOctoAI": "aiagentsforce_community.chat_models.octoai",
    "ChatOCIGenAI": "aiagentsforce_community.chat_models.oci_generative_ai",
    "ChatOCIModelDeployment": "aiagentsforce_community.chat_models.oci_data_science",
    "ChatOCIModelDeploymentVLLM": "aiagentsforce_community.chat_models.oci_data_science",
    "ChatOCIModelDeploymentTGI": "aiagentsforce_community.chat_models.oci_data_science",
    "ChatOllama": "aiagentsforce_community.chat_models.ollama",
    "ChatOpenAI": "aiagentsforce_community.chat_models.openai",
    "ChatOutlines": "aiagentsforce_community.chat_models.outlines",
    "ChatReka": "aiagentsforce_community.chat_models.reka",
    "ChatPerplexity": "aiagentsforce_community.chat_models.perplexity",
    "ChatSambaNovaCloud": "aiagentsforce_community.chat_models.sambanova",
    "ChatSambaStudio": "aiagentsforce_community.chat_models.sambanova",
    "ChatSnowflakeCortex": "aiagentsforce_community.chat_models.snowflake",
    "ChatSparkLLM": "aiagentsforce_community.chat_models.sparkllm",
    "ChatTongyi": "aiagentsforce_community.chat_models.tongyi",
    "ChatVertexAI": "aiagentsforce_community.chat_models.vertexai",
    "ChatYandexGPT": "aiagentsforce_community.chat_models.yandex",
    "ChatYuan2": "aiagentsforce_community.chat_models.yuan2",
    "ChatZhipuAI": "aiagentsforce_community.chat_models.zhipuai",
    "ErnieBotChat": "aiagentsforce_community.chat_models.ernie",
    "FakeListChatModel": "aiagentsforce_community.chat_models.fake",
    "GPTRouter": "aiagentsforce_community.chat_models.gpt_router",
    "GigaChat": "aiagentsforce_community.chat_models.gigachat",
    "HumanInputChatModel": "aiagentsforce_community.chat_models.human",
    "JinaChat": "aiagentsforce_community.chat_models.jinachat",
    "LlamaEdgeChatService": "aiagentsforce_community.chat_models.llama_edge",
    "MiniMaxChat": "aiagentsforce_community.chat_models.minimax",
    "MoonshotChat": "aiagentsforce_community.chat_models.moonshot",
    "PaiEasChatEndpoint": "aiagentsforce_community.chat_models.pai_eas_endpoint",
    "PromptLayerChatOpenAI": "aiagentsforce_community.chat_models.promptlayer_openai",
    "SolarChat": "aiagentsforce_community.chat_models.solar",
    "QianfanChatEndpoint": "aiagentsforce_community.chat_models.baidu_qianfan_endpoint",
    "VolcEngineMaasChat": "aiagentsforce_community.chat_models.volcengine_maas",
    "ChatPremAI": "aiagentsforce_community.chat_models.premai",
    "ChatLlamaCpp": "aiagentsforce_community.chat_models.llamacpp",
    "ChatYi": "aiagentsforce_community.chat_models.yi",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")
