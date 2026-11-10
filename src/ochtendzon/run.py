import subprocess
import sys
import ochtendzon.error
from os.path import isfile, isdir
from ochtendzon.config import CONFIG_NAME, load_config


def run(args):
    config = load_config()

    if not isdir("target"):
        raise error.OchtendzonError("Target folder not found.")

    binary = config["project"]["name"]
    try:
        result = subprocess.run([f"target/{binary}"])
        return result.returncode
    except FileNotFoundError:
        raise error.OchtendzonError("Binary not found.")
