"""This python script creates pull requests on Azure Devops this requires
Azure devops modules to work with the azure API.
"""
import textwrap

from msrest.authentication import BasicAuthentication
from azure.devops.connection import Connection
from azure.devops.v5_1.git.models import (
    GitPullRequest, GitPullRequestSearchCriteria, GitRepositoryCreateOptions,
    Comment, GitPullRequestCommentThread
)

from librtl.model import ManagedRepository

class PRStatus():
    """Simple Enumeration of the status a PR task can have with appropriate strings
    This will be used by the function pr_description for the status. There will be a
    different status called depending on the outcome of the test.
    """
    PASS = "Pass"
    FAIL = "Fail"
    PENDING = "Pending"
    

class AzureDevOpsInteractor():
    """Contains functions which use Azure DevOps
    """

    def __init__(self, token):
        """The __init__ function loads the credentials and does the authentication
        with the AzureDevOpsInteractor. The credentials are token based and are defined
        by AZDO_TOKEN environment varriable.
        """

        credentials = BasicAuthentication("", token)
        connection = Connection("https://jet2tfs.visualstudio.com", creds=credentials)
        self._azdo = connection.clients.get_git_client()

    def create_repo(self, project: str, name: str):
        """Create a new ManagedRepository inside the project

        :param project: name of the project
        :param name: name of the repo
        :returns: ManagedRepository
        """
        options = GitRepositoryCreateOptions(name=name)
        self._azdo.create_repository(options, project=project)
        return self.load_repo(project, name)

    def load_repo(self, project: str, name: str):
        """Create a ManagedRepository from the key identifiers of a GitRepository

        :param project: name of the project eg RunwayTest
        :param name: name of the repo eg WorldDomination
        :returns: ManagedRepository
        """
        return ManagedRepository(
            self._azdo.get_repository(repository_id=name, project=project),
            self.pull_requests_for_repo(project, name)
        )

    def pull_requests_for_repo(self, project: str, name: str):
        """Get a list of pull requests for the named repo

        Each pull request is created by GitPullRequest.as_dict()

        :param project: name of the project eg RunwayTest
        :param name: name of the repo eg WorldDomination
        :returns: list(dict)
        """
        repo_id = self._azdo.get_repository(repository_id=name, project=project).as_dict()["id"]
        pr_search = GitPullRequestSearchCriteria(repository_id=repo_id)
        results = []
        for result in self._azdo.get_pull_requests_by_project(project, pr_search, top=1000):
            results.append(result.as_dict())
        return results

    def create_thread(self, project: str, repo: str, source: str, destination: str, initial_comment: str):
        """Create a thread in an existing PR in Azure Devops

        :param project: name of the project eg RunwayTest
        :param repo: name of the repo eg WorldDomination
        :param source: name of the source branch eg feature/123-TacoTuesday
        :param destination: name of the destination branch eg develop
        :param initial_comment: the initial comment text in the thread
        :returns: dict representing the thread
        """
        pr = self.load_pull_request(project, repo, f"RouteToLive: {source}")
        thread = GitPullRequestCommentThread(comments=[Comment(content=initial_comment)])
        return self._azdo.create_thread(thread, repo, pr.pull_request_id, project=project).as_dict()

    def create_pull_request(
            self, project: str, repo: str, source: str, destination: str, is_draft=True):
        """Create a PR in azure devops

        The PR dict is created by GitPullRequest.as_dict().

        The branch arguments (source and destination) must not have the 'refs/heads/' prefix as
        this prefix is added by the method.

        The draft status should be set to false only for PRs currently progressing on the
        Route to Live at Dynamic environment level or after.

        :param project: name of the project eg RunwayTest
        :param repo: name of the repo eg WorldDomination
        :param source: name of the source branch eg feature/123-TacoTuesday
        :param destination: name of the destination branch eg develop
        :param is_draft: draft status on the PR [default=True]
        :returns: dict representing the pull request
        """
        repo_id = self._azdo.get_repository(repository_id=repo, project=project).as_dict()["id"]
        pr_create = GitPullRequest(
            title=f"RouteToLive: {source}",
            source_ref_name=f"refs/heads/{source}",
            target_ref_name=f"refs/heads/{destination}",
            description=AzureDevOpsInteractor.pr_description(),
            is_draft=is_draft
        )
        return self._azdo.create_pull_request(pr_create, repo_id)

    def load_pull_request(self, project: str, repo: str, title: str):
        """Load a single pull request as a dict using the title

        The PR dict is created by GitPullRequest.as_dict()

        :param project: name of the project eg RunwayTest
        :param repo: name of the repo eg WorldDomination
        :param title: title of the PR eg 'RouteToLive: feature/123-TacoTuesday'
        :returns: dict representing the pull request
        """
        for pr in self.pull_requests_for_repo(project, repo):
            if pr["title"] == title:
                return pr
        return None

    def get_repo(self, project: str, repo: str):
        """This function loads the repository which has been declared in there
        environment variables REPO_NAME and PROJECT. It uses the azdo_git_client to do this
        and will return details about the repository which is used in other functions to preform
        the required API requests.

        :param project: name of the project eg RunwayTest
        :param repo: name of the repo eg WorldDomination
        :returns: GitRepository
        """
        return self._azdo.get_repository(repository_id=repo, project=project)

    @staticmethod
    def pr_description(
            artifact=PRStatus.PENDING, notes=PRStatus.PENDING, build=PRStatus.PENDING,
            code_quality=PRStatus.PENDING, unit_test=PRStatus.PENDING,
            unit_coverage=PRStatus.PENDING, scan=PRStatus.PENDING, publish=PRStatus.PENDING,
            review=PRStatus.PENDING, product_owner=PRStatus.PENDING, dba_review=PRStatus.PENDING,
            team_ready=PRStatus.PENDING, integration_test=PRStatus.PENDING,
            ops_ready=PRStatus.PENDING, test_signoff=PRStatus.PENDING,
            release_ready=PRStatus.PENDING, regression_test=PRStatus.PENDING):
        """The pr_description function has number of things passed into it which
        are used to define the outcome and staus of a pull request. These will be changed
        depending on the outcome of a test and allows us to update pull requests with those details
        """
        return textwrap.dedent(f"""
                ## Release Notes
                ## Status

                {artifact} Artifact is valid
                {notes} Release notes updated
                {build} Artifact is built
                {code_quality} Code Quality
                {unit_test} Unit Tests
                {unit_coverage} Unit Test Coverage
                {scan} Security Scan
                {publish} Artifact is published
                {review} Developer Code Review
                {product_owner} PO Signoff
                {dba_review} DBA Code Review
                {team_ready} Ready for Release
                {integration_test} Integration Test
                {ops_ready} Operational Acceptance
                {test_signoff} Test Lead Review
                {release_ready} Handover to Operations Completed
                {regression_test} Regression Test
            """)
