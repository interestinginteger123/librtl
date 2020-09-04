import textwrap
import pdb
import os
import uuid
from unittest.mock import patch, MagicMock
from contextlib import contextmanager

import azure
import git
from pytest import raises
from azure.devops.v5_1.git.models import GitRepository, TeamProjectReference

from librtl.azdo import AzureDevOpsInteractor

def test_load_repo():
    token = os.environ["AZDO_TOKEN"]
    branch = ""
    repo = ""
    project = ""
    client = AzureDevOpsInteractor(token)
    with raises(azure.devops.exceptions.AzureDevOpsClientRequestError):
        test = client.load_repo(project, repo)

def test_get_repo():
    token = ""
    branch = ""
    repo = ""
    client = AzureDevOpsInteractor(token)
    with raises(azure.devops.exceptions.AzureDevOpsClientRequestError):
        test = client.get_repo(repo, branch)
        repo_name=test.name

def test_create_thread():
    dummy_token = "test-token"
    dummy_branch = "test-branch"
    dummy_repo = "test-repo"
    client = AzureDevOpsInteractor(dummy_token)
    client.pull_requests_for_repo = MagicMock()
    with patch.object(client, "create_thread", client.pull_requests_for_repo) as mock_create_thread:
        client.create_thread(dummy_repo, dummy_branch, "test-artifact-name", 1)
        mock_create_thread.assert_called_with("test-repo", "test-branch", "test-artifact-name", 1)
    return mock_create_thread

def test_invalid_token_fails():
    with raises(azure.devops.exceptions.AzureDevOpsServiceError):
        client = AzureDevOpsInteractor('test-token')
        client.load_repo("", "")
