import os
import logging
from ochtendzon.config import CONFIG_NAME, save_config


logger = logging.getLogger(__name__)

DEFAULT_MAIN = """
extern fn puts(text: str)

fn main() {
    puts("Hello, World!")
}
"""

DEFAULT_GITIGNORE = """
result
target/
"""

def init(args) -> int:
  if os.path.isfile(CONFIG_NAME) and args.force is None :
    logger.error("Config already exists, cancelling")
    return 1

  folder = os.path.basename(os.path.abspath('.'))
  logger.info(f"Creating new project inside {folder}")

  name = args.name if args.name is not None else folder
  generated = {
    'project': {
      'name': name,
      'author': "",
      'version': "0.1.0"
    },
    'dependencies': {},
  }

  save_config(generated)

  os.makedirs('src', exist_ok=True)
  with open('src/app.tau', 'w') as f:
    f.write(DEFAULT_MAIN)
  with open('.gitignore', 'w') as f:
    f.write(DEFAULT_GITIGNORE)
