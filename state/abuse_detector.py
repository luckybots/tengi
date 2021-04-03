from typing import Optional
import time


class AbuseDetector:
    def __init__(self, period_seconds: float, abuse_threshold: int):
        self.period_seconds = period_seconds
        self.abuse_threshold = abuse_threshold
        self.history = {}

    def check_abuse(self, sender) -> Optional[float]:
        s_hist = self._ensure_sender_history(sender)
        cur_time = time.time()
        s_hist = self.select_relevant_history(s_hist=s_hist, cur_time=cur_time)

        result = None
        if len(s_hist) >= self.abuse_threshold:
            oldest_elapsed = cur_time - min(s_hist)
            time_till_oldest_pop = self.period_seconds - oldest_elapsed
            result = time_till_oldest_pop
        else:
            s_hist.append(cur_time)

        self.history[sender] = s_hist
        return result

    def select_relevant_history(self, s_hist, cur_time):
        result = [x for x in s_hist if (cur_time - x <= self.period_seconds) and (cur_time >= x)]
        return result

    def _ensure_sender_history(self, sender):
        if sender not in self.history:
            self.history[sender] = []
        return self.history[sender]
