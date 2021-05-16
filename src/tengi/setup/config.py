from jsonstore import JsonStore
import json
from pathlib import Path
import logging

logger = logging.getLogger(__file__)


class Config(JsonStore):
    def __init__(self, config_path: Path, example_path: Path):
        super().__init__(str(config_path))

        self.assert_keys_present(example_path)

    def assert_keys_present(self, example_path):
        with open(example_path, 'r') as f:
            example: dict = json.load(f)
        missing_keys = []
        for k in example.keys():
            if k not in self:
                missing_keys.append(k)

        assert len(missing_keys) == 0, f'Add values {missing_keys} to the config {self._path}. ' \
                                       f'Reference: {example_path}'

    @property
    def path_str(self) -> str:
        return self._path

    def try_get_warny(self, key: str, operation_name: str):
        if key in self:
            return self[key]
        else:
            logger.warning(f'Value "{key}" not present in the config. Add it into {self.path_str} to '
                           f'"{operation_name}"')
