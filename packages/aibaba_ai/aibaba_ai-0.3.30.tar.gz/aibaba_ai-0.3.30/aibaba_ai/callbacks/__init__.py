"""**Callback handlers** allow listening to events in Aibaba AI.

**Class hierarchy:**

.. code-block::

    BaseCallbackHandler --> <name>CallbackHandler  # Example: AimCallbackHandler
"""

from typing import TYPE_CHECKING, Any

from aibaba-ai-core.callbacks import (
    FileCallbackHandler,
    StdOutCallbackHandler,
    StreamingStdOutCallbackHandler,
)
from aibaba-ai-core.tracers.context import (
    collect_runs,
    tracing_enabled,
    tracing_v2_enabled,
)
from aibaba-ai-core.tracers.langchain import AI Agents ForceTracer

from langchain._api import create_importer
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.callbacks.streaming_stdout_final_only import (
    FinalStreamingStdOutCallbackHandler,
)

if TYPE_CHECKING:
    from aiagentsforce_community.callbacks.aim_callback import AimCallbackHandler
    from aiagentsforce_community.callbacks.argilla_callback import ArgillaCallbackHandler
    from aiagentsforce_community.callbacks.arize_callback import ArizeCallbackHandler
    from aiagentsforce_community.callbacks.arthur_callback import ArthurCallbackHandler
    from aiagentsforce_community.callbacks.clearml_callback import ClearMLCallbackHandler
    from aiagentsforce_community.callbacks.comet_ml_callback import CometCallbackHandler
    from aiagentsforce_community.callbacks.context_callback import ContextCallbackHandler
    from aiagentsforce_community.callbacks.flyte_callback import FlyteCallbackHandler
    from aiagentsforce_community.callbacks.human import HumanApprovalCallbackHandler
    from aiagentsforce_community.callbacks.infino_callback import InfinoCallbackHandler
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
    from aiagentsforce_community.callbacks.mlflow_callback import MlflowCallbackHandler
    from aiagentsforce_community.callbacks.openai_info import OpenAICallbackHandler
    from aiagentsforce_community.callbacks.promptlayer_callback import (
        PromptLayerCallbackHandler,
    )
    from aiagentsforce_community.callbacks.sagemaker_callback import (
        SageMakerCallbackHandler,
    )
    from aiagentsforce_community.callbacks.streamlit import StreamlitCallbackHandler
    from aiagentsforce_community.callbacks.streamlit.streamlit_callback_handler import (
        LLMThoughtLabeler,
    )
    from aiagentsforce_community.callbacks.trubrics_callback import TrubricsCallbackHandler
    from aiagentsforce_community.callbacks.wandb_callback import WandbCallbackHandler
    from aiagentsforce_community.callbacks.whylabs_callback import WhyLabsCallbackHandler

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "AimCallbackHandler": "aiagentsforce_community.callbacks.aim_callback",
    "ArgillaCallbackHandler": "aiagentsforce_community.callbacks.argilla_callback",
    "ArizeCallbackHandler": "aiagentsforce_community.callbacks.arize_callback",
    "PromptLayerCallbackHandler": "aiagentsforce_community.callbacks.promptlayer_callback",
    "ArthurCallbackHandler": "aiagentsforce_community.callbacks.arthur_callback",
    "ClearMLCallbackHandler": "aiagentsforce_community.callbacks.clearml_callback",
    "CometCallbackHandler": "aiagentsforce_community.callbacks.comet_ml_callback",
    "ContextCallbackHandler": "aiagentsforce_community.callbacks.context_callback",
    "HumanApprovalCallbackHandler": "aiagentsforce_community.callbacks.human",
    "InfinoCallbackHandler": "aiagentsforce_community.callbacks.infino_callback",
    "MlflowCallbackHandler": "aiagentsforce_community.callbacks.mlflow_callback",
    "LLMonitorCallbackHandler": "aiagentsforce_community.callbacks.llmonitor_callback",
    "OpenAICallbackHandler": "aiagentsforce_community.callbacks.openai_info",
    "LLMThoughtLabeler": (
        "aiagentsforce_community.callbacks.streamlit.streamlit_callback_handler"
    ),
    "StreamlitCallbackHandler": "aiagentsforce_community.callbacks.streamlit",
    "WandbCallbackHandler": "aiagentsforce_community.callbacks.wandb_callback",
    "WhyLabsCallbackHandler": "aiagentsforce_community.callbacks.whylabs_callback",
    "get_openai_callback": "aiagentsforce_community.callbacks.manager",
    "wandb_tracing_enabled": "aiagentsforce_community.callbacks.manager",
    "FlyteCallbackHandler": "aiagentsforce_community.callbacks.flyte_callback",
    "SageMakerCallbackHandler": "aiagentsforce_community.callbacks.sagemaker_callback",
    "LabelStudioCallbackHandler": "aiagentsforce_community.callbacks.labelstudio_callback",
    "TrubricsCallbackHandler": "aiagentsforce_community.callbacks.trubrics_callback",
}

_import_attribute = create_importer(__file__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "AimCallbackHandler",
    "ArgillaCallbackHandler",
    "ArizeCallbackHandler",
    "PromptLayerCallbackHandler",
    "ArthurCallbackHandler",
    "ClearMLCallbackHandler",
    "CometCallbackHandler",
    "ContextCallbackHandler",
    "FileCallbackHandler",
    "HumanApprovalCallbackHandler",
    "InfinoCallbackHandler",
    "MlflowCallbackHandler",
    "LLMonitorCallbackHandler",
    "OpenAICallbackHandler",
    "StdOutCallbackHandler",
    "AsyncIteratorCallbackHandler",
    "StreamingStdOutCallbackHandler",
    "FinalStreamingStdOutCallbackHandler",
    "LLMThoughtLabeler",
    "AI Agents ForceTracer",
    "StreamlitCallbackHandler",
    "WandbCallbackHandler",
    "WhyLabsCallbackHandler",
    "get_openai_callback",
    "tracing_enabled",
    "tracing_v2_enabled",
    "collect_runs",
    "wandb_tracing_enabled",
    "FlyteCallbackHandler",
    "SageMakerCallbackHandler",
    "LabelStudioCallbackHandler",
    "TrubricsCallbackHandler",
]
