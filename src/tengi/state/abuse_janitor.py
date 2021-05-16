import time
import logging

from tengi.state.abuse_detector import AbuseDetector

logger = logging.getLogger(__file__)


class AbuseJanitor:
    """
    Periodically cleans abuse detector state from outdated user records (prevent RAM overfill)
    """
    def __init__(self, abuse_detector: AbuseDetector, period_seconds: float):

        self.abuse_detector = abuse_detector
        self.period_seconds = period_seconds
        self.last_run = time.time()

    def update(self):
        cur_time = time.time()
        if (cur_time - self.last_run) >= self.period_seconds:
            logger.info('janitor run')

            for sender, s_hist in list(self.abuse_detector.history.items()):
                s_hist = self.abuse_detector.select_relevant_history(s_hist=s_hist, cur_time=cur_time)
                if not s_hist:
                    del self.abuse_detector.history[sender]

            self.last_run = cur_time
