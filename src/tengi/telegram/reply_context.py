from typing import Callable, Optional
import logging

from telebot.types import Message
from tengi.telegram.telegram_bot import TelegramBot

LogFunc = Optional[Callable[[str], None]]

logger = logging.getLogger(__file__)


class ReplyContext:
    def reply(self,
              text: str,
              log_level: Optional[int] = logging.DEBUG,
              stacklevel: int = 2) -> None:
        """
        @param text:
        @type text:
        @param log_level:
        @type log_level:
        @param stacklevel:
        @type stacklevel: stacklevel = 1 is the current function, stacklevel = 2 is the outside calling function
        @return:
        @rtype:
        """
        if log_level is not None:
            # Log using the module name of the previous module
            logger.log(level=log_level, msg=text, stacklevel=stacklevel)


class ReplyContextTelegram(ReplyContext):
    def __init__(self,
                 telegram_bot: TelegramBot,
                 sender_message: Message):
        self.telegram_bot = telegram_bot
        self.sender_message = sender_message

    @property
    def sender_chat_id(self) -> int:
        return self.sender_message.chat.id

    def reply(self,
              text: str,
              log_level: Optional[int] = logging.DEBUG,
              stacklevel: int = 3) -> None:
        """

        @param text:
        @type text:
        @param log_level:
        @type log_level:
        @param stacklevel:
        @type stacklevel: stacklevel = 3 means outside function taking into account call to super().reply
        @return:
        @rtype:
        """
        super().reply(text=text, log_level=log_level, stacklevel=stacklevel)

        if (self.sender_message is None) or (self.sender_message.reply_to_message is None):
            reply_to_message_id = None
        else:
            reply_to_message_id = self.sender_message.reply_to_message.message_id

        self.telegram_bot.send_text(chat_id=self.sender_chat_id,
                                    reply_to_message_id=reply_to_message_id,
                                    text=text)


class ReplyContextSuppress(ReplyContext):

    def reply(self,
              text: str,
              log_level: Optional[int] = logging.DEBUG,
              stacklevel: int = 2) -> None:
        pass
