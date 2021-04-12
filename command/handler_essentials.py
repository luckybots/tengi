import logging
from typing import Callable

from tengine.command.command_handler import *
from tengine.command.command_parser import CommandParser

logger = logging.getLogger(__file__)


class CommandHandlerEssentials(CommandHandler):
    def __init__(self, config: Config, telegram_bot: TelegramBot, get_parser: Callable[[], CommandParser]):
        super().__init__(config=config, telegram_bot=telegram_bot)
        self.get_parser = get_parser

    def get_cards(self) -> Iterable[CommandCard]:
        return [CommandCard(command_str='/start',
                            description='Start working with a bot',
                            is_admin=False),
                CommandCard(command_str='/help',
                            description='User help message',
                            is_admin=False),
                CommandCard(command_str='/help2',
                            description='Admin. Print help for the commands',
                            is_admin=True),
                CommandCard(command_str='/ping',
                            description='Checks if the bot is working',
                            is_admin=False),
                CommandCard(command_str='/chat_id',
                            description='Get the current chat id',
                            is_admin=True),
                ]

    def handle(self,
               sender_chat_id,
               sender_message: Message,
               args: Namespace):
        if args.command == '/start':
            if 'response_start' in self.config:
                self.telegram_bot.send_text(sender_chat_id, self.config['response_start'])
            else:
                logger.warning(f'Setup "response_start" in config to respond to {args.command}')
        elif args.command == '/help':
            if 'response_help' in self.config:
                self.telegram_bot.send_text(sender_chat_id, self.config['response_help'])
            else:
                logger.warning(f'Setup "response_help" in config to respond to {args.command}')
        elif args.command == '/help2':
            commands_help_message = '<pre>' + self.get_parser().format_help() + '</pre>'
            self.telegram_bot.send_text(sender_chat_id, commands_help_message)
        elif args.command == '/ping':
            self.telegram_bot.send_text(sender_chat_id, 'pong')
        elif args.command == '/chat_id':
            self.telegram_bot.send_text(sender_chat_id, sender_chat_id)
        else:
            raise ValueError(f'Unhandled command: {args.command}')
