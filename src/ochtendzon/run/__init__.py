import subprocess
import sys
from os.path import isfile, isdir
from ochtendzon.config import CONFIG_NAME, load_config

def run(args):
  if isfile(CONFIG_NAME):
    config = load_config()
  else:
    print('ochtendzon toml config not found')
    return 1

  if isdir('target'):
    binary = config['project']['name']
    result = subprocess.run([f'target/{binary}'])
    return result.returncode
  else:
    print('Target folder not found')
    return 1
  
