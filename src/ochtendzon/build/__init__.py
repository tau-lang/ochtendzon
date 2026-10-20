from ochtendzon.build.files import build_folder, create_folder
from ochtendzon.build.process import link_binary
from ochtendzon.config import CONFIG_NAME, load_config
from os.path import isfile, isdir

def build(args):
  create_folder('target')

  if isfile(CONFIG_NAME):
    config = load_config()
  else:
    print('ochtendzon toml config not found')
    return 1

  if isdir('src'):
    object_files = []
    build_folder(args, 'src', object_files)

    binary = config['project']['name']
    link_binary(f'target/{binary}', object_files)
  else:
    print('Source folder not found')
    return 1
  
