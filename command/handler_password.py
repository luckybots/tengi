import logging

from tengine.command.command_handler import *


class CommandHandlerPassword(CommandHandler):
    def get_cards(self) -> Iterable[CommandCard]:
        return [CommandCard(command_str='/remember_password',
                            description='Admin. Remember admin password for current chat. --chat_id optional.',
                            is_admin=True),
                CommandCard(command_str='/forget_password',
                            description='Admin. Forget admin password for current chat. --chat_id optional.',
                            is_admin=True)]

    def handle(self, context: CommandContext):
        remembered_passwords = context.config['remembered_passwords']
        target_chat_id = context.sender_chat_id if (context.args.chat_id is None) else context.args.chat_id
        target_chat_id_str = str(target_chat_id)
        if context.command == '/remember_password':
            remembered_passwords[target_chat_id_str] = context.args.password
            context.reply('Remembered', log_level=logging.INFO)
        elif context.command == '/forget_password':
            if target_chat_id_str in remembered_passwords:
                del remembered_passwords[target_chat_id_str]
                context.reply('Forgotten', log_level=logging.INFO)
            else:
                context.reply('Was not remembered')
        else:
            raise ValueError(f'Unhandled command: {context.command}')

        context.config['remembered_passwords'] = remembered_passwords
