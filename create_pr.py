import os
import textwrap

from msrest.authentication import BasicAuthentication
from azure.devops.connection import Connection
from azure.devops.v5_1.git.models import GitPullRequest, GitPullRequestSearchCriteria, Comment, GitPullRequestCommentThread

class AzureDevOpsInteractor(object):
    "The Class for AzureDevOpsInteractor"

    def __init__(self, token):
        credentials = BasicAuthentication("", token)
        connection = Connection("https://jet2tfs.visualstudio.com", creds=credentials)
        self._azdo_git_client = connection.clients.get_git_client()

    def get_repo(self, project, repo_name):
        "This gets the information on the repo"
        for remote in self._azdo_git_client.get_repositories(project=project):
            if remote.name == repo_name:
                return remote
        return None

    def load_repository(self, repo=None, project=None, branch=None):
        "Loads the repository and checks if there is a pull request"
        remote = self.get_repo(project, repo)
        self.branch_has_open_pull_request(remote.id, branch)

        return ManagedRepository(remote)


    def branch_has_open_pull_request(self, repo_id, branch):
        "checks for open pull requests and is called by load_repository"
        
        ref_head = (f"refs/heads/{branch}")
        pr_search_criteria = GitPullRequestSearchCriteria(repository_id=repo_id, source_ref_name=ref_head)
        get_active_prs = self._azdo_git_client.get_pull_requests(repo_id, pr_search_criteria)
        if len(get_active_prs) <= 0:
            get_active_prs.append(self.create_pull_request(repo_id, f"RouteToLive: {branch}", self.pr_description(), branch, "develop"))
            self.check_for_threads(repo_id, get_active_prs[0].id)
        return get_active_prs

    def check_for_threads(self, repo_id, get_active_prs):
        
        pr_id= get_active_prs[0].id
        COMMIT_SHA = os.environ["COMMIT_SHA"]
        initial_comment = Comment(content=COMMIT_SHA)
        thread = GitPullRequestCommentThread(comments=[initial_comment])
        threads = self._azdo_git_client.get_threads(repo_id, pr_id[0].id)

        for thread in threads:
            comments =  self._azdo_git_client.get_comments(repo_id, pr_id, thread["id"])
            commit_message=any(x.message ==COMMIT_SHA for x in comments.messages)
            if commit_message == None:
                thread = self.create_thread(repo_id, COMMIT_SHA,get_active_prs)
            return thread

    def create_thread(self, repo_id, COMMIT_SHA,get_active_prs):
        thread = GitPullRequestCommentThread(comments=COMMIT_SHA)
        thread_id = self._azdo_git_client.create_thread(thread, repo_id, pr_id).as_dict()["id"]
        return thread_id

    def create_pull_request(self, repo_id, title, description, from_branch, to_branch, is_draft=True):
        "This creates the pull request and returns it"
        pr_create = GitPullRequest(title=title, source_ref_name=f"refs/heads/{from_branch}", target_ref_name=f"refs/heads/{to_branch}", description=self.pr_description(), is_draft=is_draft)
        return self._azdo_git_client.create_pull_request(pr_create, repo_id)

    def pr_description(self, artifact="Pending", notes="Pending", build="Pending", code_quality="Pending", unit_test="Pending", unit_coverage="Pending", scan="Pending", publish="Pending", review="Pending", product_owner="Pending",
                       dba_review="Pending", team_ready="Pending", integration_test="Pending", ops_ready="Pending", test_signoff="Pending", release_ready="Pending", regression_test="Pending"):
        "This is the pull request description"
        return textwrap.dedent(f"""
                ## Release Notes
                ## Status

                {artifact} Artifact is valid
                {notes} Release notes updated
                {build} Artifact is built
                {code_quality} Code Quality Pass
                {unit_test} Unit Tests Pass
                {unit_coverage} Unit Test Coverage Pass
                {scan} Security Scan Pass
                {publish} Artifact is published
                {review} Developer Code Review Pass
                {product_owner} PO Signoff
                {dba_review} DBA Code Review Pass
                {team_ready} Ready for Release
                {integration_test} Integration Test Passed
                {ops_ready} Operational Acceptance Pass
                {test_signoff} Test Lead Review Pass
                {release_ready} Handover to Operations Completed
                {regression_test} Regression Test Passed
            """)


class ManagedRepository(object):
    "This is the main managed repository class"
    def __init__(self, azdo_repo):
        self._repo = azdo_repo

if __name__ == "__main__":

    CLIENT = AzureDevOpsInteractor(os.environ["AZDO_TOKEN"])
    CLIENT.load_repository(os.environ["REPO_NAME"], os.environ["PROJECT"], os.environ["BRANCH"])
