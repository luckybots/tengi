import logging

from tengi.command.command_handler import *
from tengi.setup import config_utils

logger = logging.getLogger(__file__)


class CommandHandlerEssentials(CommandHandler):
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

    def handle(self, context: CommandContext):
        if context.command == '/start':
            response_start = config_utils.try_get_response_start(context.config)
            if response_start is not None:
                context.reply(response_start)

        elif context.command == '/help':
            response_help = config_utils.try_get_response_help(context.config)
            if response_help is not None:
                context.reply(response_help)
        elif context.command == '/help2':
            commands_help_message = '<pre>' + context.parser.format_help() + '</pre>'
            context.reply(commands_help_message)
        elif context.command == '/ping':
            context.reply('pong')
        elif context.command == '/chat_id':
            context.reply(str(context.sender_chat_id))
        else:
            raise ValueError(f'Unhandled command: {context.command}')
