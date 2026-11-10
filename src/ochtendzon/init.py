import os
import logging
from ochtendzon.error import OchtendzonError
from ochtendzon.config import config, CONFIG_NAME, ConfigHandle

DEFAULT_MAIN = """
extern fn puts(text: str) -> i32;

fn main() {
    puts("Hello, World!");
}
"""

DEFAULT_GITIGNORE = """
result
target/
"""


def init(args) -> int:
    if os.path.isfile(CONFIG_NAME) and not args.force:
        raise OchtendzonError("Config already exists, cancelling")

    folder = os.path.basename(os.path.abspath("."))
    name = args.name if args.name is not None else folder
    generated = ConfigHandle(
        {
            "project": {"name": name, "author": "", "version": "0.1.0"},
            "dependencies": {},
        }
    )

    with open(CONFIG_NAME, "w") as file:
        generated.save_to(file)

    os.makedirs("src", exist_ok=True)
    with open("src/main.tau", "w") as f:
        f.write(DEFAULT_MAIN)
    with open(".gitignore", "w") as f:
        f.write(DEFAULT_GITIGNORE)
