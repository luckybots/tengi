import abc
from argparse import Namespace
from typing import Iterable

from tengine.telegram.telegram_bot import TelegramBot
from tengine.command.card import CommandCard
from tengine.command.command_parser import CommandParser
from tengine.config import Config


class CommandHandler:
    @abc.abstractmethod
    def get_cards(self) -> Iterable[CommandCard]:
        pass

    @abc.abstractmethod
    def handle(self,
               config: Config,
               chat_id,
               args: Namespace,
               telegram_bot: TelegramBot,
               command_parser: CommandParser):
        pass
