import logging
import json

from tengi.command.command_handler import *
from tengi.setup import config_utils

logger = logging.getLogger(__file__)


class CommandHandlerConfig(CommandHandler):
    def get_cards(self) -> Iterable[CommandCard]:
        return [CommandCard(command_str='/get_config',
                            description='Admin. Reads config variable',
                            is_admin=True),
                CommandCard(command_str='/set_config',
                            description='Admin. Sets config variable',
                            is_admin=True)]

    def handle(self, context: CommandContext):
        var_name = context.get_mandatory_arg('name')

        if config_utils.is_variable_protected(config=context.config, variable=var_name):
            logger.info(f'Received {context.command} command with protected --name {var_name}')
            context.reply(f'{var_name} protected')
            return

        if var_name not in context.config:
            logger.info(f'Received {context.command} command with unknown --name {var_name}')
            context.reply(f'{var_name} not in config')
            return

        var_old_value = context.config[var_name]

        if context.command == '/get_config':
            context.reply(str(var_old_value), log_level=logging.INFO)
        elif context.command == '/set_config':
            var_new_value = context.get_mandatory_arg('value')

            if type(var_old_value) != str:
                var_new_value = json.loads(var_new_value)

            if type(var_old_value) != type(var_new_value):
                context.reply(f'Value types mismatch: {var_old_value}, {var_new_value}',
                              log_level=logging.INFO)
                return

            context.config[var_name] = var_new_value
            context.reply(f'Value {var_name} set successfully', log_level=logging.INFO)
            return
        else:
            raise Exception(f'Unhandled command {context.command} (programmer mistake in if-cascade)')

