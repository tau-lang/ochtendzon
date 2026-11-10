from ochtendzon.config import config, env
from ochtendzon.error import OchtendzonError
from ochtendzon.graph import compile_tau_c, compile_tau_qbe, output, link, execute
from pathlib import Path
import os
import asyncio


def find_files(path: Path, callback):
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file() and entry.name.endswith(".tau"):
                callback(Path(entry.path))
            elif entry.is_dir():
                find_files(entry.path)


def build_with_c(input: Path):
    output = Path(input.parent) / (input.stem + ".c")


def build(path: Path):
    with config(path) as handle:
        # create target folder
        target = path / "target"
        if not target.exists():
            target.mkdir()

        # check src folder
        source = path / "src"
        if source.exists() and source.is_dir():
            statements = []
            object_files = []

            def build_c(tau_compiler, c_compiler, path):
                statements.extend(compile_tau_c(tau_compiler, c_compiler, path))
                object_files.append(output(path, "o"))

            def find_c_compiler():
                tau_compiler = env(["OCHTENDZON_TAU_COMPILER"], "tau")
                c_compiler = env(["OCHTENDZON_C_COMPILER"], "gcc")
                return lambda path: build_c(tau_compiler, c_compiler, path)

            def build_qbe(tau_compiler, qbe_compiler, path):
                statements.extend(compile_tau_qbe("tau", "qbe", path))
                object_files.append(output(path, "s"))

            def find_qbe_compiler():
                tau_compiler = env(["OCHTENDZON_TAU_COMPILER"], "tau")
                qbe_compiler = env(["OCHTENDZON_QBE_COMPILER"], "qbe")
                return lambda path: build_qbe(tau_compiler, qbe_compiler, path)

            find_files(source, find_c_compiler())

            binary = handle.get(["project", "name"])
            linker = env(["OCHTENDZON_LINKER"], "cc")
            statements.append(link(linker, object_files, f"target/{binary}"))
            return statements
        else:
            raise OchtendzonError("Source folder not found")
