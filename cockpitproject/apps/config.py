from typing import Union
import functools
import os
import pathlib

import yaml

DEFAULT_ENVIRONMENT = "local"
ROOT_DIR = os.path.dirname(os.path.abspath(__file__)).split("apps")
DEFAULT_CONFIG_FILE_PATH = ROOT_DIR[0] + "/config/{}.yml"
ConfigDict = Union[str, int, dict]


class Config:
    def __init__(self):
        environment = os.getenv("environment", DEFAULT_ENVIRONMENT)
        self.path = pathlib.Path(DEFAULT_CONFIG_FILE_PATH.format(environment))

    @functools.cached_property
    def config(self) -> dict:
        return self._read_config()

    def get(self, key: str) -> ConfigDict:
        return os.getenv(key, self.config.get(key))

    def get_nested(self, keys: str) -> ConfigDict:
        value = None

        for key in keys.split("."):
            value = value[key] if value else self.config[key]

        return value

    def _read_config(self) -> dict:
        with open(self.path) as stream:
            return yaml.safe_load(stream)


CONFIG = Config()
