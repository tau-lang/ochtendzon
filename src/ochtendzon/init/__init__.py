import os
from ochtendzon.config import CONFIG_NAME, save_config


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
  if os.path.isfile(CONFIG_NAME):
    print("Config already exists, cancelling")
    return 1

  folder = os.path.basename(os.path.abspath('.'))
  print(f"Creating new project inside {folder}")

  name = args.name if args.name != None else folder
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
