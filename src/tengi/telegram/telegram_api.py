import asyncio
from telethon.sync import TelegramClient
from telethon.tl.types import Message
from typing import cast, List

from tengi.telegram import telegram_bot_utils


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
        asyncio.run(self._setup_session())

    def _get_api_client(self):
        return TelegramClient(session=self.api_session_name,
                              api_id=self.api_id,
                              api_hash=self.api_hash)

    async def _setup_session(self):
        """
        Creates a session object and caches it on disk, so next requests will reuse it and don't ask for phone number
        """
        api_client = self._get_api_client()
        async with api_client:
            pass

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

    def get_chat_messages_backward(self, chat_id, message_id, n_messages) -> List[Message]:
        return asyncio.run(self.get_chat_messages_backward_async(chat_id=chat_id,
                                                                 message_id=message_id,
                                                                 n_messages=n_messages))

    async def get_chat_messages_backward_async(self, chat_id, message_id, n_messages) -> List[Message]:
        if type(chat_id) == str:
            chat_id = telegram_bot_utils.to_int_chat_id_if_possible(chat_id)

        api_client = self._get_api_client()
        async with api_client:
            arr_messages = []
            gen = api_client.iter_messages(chat_id, max_id=message_id+1, limit=n_messages)
            async for msg in gen:
                arr_messages.append(msg)
        return arr_messages

    def get_chat_last_messages(self, chat_id, max_messages, max_excluded_id=0) -> List[Message]:
        return asyncio.run(self.get_chat_last_messages_async(chat_id=chat_id,
                                                             max_messages=max_messages,
                                                             max_excluded_id=max_excluded_id))

    async def get_chat_last_messages_async(self, chat_id, max_messages, max_excluded_id=0) -> List[Message]:
        api_client = self._get_api_client()
        async with api_client:
            arr_messages = []
            async for msg in api_client.iter_messages(chat_id, limit=max_messages, min_id=max_excluded_id):
                arr_messages.append(msg)
        return arr_messages
