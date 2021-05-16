import logging

from tengi.command.command_handler import *
from tengi.setup import config_utils


class CommandHandlerPassword(CommandHandler):
    def get_cards(self) -> Iterable[CommandCard]:
        return [CommandCard(command_str='/remember_password',
                            description='Admin. Remember admin password for current chat. --chat_id optional.',
                            is_admin=True),
                CommandCard(command_str='/forget_password',
                            description='Admin. Forget admin password for current chat. --chat_id optional.',
                            is_admin=True)]

    def handle(self, context: CommandContext):
        target_chat_id = context.sender_chat_id if (context.args.chat_id is None) else context.args.chat_id
        if context.command == '/remember_password':
            password = context.get_mandatory_arg('password')
            config_utils.remember_password(config=context.config,
                                           chat_id=target_chat_id,
                                           password=password)
            context.reply('Remembered', log_level=logging.INFO)
        elif context.command == '/forget_password':
            if config_utils.has_remembered_password(config=context.config, chat_id=target_chat_id):
                config_utils.delete_remembered_password(config=context.config, chat_id=target_chat_id)
                context.reply('Forgotten', log_level=logging.INFO)
            else:
                context.reply('Was not remembered')
        else:
            raise ValueError(f'Unhandled command: {context.command}')
