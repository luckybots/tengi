import logging
from typing import Iterable, Callable, Any, List
import inspect
from telebot.apihelper import ApiTelegramException

from tengi import TelegramCursor
from tengi.telegram.inbox_handler import *
from tengi.telegram import  telegram_error


logger = logging.getLogger(__file__)


def is_overwritten(method):
    #  __qualname__ examples: 'TelegramInboxHandler.edited_message', 'CommandHub.message'
    return TelegramInboxHandler.__name__ not in method.__qualname__


class TelegramInboxHub:
    def __init__(self, telegram_cursor: TelegramCursor, chain_handlers: Iterable[TelegramInboxHandler]):
        self.telegram_cursor = telegram_cursor

        # getmembers returns array of tuples like
        #   ('callback_query', <function __main__.TelegramInboxHandler.callback_query(self, message:
        #   telebot.types.CallbackQuery) -> Union[bool, NoneType]>)
        update_types = [x[0] for x in inspect.getmembers(TelegramInboxHandler, predicate=inspect.isfunction)]

        # Group handlers in dict of lists by update types
        self.handlers = {}
        for h in chain_handlers:
            for ut in update_types:
                method = getattr(h, ut)
                if is_overwritten(method):
                    if ut not in self.handlers:
                        self.handlers[ut] = []
                    self.handlers[ut].append(h)

    def update(self):
        allowed_updates = list(self.handlers.keys())
        try:
            updates = self.telegram_cursor.get_new_updates(allowed_updates=allowed_updates)
        except ApiTelegramException as ex:
            if ex.error_code == telegram_error.BAD_GATEWAY:
                #  Telegram is temporary unavailable
                logger.info('Telegram is temporary unavailable, further update is skipped')
                return
            else:
                raise ex

        for u in updates:
            try:
                arr_update_type = [ut for ut in allowed_updates if (getattr(u, ut) is not None)]
                assert len(arr_update_type) == 1, f'Update object contains multiple update types: {arr_update_type}'
                update_type = arr_update_type[0]

                def handler_func(handler: TelegramInboxHandler, item_: Any) -> bool:
                    func = getattr(handler, update_type)
                    handled_ = func(item_)
                    return handled_

                # Names of methods in TelegramInboxHandler match names of fields in types.Update
                item = getattr(u, update_type)
                handled = self._chain_handlers(handlers=self.handlers[update_type],
                                               item=item,
                                               handler_func=handler_func)
                if not handled:
                    logger.info(f'Update not handled: {update_type}, {u.update_id}')
            except Exception as ex:
                logger.exception(ex)

    @staticmethod
    def _chain_handlers(handlers: List[TelegramInboxHandler],
                        item: Any,
                        handler_func: Callable[[TelegramInboxHandler, Any], bool]):
        handled = False
        for h in handlers:
            handled = handler_func(h, item)
            if handled:
                break
        return handled
