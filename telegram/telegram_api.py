import asyncio
from telethon.sync import TelegramClient
from telethon.tl.types import Message
from typing import cast

from tengine.telegram import telegram_bot_utils


class TelegramApi:
    def __init__(self, api_session_name, api_id, api_hash):
        """
        :param api_session_name: arbitrary string to distinguish between your sessions
        :param api_id: obtain at https://my.telegram.org/auth
        :param api_hash: obtain at https://my.telegram.org/auth
        """
        self.api_session_name = api_session_name
        self.api_id = api_id
        self.api_hash = api_hash

    def _get_api_client(self):
        return TelegramClient(session=self.api_session_name,
                              api_id=self.api_id,
                              api_hash=self.api_hash)

    def get_chat_message(self, chat_id, message_id) -> Message:
        return asyncio.run(self.get_chat_message_async(chat_id=chat_id,
                                                       message_id=message_id))

    async def get_chat_message_async(self, chat_id, message_id) -> Message:
        if type(chat_id) == str:
            chat_id = telegram_bot_utils.to_int_chat_id_if_possible(chat_id)

        api_client = self._get_api_client()
        async with api_client:
            msg = await api_client.get_messages(chat_id, ids=message_id)

        if msg is None:
            raise Exception(f'In chat {chat_id} there is no message {message_id}')

        # api_client.get_messages returns Message object in case of 1 message requested though TotalList declared
        msg = cast(Message, msg)
        return msg
