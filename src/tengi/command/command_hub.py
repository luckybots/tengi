import logging
from telebot.apihelper import ApiTelegramException

from tengi.command.handler_pool import CommandHandlerPool
from tengi.command.command_parser import CommandParser
from tengi.setup.config import Config
from tengi.setup import config_utils
from tengi.telegram.telegram_bot import TelegramBot
from tengi.telegram.inbox_handler import *
from tengi.command.command_context import CommandContext
from tengi.command.command_error import CommandMissingArgError

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
        """
        No need to check for message to be from other bot -- bots in Telegram don't receive messages from other bots
            https://core.telegram.org/bots/faq
        :param message:
        :type message:
        :return:
        :rtype:
        """
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
            # Reply in private chats only as in groups multiple bots may be present
            if message.chat.type == 'private':
                response = config_utils.get_response_command_parser_error(config=self.config, command=command_str)
                self.telegram_bot.send_text(chat_id, response)
            return True

        logger.info(f'Bot command: "{args.command}"')

        is_password_correct = self.check_password(args=args, chat_id=chat_id) or \
            self.check_password(args=args, chat_id=message.from_user.id)
        if (message.chat.type != 'private') and (not is_password_correct):
            logger.info(f'Ignoring command as it is from non-admin in non-private chat')
            return True

        has_no_handler = command_str not in self.handlers
        admin_fail_auth = self.is_admin_command[command_str] and (not is_password_correct)
        if has_no_handler or admin_fail_auth:
            response = config_utils.get_response_unknown_command(config=self.config, command=command_str)
            self.telegram_bot.send_text(chat_id=chat_id, text=response)
            return True

        context = CommandContext(telegram_bot=self.telegram_bot,
                                 sender_message=message,
                                 config=self.config,
                                 parser=self.parser,
                                 args=args)
        try:
            self.handlers[command_str].handle(context)
        except CommandMissingArgError as ex:
            context.reply(str(ex), log_level=logging.INFO)
        except Exception as ex:
            logger.exception(ex)
            if is_password_correct:
                context.reply(str(ex), log_level=None)
        return True

    def check_password(self, args, chat_id):
        provided_password = args.password
        admin_password = config_utils.try_get_admin_password(self.config)
        if provided_password is None:
            rem_password = config_utils.try_get_remembered_password(config=self.config, chat_id=chat_id)
            if rem_password is not None:
                if rem_password == admin_password:
                    logger.debug(f'Used remembered password')
                    provided_password = rem_password
                else:
                    logger.debug(f'Remembered password is outdated, forgetting')
                    config_utils.delete_remembered_password(config=self.config, chat_id=chat_id)
        result = (provided_password == admin_password)
        return result
