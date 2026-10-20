import os
import toml


CONFIG_NAME = 'ochtendzon.toml'


def load_config():
  with open(CONFIG_NAME, 'r') as f:
      return toml.load(f)


def save_config(config):
  with open(CONFIG_NAME, 'w') as f:
      toml.dump(config, f)
