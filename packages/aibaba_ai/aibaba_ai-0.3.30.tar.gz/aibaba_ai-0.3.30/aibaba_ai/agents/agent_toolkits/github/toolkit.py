from typing import TYPE_CHECKING, Any

from langchain._api import create_importer

if TYPE_CHECKING:
    from aiagentsforce_community.agent_toolkits.github.toolkit import (
        BranchName,
        CommentOnIssue,
        CreateFile,
        CreatePR,
        CreateReviewRequest,
        DeleteFile,
        DirectoryPath,
        GetIssue,
        GetPR,
        GitHubToolkit,
        NoInput,
        ReadFile,
        SearchCode,
        SearchIssuesAndPRs,
        UpdateFile,
    )

# Create a way to dynamically look up deprecated imports.
# Used to consolidate logic for raising deprecation warnings and
# handling optional imports.
DEPRECATED_LOOKUP = {
    "NoInput": "aiagentsforce_community.agent_toolkits.github.toolkit",
    "GetIssue": "aiagentsforce_community.agent_toolkits.github.toolkit",
    "CommentOnIssue": "aiagentsforce_community.agent_toolkits.github.toolkit",
    "GetPR": "aiagentsforce_community.agent_toolkits.github.toolkit",
    "CreatePR": "aiagentsforce_community.agent_toolkits.github.toolkit",
    "CreateFile": "aiagentsforce_community.agent_toolkits.github.toolkit",
    "ReadFile": "aiagentsforce_community.agent_toolkits.github.toolkit",
    "UpdateFile": "aiagentsforce_community.agent_toolkits.github.toolkit",
    "DeleteFile": "aiagentsforce_community.agent_toolkits.github.toolkit",
    "DirectoryPath": "aiagentsforce_community.agent_toolkits.github.toolkit",
    "BranchName": "aiagentsforce_community.agent_toolkits.github.toolkit",
    "SearchCode": "aiagentsforce_community.agent_toolkits.github.toolkit",
    "CreateReviewRequest": "aiagentsforce_community.agent_toolkits.github.toolkit",
    "SearchIssuesAndPRs": "aiagentsforce_community.agent_toolkits.github.toolkit",
    "GitHubToolkit": "aiagentsforce_community.agent_toolkits.github.toolkit",
}

_import_attribute = create_importer(__package__, deprecated_lookups=DEPRECATED_LOOKUP)


def __getattr__(name: str) -> Any:
    """Look up attributes dynamically."""
    return _import_attribute(name)


__all__ = [
    "NoInput",
    "GetIssue",
    "CommentOnIssue",
    "GetPR",
    "CreatePR",
    "CreateFile",
    "ReadFile",
    "UpdateFile",
    "DeleteFile",
    "DirectoryPath",
    "BranchName",
    "SearchCode",
    "CreateReviewRequest",
    "SearchIssuesAndPRs",
    "GitHubToolkit",
]
