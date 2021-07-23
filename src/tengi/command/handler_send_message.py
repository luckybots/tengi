import logging

from tengi.command.command_handler import *


class CommandHandlerSendMessage(CommandHandler):
    def get_cards(self) -> Iterable[CommandCard]:
        return [CommandCard(command_str='/send_message',
                            description='Send message to another user via the bot',
                            is_admin=True)]

    def handle(self, context: CommandContext):
        if context.command == '/send_message':
            chat_id = context.get_mandatory_arg('chat_id')
            text = context.get_mandatory_arg('text')
            try:
                context.telegram_bot.send_text(chat_id=chat_id,
                                               text=text)
                context.reply(f'Message to {chat_id} sent', log_level=logging.INFO)
            except Exception as ex:
                context.reply(str(ex), log_level=logging.INFO)
        else:
            raise ValueError(f'Unhandled command: {context.command}')
