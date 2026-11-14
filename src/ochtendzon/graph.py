from dataclasses import dataclass
from typing import Callable, Awaitable, Iterable
from collections import defaultdict
from ochtendzon.error import OchtendzonError
from pathlib import PurePath, Path
import asyncio
import logging

"""
When developing the very first shell script for automating tau compilation, we
encountered the problem that only one command at a time was executed. File
compilations that didn't depended on each other were still blocking. To solve
this issue, we introduce the build graph together with build statements. This
is inspired by the ninja build tool (https://ninja-build.org/).

Formal definition of the problem for the build graph:
- Each statement hast a list of required input files and produces a list of
  output files.
- Each statement contains a rule that when run starts a process that takes
  the input files and produces the declared output files.
- Find an acyclic direct graph and order all statements based on its
  dependencies. Run statements from the bottom of the tree to the top
  asynchronous. A parent can only be started when all dependencies have
  successfully finished.
"""

logger = logging.getLogger(__name__)


@dataclass
class Statement:
    name: str
    inputs: list[str]
    outputs: list[str]
    run: Callable[[], Awaitable[None]]


def build_graph(statements: Iterable[Statement]):
    producers = {}

    for i, statement in enumerate(statements):
        for output in statement.outputs:
            if output in producers:
                raise ValueError(f"Multiple producers for file: {output}")
            producers[output] = i

    graph = defaultdict(set)
    indegree = [0] * len(statements)

    for i, statement in enumerate(statements):
        for input_file in statement.inputs:
            producer = producers.get(input_file)

            if producer is not None and producer != i:
                if i not in graph[producer]:
                    graph[producer].add(i)
                    indegree[i] += 1

            elif producer == i:
                raise ValueError(
                    f"Statement {statement.name} depends on its own output"
                )

    return graph, indegree


async def execute(statements: Iterable[Statement]):
    graph, indegree = build_graph(statements)

    count = len(statements)
    completed = set()
    running = {}

    async def run_statement(index):
        statement = statements[index]
        logger.debug(statement.name)
        await statement.run()

    async with asyncio.TaskGroup() as group:

        ready = [i for i in range(count) if indegree[i] == 0]

        while ready or running:

            # Start all currently available tasks.
            while ready:
                i = ready.pop()
                task = group.create_task(run_statement(i))
                running[task] = i

            if not running:
                break

            # Wait for at least one task to finish.
            done, _ = await asyncio.wait(
                running,
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in done:
                i = running.pop(task)

                # Propagate exceptions.
                task.result()

                completed.add(i)

                # Release dependent tasks.
                for dependent in graph[i]:
                    indegree[dependent] -= 1

                    if indegree[dependent] == 0:
                        ready.append(dependent)

    if len(completed) != count:
        remaining = [statements[i].name for i in range(count) if i not in completed]

        raise ValueError(f"Dependency cycle detected or unresolved tasks: {remaining}")


async def exec_subprocess(cmd: Iterable[str]):
    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            *map(str, cmd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()
    except FileNotFoundError:
        raise OchtendzonError(f"Could not find program: {cmd}")

    except asyncio.CancelledError:
        if proc is not None and proc.returncode is None:
            proc.kill()
            await proc.communicate()

        raise

    if proc.returncode != 0:
        raise OchtendzonError(
            f"Command failed ({proc.returncode}): {cmd}\n"
            f"stdout:\n{stdout.decode(errors='replace')}\n"
            f"stderr:\n{stderr.decode(errors='replace')}"
        )


def output(folder: PurePath, file: PurePath, ext: str) -> PurePath:
    return folder.joinpath(*file.parts[1:-1]) / f"{file.stem}.{ext}"


def compile_tau_qbe(
    tau_compiler: str, qbe_compiler: str, input: PurePath
) -> list[Statement]:
    temp = output(PurePath("target"), input, "ssa")
    Path(temp.parent).mkdir(parents=True, exist_ok=True)
    result = output(PurePath("target"), input, "s")
    return [
        Statement(
            f"Compile {input} with {tau_compiler} to Qbe",
            [input],
            [temp],
            lambda: exec_subprocess(
                [tau_compiler, input, "-o", temp, "--codegen", "qbe"]
            ),
        ),
        Statement(
            f"Compile {temp} with {qbe_compiler} to Assembly",
            [temp],
            [result],
            lambda: exec_subprocess([qbe_compiler, temp, "-o", result]),
        ),
    ]


def compile_tau_c(tau_compiler: str, c_compiler: str, input: PurePath):
    temp = output(PurePath("target"), input, "c")
    Path(temp.parent).mkdir(parents=True, exist_ok=True)
    result = output(PurePath("target"), input, "o")
    return [
        Statement(
            f"Compile {input} with {tau_compiler} to C",
            [input],
            [temp, output(input, "h")],
            lambda: exec_subprocess(
                [tau_compiler, input, "-o", temp, "--codegen", "c"]
            ),
        ),
        Statement(
            f"Compile {temp} with {c_compiler} to ObjectFile",
            [temp],
            [result],
            lambda: exec_subprocess([c_compiler, "-c", temp, "-o", result]),
        ),
    ]


def link(linker: str, inputs: Iterable[PurePath], output: PurePath):
    return Statement(
        f"Linking {', '.join(map(str, inputs))} -> {output}",
        inputs,
        [output],
        lambda: exec_subprocess([linker, "-o", output, *inputs]),
    )
