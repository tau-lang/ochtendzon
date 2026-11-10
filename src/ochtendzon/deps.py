import os
import logging
import subprocess
from contextlib import chdir
from ochtendzon.config import *
from ochtendzon.error import OchtendzonError
from ochtendzon.build import build
from ochtendzon.graph import Statement
from toml.decoder import InlineTableDict
from pathlib import Path

logger = logging.getLogger(__name__)


class ForceInlineTable(dict, InlineTableDict):
    def __init__(self, obj):
        super().__init__(obj)


def build_dependency(path: Path) -> list[Statement]:
    with chdir(path):
        update()
        return build(path)


def pull_git(path: Path, git: str, branch: str = None):
    args = [
        "git",
        "clone",
        "--recursive",
        "--quiet",
        "--progress",
        "--checkout",
        "--single-branch",
        "--depth",
        "1",
        git,
        path,
    ]
    if branch is not None:
        args.extend(["--branch", branch])
    process = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise OchtendzonError(f"Could not pull dependency:\n{stderr}")


def cache_path(resolve):
    return os.path.expanduser(f"~/.cache/ochtendzon/deps/{resolve}")


def verify_dependency(path: Path, name: str, version: str) -> list[Statement]:
    with config(path) as handler:
        found_name = handler.get(["project", "name"])
        if found_name is None or found_name != name:
            raise OchtendzonError(f"Expected name {name}, found name {found_name}")

        found_version = handler.get(["project", "version"])
        if found_version is None or found_version != version:
            raise OchtendzonError(
                f"Expected version {version}, found name {found_version}"
            )

        binary = path / "target" / name
        if not os.path.isfile(binary):
            logger.info(f"Building dependency {name}")
            return build_dependency(path)

    # Nothing to build
    return []


def update() -> list[Statement]:
    with config(Path(".")) as handler:
        statements = []
        dependencies = handler.get_or_else(["dependencies"], dict)
        for dependency in dependencies.items():
            name, value = dependency
            version = value["version"]
            resolve = f"{name}-{version}"
            if "git" in value:
                git = value["git"]
                path = Path(cache_path(resolve))
                if not path.exists():
                    pull_git(path, git)
                statements.extend(verify_dependency(path, name, version))
            if "path" in value:
                path = Path(value["path"])
                statements.extend(verify_dependency(path, name, version))
        return statements


def add(name: str, version: str, git=None, path=None) -> list[Statement]:
    with config(Path(".")) as handler:
        logger.info(f"Adding dependency {name}")
        dependencies = handler.get_or_else(["dependencies"], dict)

        if name in dependencies:
            logger.warn(f"Dependecy {name} is already installed")
        entries = {"version": version}
        if git is not None:
            entries["git"] = git
        if path is not None:
            entries["path"] = path
        dependencies[name] = ForceInlineTable(entries)
        handler.insert(["dependencies"], dependencies)

        return update()


def remove(name: str) -> None:
    with config(Path(".")) as handler:
        logger.info(f"Removing dependency {name}")
        dependencies = handler.get_or_else(["dependencies"], dict)
        value = dependencies.pop(name, None)

        handler.insert(["dependencies"], dependencies)

        update_dependencies()
