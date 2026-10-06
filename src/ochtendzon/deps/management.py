import os
import logging
import subprocess
from contextlib import chdir
from ochtendzon.config import *
from ochtendzon.deps.step import find_step
from toml.decoder import InlineTableDict

logger = logging.getLogger(__name__)

class ForceInlineTable(dict, InlineTableDict):
    def __init__(self, obj):
        super().__init__(obj)


def build_dependency(resolve):
    cache = os.path.expanduser(f"~/.cache/ochtendzon/deps/{resolve}")
    with chdir(cache):
        update_dependencies()
        import ochtendzon.build
        build.build({target: 'cpp'})


def pull_dependency(handler, name, version, src):
    steps = handler.split('+')
    for step in steps:
        status = find_step(step, name, version, src)
        if status is not None: return status

def verify_dependency(resolve, name, version):
    cache = os.path.expanduser(f"~/.cache/ochtendzon/deps/{resolve}")
    with chdir(cache):
        config = load_config()
        if config is None:
            logger.error(f"Dependency should include a valid config")
            return 1

        found_name = config_or_default(config, ['project', 'name'], None)
        if found_name is None or found_name != name:
            logger.error(f"Expected name {name}, found name {found_name}")
            return 1

        found_version = config_or_default(config, ['project', 'version'], None)
        if found_version is None or found_version != version:
            logger.info(f"Expected version {version}, found name {found_version}")
            return 1

        binary = os.path.join(cache, 'target', name)
        if not os.path.isfile(binary):
            logger.info(f"Building dependency")
            return build_dependency(resolve)


def update_dependencies():
    config = load_config()
    if config is None: return 1
    dependencies = config_or_default(config, ['dependencies'], dict())
    for dependency in dependencies.items():
        (name, value) = dependency
        version = value['version']
        resolve = f'{name}-{version}'
        src = value['src']
        (handler, url) = src.split(':', 1)
        cache = os.path.expanduser(f"~/.cache/ochtendzon/deps/{resolve}")
        if not os.path.exists(cache) or len(os.listdir(cache)) == 0:
            logger.info(f"Downloading {resolve} to {cache}")
            pull_dependency(handler, name, version, url)
        verify_dependency(resolve, name, version)


def add_dependency(name, version, src):
    config = load_config()
    logger.info(f"Adding dependency {name}")
    dependencies = config_or_default(config, ["dependencies"], dict())
    
    if name in dependencies:
        logger.warn(f"Dependecy {name} is already installed")
    dependencies[name] = ForceInlineTable({'version': version, 'src': src})
    config['dependencies'] = dependencies
    save_config(config)
    update_dependencies()


def remove_dependency(name):
    config = load_config()
    logger.info(f"Removing dependency {name}")
    dependencies = config_or_default(config, ["dependencies"], dict())
    value = dependencies.pop(name, None)
    if value is None:
        logger.warn(f"Dependency {name} does not exist")
    config['dependencies'] = dependencies
    save_config(config)
    update_dependencies()
