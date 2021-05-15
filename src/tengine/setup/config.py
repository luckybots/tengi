from jsonstore import JsonStore
import json
from pathlib import Path


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

        assert len(missing_keys) == 0, f'Keys are missing from config: {self._path}: {missing_keys}'

