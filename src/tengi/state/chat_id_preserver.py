from typing import Iterable
from telebot.types import Message
from tengi import event
from tengi.telegram.telegram_bot import EV_TEL_RECEIVED_MESSAGES
from tengi.state.preserver import *


class ChatIdPreserver(Preserver):
    def __init__(self, state_file_path: Path):
        super().__init__(state_file_path)

        event.emitter.on(EV_TEL_RECEIVED_MESSAGES, self._on_receive_messages)

    def _ensure_private_chats_list(self) -> list:
        if 'private_chats' not in self.state:
            self.state['private_chats'] = []

        return self.state['private_chats']

    def _update_private_chats_list(self, value: list):
        self.state['private_chats'] = value

    def _add_private_chat(self, chat_id):
        private_chats = self._ensure_private_chats_list()
        if chat_id not in private_chats:
            private_chats.append(chat_id)
            self._update_private_chats_list(private_chats)

    def _on_receive_messages(self, messages: Iterable[Message]):
        for m in messages:
            if m.chat.type == 'private':
                self._add_private_chat(m.chat.id)
