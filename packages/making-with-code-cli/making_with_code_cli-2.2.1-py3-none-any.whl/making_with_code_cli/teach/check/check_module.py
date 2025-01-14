# test_module.py
# --------------
# Defines a test case for a MWC module.

from pathlib import Path
from subprocess import run
import requests
import toml
from git import Repo, InvalidGitRepositoryError, GitCommandError

DEFAULT_BRANCH_NAME = "main"
PYTHON_VERSION = ">=3.10"

class TestCouldNotContinue(Exception):
    pass

class TestMWCModule:

    def __init__(self, module_metadata, repo_path):
        self.module_metadata = module_metadata
        self.repo_path = repo_path

    def run(self):
        self.errors = []
        try:
            self.fetch_repo()
            self.test_curriculum_page_exists()
            self.test_has_commit_template()
            self.test_poetry()
            self.test_module_metadata()
        except TestCouldNotContinue as err:
            self.errors.append(str(err))
        return self.errors

    def fetch_repo(self):
        """Ensures the repo is present and up to date.
        """
        if self.repo_path.exists():
            try: 
                repo = Repo(self.repo_path)
                repo.remotes.origin.pull()
            except InvalidGitRepositoryError:
                raise TestCouldNotContinue(f"{self.module_path} exists but is not a repo")
        else:
            try:
                repo = Repo.clone_from(self.module_metadata['repo_url'], self.repo_path)
            except GitCommandError:
                raise TestCouldNotContinue("Could not clone repo")
        if not repo.active_branch.name == DEFAULT_BRANCH_NAME:
            self.errors.append(f"Default branch is not '{DEFAULT_BRANCH_NAME}'")

    def test_curriculum_page_exists(self):
        page_url = self.module_metadata['url']
        response = requests.get(page_url)
        if not response.ok:
            self.errors.append(f"Curriculum page missing: {page_url}")

    def test_has_commit_template(self):
        ct = self.repo_path / ".commit_template"
        if not ct.exists:
            self.errors.append(".commit_template is missing")

    def test_poetry(self):
        result = run("poetry check", cwd=self.repo_path, shell=True, capture_output=True, 
                text=True)
        if result.returncode:
            for err in result.stderr.split('\n'):
                if err.strip():
                    self.errors.append(err.strip())

    def test_module_metadata(self):
        md_file = self.repo_path/"pyproject.toml"
        if not md_file.exists():
            self.errors.append(f"pyproject.toml missing")
            return 
        md = toml.load(md_file)
        if not "project" in md:
            self.errors.append("'project' section missing from pyproject.toml")
            return
        if "tool" in md:
            self.errors.append("Deprecated 'tool' section found in pyproject.toml")
        pyversion = md['project'].get('requires-python')
        if not pyversion == PYTHON_VERSION:
            self.errors.append(f"python version is {pyversion}, expected {PYTHON_VERSION}")





