from tengine.command.command_handler import *


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

    def handle(self,
               config: Config,
               chat_id,
               args: Namespace,
               telegram_bot: TelegramBot,
               command_parser: CommandParser):
        if args.command == '/start':
            telegram_bot.send_text(chat_id, config['response_start'])
        elif args.command == '/help':
            telegram_bot.send_text(chat_id, config['response_help'])
        elif args.command == '/help2':
            commands_help_message = '<pre>' + command_parser.format_help() + '</pre>'
            telegram_bot.send_text(chat_id, commands_help_message)
        elif args.command == '/ping':
            telegram_bot.send_text(chat_id, 'pong')
        elif args.command == '/chat_id':
            telegram_bot.send_text(chat_id, chat_id)
        else:
            raise ValueError(f'Unhandled command: {args.command}')