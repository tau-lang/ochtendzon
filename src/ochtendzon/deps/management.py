import os
import logging
import subprocess
from ochtendzon.config import *
from toml.decoder import InlineTableDict

logger = logging.getLogger(__name__)

class ForceInlineTable(dict, InlineTableDict):
    def __init__(self, obj):
        super().__init__(obj)

def pull_source(args, resolve):
  try:
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
      logger.error(f"When pulling dependency {resolve}: {stderr}")
  except FileNotFoundError:
    logger.error(f"Could not find file handler {args}")


def update_dependencies():
    config = load_config()
    dependencies = config['dependencies']
    for dependency in dependencies.items():
        (name, value) = dependency
        version = value['version']
        resolve = f'{name}-{version}'
        src = value['src']
        (handler, url) = src.split(':', 1)
        cache = os.path.expanduser(f"~/.cache/ochtendzon/deps/{resolve}")
        if not os.path.exists(cache) or len(os.listdir(cache)) == 0:
            logger.info(f"Downloading {resolve} to {cache}")
            match handler:
                case 'git':
                    pull_source([
                        'git', 'clone',
                        '--recursive',
                        '--quiet',
                        '--progress',
                        '--checkout',
                        '--branch', version,
                        '--single-branch',
                        '--depth', "1",
                        url, cache
                    ], resolve)
                case 'curl':
                    tmp = os.path.expanduser("~/.cache/ochtendzon/tmp/")
                    download = os.path.join(tmp, resolve)
                    os.makedirs(tmp, exist_ok = True) 
                    pull_source([
                        'curl', '-s', '-L', url, '-o', download
                    ], resolve)
                    os.makedirs(cache, exist_ok = True) 
                    pull_source([
                        'tar', 'xvz', '-f', download, '-C', cache
                    ], resolve)


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
