"""Model objects for use by librtl
"""
import os
import uuid

from git import Repo
import jinja2

class Templater():
    """Create common strings from known templates
    """
    TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

    def __init__(self):
        self._env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(Templater.TEMPLATE_DIR)
        )

    def render(self, template, data):
        """Return a string of the template combined with the data
        """
        return self._env.get_template(template).render(**data)

TEMPLATER = Templater()

class ManagedRepository():
    """Model representing an Azure Devops Git Repository managed by librtl
    """

    def __init__(self, remote, pull_requests):
        self._remote = remote.as_dict()
        self._prs = pull_requests
        self._local = None
        self.id = self._remote["id"]
        self.project = self._remote["project"]["name"]
        self.name = self._remote["name"]
        self._check_config()

    def _check_config(self):
        local_path = os.path.join("/tmp", str(uuid.uuid4()))
        self._local = Repo.clone_from(self._remote["ssh_url"], local_path)
        if not self.has_folder("rtl"):
            self.add_folder("rtl")
        if not self.has_file("rtl/self.yaml"):
            self.add_file(
                "rtl/self.yaml",
                TEMPLATER.render(
                    "self.yaml",
                    {
                        "name": self._remote["name"],
                        "componentTemplate": "dotnet-core-stateless-microservice-api"
                    }
                )
            )
        if not self.has_file("rtl/Dockerfile.component"):
            self.add_file(
                "rtl/Dockerfile.component",
                TEMPLATER.render(
                    "Dockerfile.component",
                    {
                        "name": self._remote["name"]
                    }
                )
            )
        if not self.has_file("README.md"):
            self.add_file(
                "README.md",
                TEMPLATER.render(
                    "README.md",
                    {"name": self._remote["name"]}
                )
            )
        else:
            self.update_file(
                "README.md",
                TEMPLATER.render(
                    "README.md",
                    {"name": self._remote["name"]}
                )
            )
        self._local.index.add(["rtl", "README.md"])
        self._local.index.commit("Add essential files for NewRouteToLive")
        self._local.git.push()
        if not self.has_branch("develop"):
            self.create_branch("develop")

    def checkout(self, name):
        """git checkout branch
        """
        self._local.git.checkout(name)

    def commit(self, message):
        """git commit
        """
        self._local.git.commit('-m', message)

    def push(self):
        """git push
        """
        self._local.git.push()

    def has_branch(self, name):
        """Returns True if branch exists in the remote
        """
        return f"refs/remotes/origin/{name}" in self._local.remotes.origin.refs

    def create_branch(self, name, src="master"):
        """Create a branch in the managed repository
        """
        self._local.git.checkout(src)
        self._local.create_head(name)
        self._local.git.checkout(name)
        self._local.git.push("--set-upstream", "origin", name)

    def has_file(self, path):
        """Returns True if path exists and is a file
        """
        fpath = os.path.join(self._local.working_tree_dir, path)
        return os.path.exists(fpath) and os.path.isfile(fpath)

    def add_file(self, path, content):
        """Adds a file with the content at the path
        """
        with open(os.path.join(self._local.working_tree_dir, path), "a+") as opf:
            opf.write(content)
        self._local.git.add(path)

    def update_file(self, path, additional_content):
        """Update an existing file in place
        """
        self.add_file(path, additional_content)
        self._local.git.add(path)

    def has_folder(self, path):
        """Returns True if path exists and is a folder
        """
        fpath = os.path.join(self._local.working_tree_dir, path)
        return os.path.exists(fpath) and os.path.isdir(fpath)

    def add_folder(self, path, mode=0o755):
        """Adds a folder with the content at the path
        """
        os.makedirs(os.path.join(self._local.working_tree_dir, path), exist_ok=True, mode=mode)
