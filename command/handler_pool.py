from typing import List
from tengine.command.command_handler import CommandHandler


class CommandHandlerPool:
    def __init__(self, handlers: List[CommandHandler]):
        self.handlers = handlers
