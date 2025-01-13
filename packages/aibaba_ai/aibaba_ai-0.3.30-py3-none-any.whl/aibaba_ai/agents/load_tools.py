from typing import Any

from langchain._api import create_importer

_importer = create_importer(
    __package__, fallback_module="aiagentsforce_community.agent_toolkits.load_tools"
)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _importer(name)
