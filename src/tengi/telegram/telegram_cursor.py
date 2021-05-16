from telebot import types
from typing import List
from datetime import datetime
import logging

from tengi.telegram.telegram_bot import TelegramBot

logger = logging.getLogger(__file__)


class TelegramCursor:
    def __init__(self, bot: TelegramBot, look_back_days: float, long_polling_timeout: float = 20):
        self.bot = bot
        self.look_back_days = look_back_days
        self.long_polling_timeout = long_polling_timeout
        self.last_bot_update_id = None

    def look_back(self, allowed_updates):
        updates = self.bot.get_updates(long_polling_timeout=0,
                                       limit=100,
                                       allowed_updates=allowed_updates)

        # Sort updates from newest to oldest to use latest message in the chat only
        updates = sorted(updates,
                         key=lambda upd: upd.update_id,
                         reverse=True)
        now = datetime.utcnow()
        look_back_seconds = self.look_back_days * 24 * 60 * 60
        look_back_updates = []
        cached_chat_ids = set()
        for u in updates:
            if u.message is not None:  # Ignore messages that are outside the look back window
                elapsed_seconds = (now - datetime.utcfromtimestamp(u.message.date)).total_seconds()
                if elapsed_seconds > look_back_seconds:
                    continue
                # Cache only the last message from the chat
                chat_id = u.message.chat.id
                if chat_id in cached_chat_ids:
                    continue
                cached_chat_ids.add(chat_id)
            look_back_updates.append(u)

        # Sort updates from oldest to newest to handle in natural order
        look_back_updates = sorted(look_back_updates,
                                   key=lambda upd: upd.update_id)
        return look_back_updates

    def get_new_updates(self, allowed_updates) -> List[types.Update]:
        look_back_updates = []
        if self.last_bot_update_id is None:
            look_back_updates = self.look_back(allowed_updates=allowed_updates)
            if look_back_updates:
                last_update = max(look_back_updates, key=lambda upd: upd.update_id)
                self.last_bot_update_id = last_update.update_id
            else:
                self.last_bot_update_id = -1

        long_polling_timeout = self.long_polling_timeout if (not look_back_updates) else 0
        updates: List[types.Update] = self.bot.get_updates(offset=self.last_bot_update_id + 1,
                                                           long_polling_timeout=long_polling_timeout,
                                                           allowed_updates=allowed_updates)
        if look_back_updates:
            updates = look_back_updates + updates

        if updates:
            last_update = max(updates, key=lambda upd: upd.update_id)
            self.last_bot_update_id = last_update.update_id

        return updates
