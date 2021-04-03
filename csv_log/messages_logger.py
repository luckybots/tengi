from telebot.types import Message
from typing import Iterable

from tengine.csv_log.csv_logger import *
from tengine import CommandParser, event, Hasher
from tengine.telegram.telegram_utils import encode_case_id, get_file_id
from tengine.telegram.telegram_bot import EV_TEL_RECEIVED_MESSAGES, EV_TEL_SENT_MESSAGE


class MessagesLogger(CsvLogger):
    def __init__(self, dir_path, file_name_prefix, command_parser: CommandParser, hasher: Hasher):
        super().__init__(dir_path=dir_path, file_name_prefix=file_name_prefix)

        self.command_parser = command_parser
        self.hasher = hasher

        event.emitter.on(EV_TEL_RECEIVED_MESSAGES, self._on_receive_messages)
        event.emitter.on(EV_TEL_SENT_MESSAGE, self._on_self_send_message)

    def log_message(self, m: Message, is_self: bool, hide_command_password=True):
        case_id = encode_case_id(chat_id=m.chat.id,
                                 message_id=m.message_id)

        text = m.text
        if text is None:
            text = m.caption

        if hide_command_password:
            if self.command_parser.is_command(text) and self.command_parser.contains_password(text):
                text = self.command_parser.hide_password(text)

        row_dict = {
            'case_hash': self.hasher.trimmed(case_id),
            'conversation_hash': self.hasher.trimmed(m.chat.id),
            'received_dt': datetime.utcfromtimestamp(m.date),
            'is_self': is_self,
            'chat_type': m.chat.type,
            'content_type':  m.content_type,
            'text': text,
            'file_id': get_file_id(m),
        }

        self.write_row(row_dict)

    def _on_receive_messages(self, messages: Iterable[Message]):
        for m in messages:
            self.log_message(m, is_self=False, hide_command_password=True)

    def _on_self_send_message(self, m: Message):
        self.log_message(m, is_self=True, hide_command_password=False)