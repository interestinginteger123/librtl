import uuid
import os

from librtl.azdo import AzureDevOpsInteractor

@when(u'I make a new commit to \'feature/Utopia\'')
def step_impl(context):
    filename = str(uuid.uuid4())
    context.repo.checkout("feature/Utopia")
    context.repo.add_file(filename, "Hello, World!")
    context.repo.commit("Greetings")
    context.repo.push()

@when(u'I trigger a PR update for that commit')
def step_impl(context):
    comment = "1.0.0"
    context.client.create_thread(context.repo.project, context.repo.name, "feature/Utopia", "develop", comment)

@then(u'the Pull Request "RouteToLive: feature/Utopia" has a new thread')
def step_impl(context):
    context.pr_threads = context.client.get_threads(context.repo.project, context.repo.name, "feature/Utopia", "develop")
    assert len(context.pr_threads) == 1

@then(u'that thread has an initial comment including the formatted name of the built artifact')
def step_impl(context):
    assert "1.0.0" == context.pr_threads[0]["comments"][0].as_dict()["content"]

@given(u'I have an empty Azure Devops Git Repo')
def step_impl(context):
    project_name = "RunwayTest"
    repo_name = str(uuid.uuid4())
    client = AzureDevOpsInteractor(os.environ["AZDO_TOKEN"])
    repo = client.create_repo(project_name, repo_name)
    repo.create_branch('develop')
    context.client = client
    context.repo = repo

@given(u'there is a new branch named \'feature/Utopia\'')
def step_impl(context):
    context.repo.create_branch('feature/Utopia')

@when(u'I create a pull request from \'feature/Utopia\' to \'develop\'')
def step_impl(context):
    context.client.create_pull_request(context.repo.project, context.repo.id, 'feature/Utopia', 'develop')

@then(u'there is an Azure Devops Pull Request with the title "RouteToLive: feature/Utopia"')
def step_impl(context):
    context.get_pr = context.client.load_pull_request(context.repo.project, context.repo.name, 'RouteToLive: feature/Utopia')
    assert context.get_pr is not None

@then(u'that Pull Request goes from feature/Utopia to develop')
def step_impl(context):
    assert context.get_pr["source_ref_name"] == 'refs/heads/feature/Utopia'
    assert context.get_pr["target_ref_name"] == 'refs/heads/develop'

@then(u'that Pull Request has the \'Draft\' status')
def step_impl(context):
    assert context.get_pr["is_draft"]
