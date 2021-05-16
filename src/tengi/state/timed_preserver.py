import time
import copy

from tengi.state.preserver import *


class TimedPreserver(Preserver):
    def __init__(self, state_file_path: Path, save_period: float, indent=2):
        super().__init__(state_file_path=state_file_path,
                         indent=indent,
                         auto_commit=False)
        self.save_period = save_period
        self.saved_time = time.time()
        self.saved_dict = copy.deepcopy(self._get_state_data())

    def update(self):
        cur_time = time.time()
        if (self.saved_time is None) or \
                (cur_time - self.saved_time >= self.save_period):

            cur_dict = self._get_state_data()
            if self.saved_dict != cur_dict:
                self._save_state()
                self.saved_dict = copy.deepcopy(cur_dict)

            self.saved_time = cur_time
