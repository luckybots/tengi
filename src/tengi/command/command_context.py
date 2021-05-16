from argparse import Namespace
from typing import Any, TYPE_CHECKING
from tengi.telegram.reply_context import *
from tengi.setup.config import Config
from tengi.command.command_error import CommandMissingArgError

if TYPE_CHECKING:
    from tengi.command.command_parser import CommandParser


class CommandContext(ReplyContextTelegram):
    def __init__(self,
                 telegram_bot: TelegramBot,
                 sender_message: Message,
                 config: Config,
                 parser: 'CommandParser',
                 args: Namespace):
        super().__init__(telegram_bot=telegram_bot, sender_message=sender_message)
        self.config = config
        self.parser = parser
        self.args = args

    @property
    def command(self):
        return self.args.command

    def get_mandatory_arg(self, arg_name: str, cast_func: Optional[Callable] = None) -> Any:
        value = getattr(self.args, arg_name)
        if value is None:
            raise CommandMissingArgError(f'--{arg_name} required')
        if cast_func is not None:
            try:
                value = cast_func(value)
            except ValueError:
                raise CommandMissingArgError(f'--{arg_name} should have type {cast_func}')
        return value

    def get_optional_arg(self, arg_name: str, default: Any) -> Any:
        value = getattr(self.args, arg_name, default)
        return value
