import abc
from typing import Iterable

from tengine.command.card import CommandCard
from tengine.command.command_context import CommandContext


class CommandHandler:
    @abc.abstractmethod
    def get_cards(self) -> Iterable[CommandCard]:
        pass

    @abc.abstractmethod
    def handle(self,
               context: CommandContext):
        pass
