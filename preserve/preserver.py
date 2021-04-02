from jsonstore import JsonStore
from pathlib import Path


class Preserver:
    def __init__(self, state_file_path: Path):
        state_file_path.parent.mkdir(exist_ok=True, parents=True)
        self.state = JsonStore(str(state_file_path))
