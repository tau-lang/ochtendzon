import os
import toml
import logging
import contextlib
from typing import Callable, Iterable, Optional
from ochtendzon.error import OchtendzonError

CONFIG_NAME = "ochtendzon.toml"


class ConfigHandle:
    def __init__(self, toml: dict):
        self.toml = toml

    def get(self, keys: list[str], default: Optional[str] = None) -> Optional[str]:
        lookup = self.toml
        for key in keys:
            if not isinstance(lookup, dict) or key not in lookup:
                return default
            lookup = lookup[key]

        return lookup

    def get_or_else(self, keys: list[str], f: Callable[[], str]) -> str:
        result = self.get(keys)
        return result if result is not None else f()

    def insert(self, keys: list[str], value: str):
        if not keys:
            raise ValueError("Keys cannot be empty")

        lookup = self.toml
        for key in keys[:-1]:
            if key not in lookup:
                lookup[key] = dict()
            lookup = lookup[key]
        lookup[keys[-1]] = value

    def save_to(self, file):
        toml.dump(self.toml, file, encoder=toml.TomlEncoder(preserve=True))


class config:
    def __init__(self, directory):
        self.directory = directory
        self.handle = None
        self._chdir = contextlib.chdir(directory)

    def __enter__(self):
        self._chdir.__enter__()

        try:
            with open(CONFIG_NAME, "r") as f:
                self.handle = ConfigHandle(toml.load(f))

            return self.handle
        except FileNotFoundError:
            self._chdir.__exit__(None, None, None)
            raise OchtendzonError(
                f"Could not find {CONFIG_NAME} inside {self.directory}"
            )

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is None and self.handle is not None:
                with open(CONFIG_NAME, "w") as file:
                    self.handle.save_to(file)
        finally:
            self._chdir.__exit__(exc_type, exc_value, traceback)

        return False


def env(keys: list[str], default: Optional[None] = None) -> Optional[str]:
    for key in keys:
        value = os.getenv(key)
        if value is not None:
            return value
    return default
