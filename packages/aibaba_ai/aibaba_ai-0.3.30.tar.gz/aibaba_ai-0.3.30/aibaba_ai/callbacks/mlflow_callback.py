from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.callbacks.mlflow_callback import (
        MlflowCallbackHandler,
        MlflowLogger,
        analyze_text,
        construct_html_from_prompt_and_generation,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "analyze_text": "aiagentsforce_community.callbacks.mlflow_callback",
    "construct_html_from_prompt_and_generation": (
        "aiagentsforce_community.callbacks.mlflow_callback"
    ),
    "MlflowLogger": "aiagentsforce_community.callbacks.mlflow_callback",
    "MlflowCallbackHandler": "aiagentsforce_community.callbacks.mlflow_callback",
}

_import_attribute = create_importer(__file__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "analyze_text",
    "construct_html_from_prompt_and_generation",
    "MlflowLogger",
    "MlflowCallbackHandler",
]
