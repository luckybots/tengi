import signal
import sys
import time
import logging
from typing import Iterable, Callable

logger = logging.getLogger(__file__)


class App:
    def __init__(self,
                 update_funcs: Iterable[Callable],
                 update_seconds: float,
                 restart_seconds: float):
        self.update_funcs = update_funcs
        self.update_seconds = update_seconds
        self.restart_seconds = restart_seconds

    def run(self):
        # KeyboardInterrupt catching doesn't work as telebot catches it internally and sends as a different error
        def sigint_handler(_sig, _frame):
            logger.info('Ctrl+C pressed')
            logger.info('Bot finished')
            sys.exit(0)

        signal.signal(signal.SIGINT, sigint_handler)

        logger.info('App started')
        should_interrupt = False
        while True:
            try:
                while True:
                    upd_begin = time.time()

                    for u_func in self.update_funcs:
                        u_func()

                    upd_end = time.time()
                    upd_remaining = self.update_seconds - (upd_end - upd_begin)

                    should_interrupt = self.should_interrupt()
                    if should_interrupt:
                        logger.info(f'Got should_interrupt')
                        break

                    if upd_remaining > 0:
                        time.sleep(upd_remaining)
            except Exception as e:
                logger.exception(e)

            if should_interrupt:
                break

            logger.info(f'Restarting in {self.restart_seconds:,} seconds')
            time.sleep(self.restart_seconds)

    @classmethod
    def should_interrupt(cls):
        """
        An ability to interrupt infinite loop, used for testing
        :return:
        """
        return False
