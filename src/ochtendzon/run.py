import subprocess
import sys
import ochtendzon.error
from os.path import isdir
from pathlib import Path
from ochtendzon.config import config


def run(path):
    with config(path) as handle:
        if not isdir("target"):
            raise error.OchtendzonError("Target folder not found.")

        binary = handle.get(["project", "name"])
        try:
            result = subprocess.run([f"target/{binary}"])
            return result.returncode
        except FileNotFoundError:
            raise error.OchtendzonError("Binary not found.")
