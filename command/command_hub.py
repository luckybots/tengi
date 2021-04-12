import logging
from telebot.apihelper import ApiTelegramException

from tengine.command.handler_pool import CommandHandlerPool
from tengine.command.command_parser import CommandParser
from tengine.config import Config
from tengine.telegram.telegram_bot import TelegramBot
from tengine.telegram.inbox_handler import *

logger = logging.getLogger(__file__)


class CommandHub(TelegramInboxHandler):
    def __init__(self,
                 config: Config,
                 telegram_bot: TelegramBot,
                 parser: CommandParser,
                 handler_pool: CommandHandlerPool):
        self.config = config
        self.telegram_bot = telegram_bot
        self.parser = parser

        self.handlers = {}
        self.is_admin_command = {}
        for h in handler_pool.handlers:
            for card in h.get_cards():
                if card.command_str in self.handlers:
                    raise Exception(f'Handler for {card.command_str} already added: {self.handlers[card.command_str]}')
                self.handlers[card.command_str] = h
                self.is_admin_command[card.command_str] = card.is_admin

    def message(self, message: types.Message) -> bool:
        return self.try_handle_command(message)

    def try_handle_command(self, message) -> bool:
        """
        :param message:
        :return: is message a command
        """
        chat_id = message.chat.id

        if message.chat.type == 'channel':
            logger.debug('Message ignored by command handler as it was sent in the channel')
            return False

        if message.content_type != 'text':
            logger.debug('Message ignored by command handler as it is not a text message')
            return False

        text: str = message.text
        if text is None:
            logger.debug('Message ignored by command handler as it does not have text')
            return False

        is_command, command_str = self.parser.is_command(text, return_first_word=True)
        if not is_command:
            logger.debug('Message ignored by command handler as it does not have text')
            return False

        # Hide password if it's in the command
        if self.parser.contains_secret(text):
            try:
                text_w_hide = self.parser.hide_secret(text)
                self.telegram_bot.delete_message(chat_id, message.message_id)
                self.telegram_bot.send_text(chat_id, text_w_hide)
            except ApiTelegramException as ex:
                logger.info(f'Got an exception when trying to hide password, most likely bot does not have admin '
                            f'rights: {ex}')
                self.telegram_bot.send_text(chat_id, 'Please provide admin rights for bot to be able to hide '
                                                     'password in the chat log')

        args = self.parser.parse_command(text)

        if self.parser.error_message is not None:
            logger.debug(f'command handler parser error "{self.parser.error_message}"')
            response = self.config['response_command_parser_error'].format(first_word=command_str)
            self.telegram_bot.send_text(chat_id, response)
            return True

        logger.info(f'Bot command: "{args.command}"')

        is_password_correct = self.check_password(args=args, chat_id=chat_id)

        if (message.chat.type != 'private') and (not is_password_correct):
            logger.info(f'Ignoring command as it is from non-admin in non-private chat')
        elif command_str not in self.handlers:
            response = self.config['response_unknown_command'].format(first_word=command_str)
            self.telegram_bot.send_text(chat_id=chat_id, text=response)
        elif self.is_admin_command[command_str] and (not is_password_correct):
            response = self.config['response_unknown_command'].format(first_word=command_str)
            self.telegram_bot.send_text(chat_id=chat_id, text=response)
        else:
            try:
                self.handlers[command_str].handle(sender_chat_id=chat_id,
                                                  sender_message=message,
                                                  args=args)
            except Exception as ex:
                logger.exception(ex)
                if is_password_correct:
                    self.telegram_bot.send_text(chat_id, f'Exception: {ex}')
        return True

    def check_password(self, args, chat_id):
        password = args.password
        if password is None:
            remembered_passwords = self.config['remembered_passwords']
            chat_id_str = str(chat_id)
            rem_password = remembered_passwords.get(chat_id_str, None)
            if rem_password is not None:
                if rem_password == self.config['admin_password']:
                    logger.debug(f'Used remembered password')
                    password = rem_password
                else:
                    logger.debug(f'Remembered password is outdated, forgetting')
                    del remembered_passwords[chat_id_str]
                    self.config['remembered_passwords'] = remembered_passwords
        result = (password == self.config['admin_password'])
        return result
