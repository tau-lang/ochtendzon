import logging
import asyncio
import os
import argparse
from pathlib import Path
from ochtendzon.error import OchtendzonError
from ochtendzon.build import build
from ochtendzon.init import init
from ochtendzon.deps import add, update, remove
from ochtendzon.graph import execute

logger = logging.getLogger(__name__)


async def command(args):
    try:
        match args.command:
            case "build":
                await execute(build(Path(".")))
            case "init":
                init(force=args.force)
            case "run":
                await execute(build(Path(".")))
                run()
            case "add":
                await execute(
                    add(args.name, args.version, git=args.git, path=args.path)
                )
            case "update":
                await execute(update())
            case "remove":
                remove(args.name)
    except* OchtendzonError as errors:
        for error in errors.exceptions:
            logger.error("%s", error)
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="ochtendzon",
        description="Simple compiler toolchain for the Tau language. ",
        fromfile_prefix_chars="@",
        suggest_on_error=True,
    )

    subparsers = parser.add_subparsers(title="commands", required=True, dest="command")

    parser_build = subparsers.add_parser("build", help="Compile the current package")
    parser_build.add_argument("--target", choices=("cpp", "cranelift"), default="cpp")

    parser_init = subparsers.add_parser("init", help="Create a new ochtendzon package")
    parser_init.add_argument("--name", type=str)
    parser_init.add_argument("-f", "--force", action="store_true")

    parser_run = subparsers.add_parser("run", help="Run a binary of the local package")

    parser_add = subparsers.add_parser(
        "add", help="Add the package to the dependencies"
    )
    parser_add.add_argument("name", type=str)
    parser_add.add_argument("version", type=str)
    parser_add.add_argument("--git", type=str)
    parser_add.add_argument("--path", type=str)

    parser_update = subparsers.add_parser("update", help="Updates all dependencies")

    parser_remove = subparsers.add_parser(
        "remove", help="Remove the package from the dependencies"
    )
    parser_remove.add_argument("name", type=str)

    args = parser.parse_args()

    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
    asyncio.run(command(args))
