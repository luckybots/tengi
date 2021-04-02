import logging
import json
from tengine.command.command_handler import *

logger = logging.getLogger(__file__)


class CommandHandlerConfig(CommandHandler):
    def get_cards(self) -> Iterable[CommandCard]:
        return [CommandCard(command_str='/get_config',
                            description='Admin. Reads config variable',
                            is_admin=True),
                CommandCard(command_str='/set_config',
                            description='Admin. Sets config variable',
                            is_admin=True)]

    def handle(self,
               config: Config,
               chat_id,
               args: Namespace,
               telegram_bot: TelegramBot,
               command_parser: CommandParser):
        var_name = args.name

        if var_name is None:
            logger.info(f'Received {args.command} command without --name')
            telegram_bot.send_text(chat_id, '--name is required')
            return

        if var_name in self._get_protected_vars(config):
            logger.info(f'Received {args.command} command with protected --name {var_name}')
            telegram_bot.send_text(chat_id, f'{var_name} protected')
            return

        if var_name not in config:
            logger.info(f'Received {args.command} command with unknown --name {var_name}')
            telegram_bot.send_text(chat_id, f'{var_name} not in config')
            return

        var_old_value = config[var_name]

        if args.command == '/get_config':
            logger.info(f'Config value get: {var_name}')
            telegram_bot.send_text(chat_id, str(var_old_value))
        elif args.command == '/set_config':
            var_new_value = args.value

            if var_new_value is None:
                logger.info(f'Received {args.command} command without --value')
                telegram_bot.send_text(chat_id, '--value is required')
                return

            if type(var_old_value) != str:
                var_new_value = json.loads(var_new_value)

            if type(var_old_value) != type(var_new_value):
                logger.info(f'Config value set, types mismatch: {var_name}')
                telegram_bot.send_text(chat_id, f'Value types mismatch: {var_old_value}, {var_new_value}')
                return

            config[var_name] = var_new_value
            logger.info(f'Config value set: {var_name}')
            telegram_bot.send_text(chat_id, 'Value set successfully')
            return
        else:
            raise Exception(f'Unhandled command {args.command} (programmer mistake in if-cascade)')

    @staticmethod
    def _get_protected_vars(config: Config):
        result = []
        if 'protected_vars' in config:
            result = config['protected_vars']
        return result
