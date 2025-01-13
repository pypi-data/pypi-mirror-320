"""**Callback handlers** allow listening to events in Aibaba AI.

**Class hierarchy:**

.. code-block::

    BaseCallbackHandler --> <name>CallbackHandler  # Example: AimCallbackHandler
"""

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from aiagentsforce_community.callbacks.aim_callback import (
        AimCallbackHandler,
    )
    from aiagentsforce_community.callbacks.argilla_callback import (
        ArgillaCallbackHandler,
    )
    from aiagentsforce_community.callbacks.arize_callback import (
        ArizeCallbackHandler,
    )
    from aiagentsforce_community.callbacks.arthur_callback import (
        ArthurCallbackHandler,
    )
    from aiagentsforce_community.callbacks.clearml_callback import (
        ClearMLCallbackHandler,
    )
    from aiagentsforce_community.callbacks.comet_ml_callback import (
        CometCallbackHandler,
    )
    from aiagentsforce_community.callbacks.context_callback import (
        ContextCallbackHandler,
    )
    from aiagentsforce_community.callbacks.fiddler_callback import (
        FiddlerCallbackHandler,
    )
    from aiagentsforce_community.callbacks.flyte_callback import (
        FlyteCallbackHandler,
    )
    from aiagentsforce_community.callbacks.human import (
        HumanApprovalCallbackHandler,
    )
    from aiagentsforce_community.callbacks.infino_callback import (
        InfinoCallbackHandler,
    )
    from aiagentsforce_community.callbacks.labelstudio_callback import (
        LabelStudioCallbackHandler,
    )
    from aiagentsforce_community.callbacks.llmonitor_callback import (
        LLMonitorCallbackHandler,
    )
    from aiagentsforce_community.callbacks.manager import (
        get_openai_callback,
        wandb_tracing_enabled,
    )
    from aiagentsforce_community.callbacks.mlflow_callback import (
        MlflowCallbackHandler,
    )
    from aiagentsforce_community.callbacks.openai_info import (
        OpenAICallbackHandler,
    )
    from aiagentsforce_community.callbacks.promptlayer_callback import (
        PromptLayerCallbackHandler,
    )
    from aiagentsforce_community.callbacks.sagemaker_callback import (
        SageMakerCallbackHandler,
    )
    from aiagentsforce_community.callbacks.streamlit import (
        LLMThoughtLabeler,
        StreamlitCallbackHandler,
    )
    from aiagentsforce_community.callbacks.trubrics_callback import (
        TrubricsCallbackHandler,
    )
    from aiagentsforce_community.callbacks.upstash_ratelimit_callback import (
        UpstashRatelimitError,
        UpstashRatelimitHandler,  # noqa: F401
    )
    from aiagentsforce_community.callbacks.uptrain_callback import (
        UpTrainCallbackHandler,
    )
    from aiagentsforce_community.callbacks.wandb_callback import (
        WandbCallbackHandler,
    )
    from aiagentsforce_community.callbacks.whylabs_callback import (
        WhyLabsCallbackHandler,
    )


_module_lookup = {
    "AimCallbackHandler": "aiagentsforce_community.callbacks.aim_callback",
    "ArgillaCallbackHandler": "aiagentsforce_community.callbacks.argilla_callback",
    "ArizeCallbackHandler": "aiagentsforce_community.callbacks.arize_callback",
    "ArthurCallbackHandler": "aiagentsforce_community.callbacks.arthur_callback",
    "ClearMLCallbackHandler": "aiagentsforce_community.callbacks.clearml_callback",
    "CometCallbackHandler": "aiagentsforce_community.callbacks.comet_ml_callback",
    "ContextCallbackHandler": "aiagentsforce_community.callbacks.context_callback",
    "FiddlerCallbackHandler": "aiagentsforce_community.callbacks.fiddler_callback",
    "FlyteCallbackHandler": "aiagentsforce_community.callbacks.flyte_callback",
    "HumanApprovalCallbackHandler": "aiagentsforce_community.callbacks.human",
    "InfinoCallbackHandler": "aiagentsforce_community.callbacks.infino_callback",
    "LLMThoughtLabeler": "aiagentsforce_community.callbacks.streamlit",
    "LLMonitorCallbackHandler": "aiagentsforce_community.callbacks.llmonitor_callback",
    "LabelStudioCallbackHandler": "aiagentsforce_community.callbacks.labelstudio_callback",
    "MlflowCallbackHandler": "aiagentsforce_community.callbacks.mlflow_callback",
    "OpenAICallbackHandler": "aiagentsforce_community.callbacks.openai_info",
    "PromptLayerCallbackHandler": "aiagentsforce_community.callbacks.promptlayer_callback",
    "SageMakerCallbackHandler": "aiagentsforce_community.callbacks.sagemaker_callback",
    "StreamlitCallbackHandler": "aiagentsforce_community.callbacks.streamlit",
    "TrubricsCallbackHandler": "aiagentsforce_community.callbacks.trubrics_callback",
    "UpstashRatelimitError": "aiagentsforce_community.callbacks.upstash_ratelimit_callback",
    "UpstashRatelimitHandler": "aiagentsforce_community.callbacks.upstash_ratelimit_callback",  # noqa
    "UpTrainCallbackHandler": "aiagentsforce_community.callbacks.uptrain_callback",
    "WandbCallbackHandler": "aiagentsforce_community.callbacks.wandb_callback",
    "WhyLabsCallbackHandler": "aiagentsforce_community.callbacks.whylabs_callback",
    "get_openai_callback": "aiagentsforce_community.callbacks.manager",
    "wandb_tracing_enabled": "aiagentsforce_community.callbacks.manager",
}


def __getattr__(name: str) -> Any:
    if name in _module_lookup:
        module = importlib.import_module(_module_lookup[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__} has no attribute {name}")


__all__ = [
    "AimCallbackHandler",
    "ArgillaCallbackHandler",
    "ArizeCallbackHandler",
    "ArthurCallbackHandler",
    "ClearMLCallbackHandler",
    "CometCallbackHandler",
    "ContextCallbackHandler",
    "FiddlerCallbackHandler",
    "FlyteCallbackHandler",
    "HumanApprovalCallbackHandler",
    "InfinoCallbackHandler",
    "LLMThoughtLabeler",
    "LLMonitorCallbackHandler",
    "LabelStudioCallbackHandler",
    "MlflowCallbackHandler",
    "OpenAICallbackHandler",
    "PromptLayerCallbackHandler",
    "SageMakerCallbackHandler",
    "StreamlitCallbackHandler",
    "TrubricsCallbackHandler",
    "UpstashRatelimitError",
    "UpstashRatelimitHandler",
    "UpTrainCallbackHandler",
    "WandbCallbackHandler",
    "WhyLabsCallbackHandler",
    "get_openai_callback",
    "wandb_tracing_enabled",
]
