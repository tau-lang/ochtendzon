import os
import logging
from ochtendzon.config import *
from toml.decoder import InlineTableDict

logger = logging.getLogger(__name__)

class ForceInlineTable(dict, InlineTableDict):
    def __init__(self, obj):
        super().__init__(obj)

def update_dependencies():
    config = load_config()
    dependencies = config['dependencies']
    for dependency in dependencies.items():
        (name, value) = dependency
        resolve = f'{name}-{value['version']}'
        src = value['src']


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
