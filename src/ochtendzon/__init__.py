import logging
import asyncio
import os
import shutil
import argparse
from pathlib import PurePath, Path
from ochtendzon.build import build
from ochtendzon.deps import add, update, remove
from ochtendzon.error import OchtendzonError
from ochtendzon.graph import execute
from ochtendzon.init import init
from ochtendzon.run import run

logger = logging.getLogger(__name__)


async def command(args):
    try:
        match args.command:
            case "build" | "b":
                await execute(build(Path(), args.codegen))
            case "clean":
                target = Path("target")
                if target.exists():
                    shutil.rmtree(target)
                else:
                    logger.warn("target folder does not exist")
            case "init":
                init(force=args.force)
            case "run":
                await execute(build(Path(), args.codegen))
                run(PurePath())
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
    )

    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("-v", "--verbose", action="store_true")

    subparsers = parser.add_subparsers(title="commands", required=True, dest="command")

    parser_build = subparsers.add_parser(
        "build", aliases=["b"], help="Compile the current package", parents=[parent]
    )
    parser_build.add_argument(
        "-C", "--codegen", choices=("c", "cranelift", "qbe"), default="qbe"
    )

    parser_clean = subparsers.add_parser(
        "clean", help="Remove the target directory", parents=[parent]
    )

    parser_init = subparsers.add_parser(
        "init", help="Create a new ochtendzon package", parents=[parent]
    )
    parser_init.add_argument("--name", type=str)
    parser_init.add_argument("-f", "--force", action="store_true")

    parser_run = subparsers.add_parser(
        "run", help="Run a binary of the local package", parents=[parent]
    )
    parser_run.add_argument(
        "-C", "--codegen", choices=("c", "cranelift", "qbe"), default="qbe"
    )

    parser_add = subparsers.add_parser(
        "add", help="Add the package to the dependencies", parents=[parent]
    )
    parser_add.add_argument("name", type=str)
    parser_add.add_argument("version", type=str)
    parser_add.add_argument("--git", type=str)
    parser_add.add_argument("--path", type=str)

    parser_update = subparsers.add_parser(
        "update", help="Updates all dependencies", parents=[parent]
    )

    parser_remove = subparsers.add_parser(
        "remove", help="Remove the package from the dependencies", parents=[parent]
    )
    parser_remove.add_argument("name", type=str)

    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format="%(levelname)s: %(message)s", level=level)
    asyncio.run(command(args))
