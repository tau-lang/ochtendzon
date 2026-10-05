import os
from ochtendzon.config import *
from toml.decoder import InlineTableDict


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
        print(resolve)


def add_dependency(name, version, src):
    config = load_config()
    dependencies = config_or_default(config, ["dependencies"], dict())
    dependencies[name] = ForceInlineTable({'version': version, 'src': src})
    config['dependencies'] = dependencies
    save_config(config)
    update_dependencies()


def remove_dependency(name):
    config = load_config()
    config['dependencies'].remove(name)
    save_config(config)
    update_dependencies()
