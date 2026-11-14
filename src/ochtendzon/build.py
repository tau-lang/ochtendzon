from ochtendzon.config import config, env
from ochtendzon.error import OchtendzonError
from ochtendzon.graph import (
    Statement,
    compile_tau_c,
    compile_tau_qbe,
    output,
    link,
    execute,
)
from pathlib import PurePath, Path
from typing import Callable
import os
import asyncio


def find_files(path: PurePath, callback: Callable[[PurePath], None]):
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file() and entry.name.endswith(".tau"):
                callback(PurePath(entry.path))
            elif entry.is_dir():
                find_files(entry.path, callback)


def find_c_compiler(statements: list[Statement], object_files: list[PurePath]):
    tau_compiler = env(["OCHTENDZON_TAU_COMPILER"], "tau")
    c_compiler = env(["OCHTENDZON_C_COMPILER"], "gcc")

    def build_c(tau_compiler: str, c_compiler: str, path: PurePath):
        statements.extend(compile_tau_c(tau_compiler, c_compiler, path))
        object_files.append(output(PurePath("target"), path, "o"))

    return lambda path: build_c(tau_compiler, c_compiler, path)


def find_qbe_compiler(statements: list[Statement], object_files: list[PurePath]):
    tau_compiler = env(["OCHTENDZON_TAU_COMPILER"], "tau")
    qbe_compiler = env(["OCHTENDZON_QBE_COMPILER"], "qbe")

    def build_qbe(tau_compiler: str, qbe_compiler: str, path: PurePath):
        statements.extend(compile_tau_qbe("tau", "qbe", path))
        object_files.append(output(PurePath("target"), path, "s"))

    return lambda path: build_qbe(tau_compiler, qbe_compiler, path)


def build(path: Path, codegen: str):
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

            builder = None
            match codegen:
                case "c":
                    builder = find_c_compiler(statements, object_files)
                case "qbe":
                    builder = find_qbe_compiler(statements, object_files)
                case "cranelift":
                    raise OchtendzonError("codegen backend is not implemented")

            find_files(source, builder)

            binary = handle.get(["project", "name"])
            linker = env(["OCHTENDZON_LINKER"], "cc")
            statements.append(link(linker, object_files, f"target/{binary}"))
            return statements
        else:
            raise OchtendzonError("Source folder not found")
