import os
import toml


CONFIG_NAME = 'ochtendzon.toml'


def load_config():
  with open(CONFIG_NAME, 'r') as f:
      return toml.load(f)


def save_config(config):
  with open(CONFIG_NAME, 'w') as f:
      toml.dump(config, f, encoder=toml.TomlEncoder(preserve=True))


def config_or_default(self, keys: list[str], default):
  for key in keys:
    if key in self:
      self = self[key]
    else: return default
  return self


def env_or_default(keys: list[str], default):
  for key in keys:
    value = os.getenv(key)
    if value is not None: return value
  return default