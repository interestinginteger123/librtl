import os
import uuid

import git
from azure.devops.v5_1.git.models import GitRepository, TeamProjectReference

from librtl.model import ManagedRepository

def setup_repo():
    remote_dir = os.path.join("/tmp", str(uuid.uuid4()))
    remote = git.Repo.init(remote_dir, bare=True)
    return GitRepository(
        ssh_url=f"file:///{remote_dir}",
        id=str(uuid.uuid4()),
        name=str(uuid.uuid4()),
        project=TeamProjectReference(name=str(uuid.uuid4())))

def test_ensures_default_files():
    repo = ManagedRepository(setup_repo(), [])
    assert repo.has_file("rtl/self.yaml")
    assert repo.has_file("rtl/Dockerfile.component")
    assert repo.has_file("README.md")
