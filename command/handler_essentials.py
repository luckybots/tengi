import logging

from tengine.command.command_handler import *

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
            if 'response_start' in context.config:
                context.reply(context.config['response_start'])
            else:
                logger.warning(f'Setup "response_start" in config to respond to {context.command}')
        elif context.command == '/help':
            if 'response_help' in context.config:
                context.reply(context.config['response_help'])
            else:
                logger.warning(f'Setup "response_help" in config to respond to {context.command}')
        elif context.command == '/help2':
            commands_help_message = '<pre>' + context.parser.format_help() + '</pre>'
            context.reply(commands_help_message)
        elif context.command == '/ping':
            context.reply('pong')
        elif context.command == '/chat_id':
            context.reply(str(context.sender_chat_id))
        else:
            raise ValueError(f'Unhandled command: {context.command}')
