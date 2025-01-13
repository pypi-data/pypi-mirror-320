"""Agent toolkits contain integrations with various resources and services.

Aibaba AI has a large ecosystem of integrations with various external resources
like local and remote file systems, APIs and databases.

These integrations allow developers to create versatile applications that combine the
power of LLMs with the ability to access, interact with and manipulate external
resources.

When developing an application, developers should inspect the capabilities and
permissions of the tools that underlie the given agent toolkit, and determine
whether permissions of the given toolkit are appropriate for the application.

See [Security](https://docs.aibaba.world/docs/security) for more information.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any

from aibaba-ai-core._api.path import as_import_path
from aibaba-ai-core.tools.retriever import create_retriever_tool

from langchain._api import create_importer
from langchain.agents.agent_toolkits.conversational_retrieval.openai_functions import (
    create_conversational_retrieval_agent,
)
from langchain.agents.agent_toolkits.vectorstore.base import (
    create_vectorstore_agent,
    create_vectorstore_router_agent,
)
from langchain.agents.agent_toolkits.vectorstore.toolkit import (
    VectorStoreInfo,
    VectorStoreRouterToolkit,
    VectorStoreToolkit,
)

if TYPE_CHECKING:
    from aiagentsforce_community.agent_toolkits.ainetwork.toolkit import AINetworkToolkit
    from aiagentsforce_community.agent_toolkits.amadeus.toolkit import AmadeusToolkit
    from aiagentsforce_community.agent_toolkits.azure_cognitive_services import (
        AzureCognitiveServicesToolkit,
    )
    from aiagentsforce_community.agent_toolkits.file_management.toolkit import (
        FileManagementToolkit,
    )
    from aiagentsforce_community.agent_toolkits.gmail.toolkit import GmailToolkit
    from aiagentsforce_community.agent_toolkits.jira.toolkit import JiraToolkit
    from aiagentsforce_community.agent_toolkits.json.base import create_json_agent
    from aiagentsforce_community.agent_toolkits.json.toolkit import JsonToolkit
    from aiagentsforce_community.agent_toolkits.multion.toolkit import MultionToolkit
    from aiagentsforce_community.agent_toolkits.nasa.toolkit import NasaToolkit
    from aiagentsforce_community.agent_toolkits.nla.toolkit import NLAToolkit
    from aiagentsforce_community.agent_toolkits.office365.toolkit import O365Toolkit
    from aiagentsforce_community.agent_toolkits.openapi.base import create_openapi_agent
    from aiagentsforce_community.agent_toolkits.openapi.toolkit import OpenAPIToolkit
    from aiagentsforce_community.agent_toolkits.playwright.toolkit import (
        PlayWrightBrowserToolkit,
    )
    from aiagentsforce_community.agent_toolkits.powerbi.base import create_pbi_agent
    from aiagentsforce_community.agent_toolkits.powerbi.chat_base import (
        create_pbi_chat_agent,
    )
    from aiagentsforce_community.agent_toolkits.powerbi.toolkit import PowerBIToolkit
    from aiagentsforce_community.agent_toolkits.slack.toolkit import SlackToolkit
    from aiagentsforce_community.agent_toolkits.spark_sql.base import create_spark_sql_agent
    from aiagentsforce_community.agent_toolkits.spark_sql.toolkit import SparkSQLToolkit
    from aiagentsforce_community.agent_toolkits.sql.base import create_sql_agent
    from aiagentsforce_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
    from aiagentsforce_community.agent_toolkits.steam.toolkit import SteamToolkit
    from aiagentsforce_community.agent_toolkits.zapier.toolkit import ZapierToolkit

DEPRECATED_AGENTS = [
    "create_csv_agent",
    "create_pandas_dataframe_agent",
    "create_xorbits_agent",
    "create_python_agent",
    "create_spark_dataframe_agent",
]

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "AINetworkToolkit": "aiagentsforce_community.agent_toolkits.ainetwork.toolkit",
    "AmadeusToolkit": "aiagentsforce_community.agent_toolkits.amadeus.toolkit",
    "AzureCognitiveServicesToolkit": (
        "aiagentsforce_community.agent_toolkits.azure_cognitive_services"
    ),
    "FileManagementToolkit": (
        "aiagentsforce_community.agent_toolkits.file_management.toolkit"
    ),
    "GmailToolkit": "aiagentsforce_community.agent_toolkits.gmail.toolkit",
    "JiraToolkit": "aiagentsforce_community.agent_toolkits.jira.toolkit",
    "JsonToolkit": "aiagentsforce_community.agent_toolkits.json.toolkit",
    "MultionToolkit": "aiagentsforce_community.agent_toolkits.multion.toolkit",
    "NasaToolkit": "aiagentsforce_community.agent_toolkits.nasa.toolkit",
    "NLAToolkit": "aiagentsforce_community.agent_toolkits.nla.toolkit",
    "O365Toolkit": "aiagentsforce_community.agent_toolkits.office365.toolkit",
    "OpenAPIToolkit": "aiagentsforce_community.agent_toolkits.openapi.toolkit",
    "PlayWrightBrowserToolkit": "aiagentsforce_community.agent_toolkits.playwright.toolkit",
    "PowerBIToolkit": "aiagentsforce_community.agent_toolkits.powerbi.toolkit",
    "SlackToolkit": "aiagentsforce_community.agent_toolkits.slack.toolkit",
    "SteamToolkit": "aiagentsforce_community.agent_toolkits.steam.toolkit",
    "SQLDatabaseToolkit": "aiagentsforce_community.agent_toolkits.sql.toolkit",
    "SparkSQLToolkit": "aiagentsforce_community.agent_toolkits.spark_sql.toolkit",
    "ZapierToolkit": "aiagentsforce_community.agent_toolkits.zapier.toolkit",
    "create_json_agent": "aiagentsforce_community.agent_toolkits.json.base",
    "create_openapi_agent": "aiagentsforce_community.agent_toolkits.openapi.base",
    "create_pbi_agent": "aiagentsforce_community.agent_toolkits.powerbi.base",
    "create_pbi_chat_agent": "aiagentsforce_community.agent_toolkits.powerbi.chat_base",
    "create_spark_sql_agent": "aiagentsforce_community.agent_toolkits.spark_sql.base",
    "create_sql_agent": "aiagentsforce_community.agent_toolkits.sql.base",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Get attr name."""
    if name in DEPRECATED_AGENTS:
        relative_path = as_import_path(Path(__file__).parent, suffix=name)
        old_path = "langchain." + relative_path
        new_path = "langchain_experimental." + relative_path
        raise ImportError(
            f"{name} has been moved to langchain experimental. "
            "See https://github.com/aibaba-ai/aibaba-ai/discussions/11680"
            "for more information.\n"
            f"Please update your import statement from: `{old_path}` to `{new_path}`."
        )
    return _import_attribute(name)


__all__ = [
    "AINetworkToolkit",
    "AmadeusToolkit",
    "AzureCognitiveServicesToolkit",
    "FileManagementToolkit",
    "GmailToolkit",
    "JiraToolkit",
    "JsonToolkit",
    "MultionToolkit",
    "NasaToolkit",
    "NLAToolkit",
    "O365Toolkit",
    "OpenAPIToolkit",
    "PlayWrightBrowserToolkit",
    "PowerBIToolkit",
    "SlackToolkit",
    "SteamToolkit",
    "SQLDatabaseToolkit",
    "SparkSQLToolkit",
    "VectorStoreInfo",
    "VectorStoreRouterToolkit",
    "VectorStoreToolkit",
    "ZapierToolkit",
    "create_json_agent",
    "create_openapi_agent",
    "create_pbi_agent",
    "create_pbi_chat_agent",
    "create_spark_sql_agent",
    "create_sql_agent",
    "create_vectorstore_agent",
    "create_vectorstore_router_agent",
    "create_conversational_retrieval_agent",
    "create_retriever_tool",
]
