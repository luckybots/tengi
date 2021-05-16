import abc
from typing import Iterable

from tengi.command.card import CommandCard
from tengi.command.command_context import CommandContext


class CommandHandler:
    @abc.abstractmethod
    def get_cards(self) -> Iterable[CommandCard]:
        pass

    @abc.abstractmethod
    def handle(self,
               context: CommandContext):
        pass
