import abc
from argparse import Namespace
from typing import Iterable
from telebot.types import Message

from tengine.command.card import CommandCard
from tengine.telegram.telegram_bot import TelegramBot
from tengine.config import Config


class CommandHandler:
    def __init__(self, config: Config, telegram_bot: TelegramBot):
        self.config = config
        self.telegram_bot = telegram_bot

    @abc.abstractmethod
    def get_cards(self) -> Iterable[CommandCard]:
        pass

    @abc.abstractmethod
    def handle(self,
               sender_chat_id: int,
               sender_message: Message,
               args: Namespace):
        pass
