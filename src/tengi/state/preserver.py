from jsonstore import JsonStore
from pathlib import Path


class Preserver:
    def __init__(self, state_file_path: Path, indent=2, auto_commit=True):
        state_file_path.parent.mkdir(exist_ok=True, parents=True)
        self.state = JsonStore(str(state_file_path),
                               indent=indent,
                               auto_commit=auto_commit)

    def _get_state_data(self) -> dict:
        # noinspection PyProtectedMember
        return self.state._data

    def _save_state(self):
        # noinspection PyProtectedMember
        self.state._save()
