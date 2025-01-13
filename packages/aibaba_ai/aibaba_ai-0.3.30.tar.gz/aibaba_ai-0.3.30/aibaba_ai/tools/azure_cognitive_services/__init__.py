"""Azure Cognitive Services Tools."""

from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.tools import (
        AzureCogsFormRecognizerTool,
        AzureCogsImageAnalysisTool,
        AzureCogsSpeech2TextTool,
        AzureCogsText2SpeechTool,
        AzureCogsTextAnalyticsHealthTool,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "AzureCogsImageAnalysisTool": "aiagentsforce_community.tools",
    "AzureCogsFormRecognizerTool": "aiagentsforce_community.tools",
    "AzureCogsSpeech2TextTool": "aiagentsforce_community.tools",
    "AzureCogsText2SpeechTool": "aiagentsforce_community.tools",
    "AzureCogsTextAnalyticsHealthTool": "aiagentsforce_community.tools",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "AzureCogsImageAnalysisTool",
    "AzureCogsFormRecognizerTool",
    "AzureCogsSpeech2TextTool",
    "AzureCogsText2SpeechTool",
    "AzureCogsTextAnalyticsHealthTool",
]
