from tengine.command.command_handler import *


class CommandHandlerPassword(CommandHandler):
    def get_cards(self) -> Iterable[CommandCard]:
        return [CommandCard(command_str='/remember_password',
                            description='Admin. Remember admin password for current chat. --chat_id optional.',
                            is_admin=True),
                CommandCard(command_str='/forget_password',
                            description='Admin. Forget admin password for current chat. --chat_id optional.',
                            is_admin=True)]

    def handle(self,
               config: Config,
               chat_id,
               message: Message,
               args: Namespace,
               telegram_bot: TelegramBot,
               command_parser: CommandParser):
        remembered_passwords = config['remembered_passwords']
        target_chat_id = chat_id if (args.chat_id is None) else args.chat_id
        target_chat_id_str = str(target_chat_id)
        if args.command == '/remember_password':
            remembered_passwords[target_chat_id_str] = args.password
            telegram_bot.send_text(chat_id, 'Remembered')
        elif args.command == '/forget_password':
            if target_chat_id_str in remembered_passwords:
                del remembered_passwords[target_chat_id_str]
                telegram_bot.send_text(chat_id, 'Forgotten')
            else:
                telegram_bot.send_text(chat_id, 'Was not remembered')
        else:
            raise ValueError(f'Unhandled command: {args.command}')

        config['remembered_passwords'] = remembered_passwords
