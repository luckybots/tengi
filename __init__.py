import logging

from tengine.app import App
from tengine.config import Config
from tengine.telegram import telegram_utils
from tengine.telegram.telegram_bot import TelegramBot
from tengine.telegram.telegram_cursor import TelegramCursor
from tengine.telegram.inbox_hub import TelegramInboxHub
from tengine.telegram.inbox_handler import TelegramInboxHandler
from tengine.command.command_handler import CommandHandler
from tengine.command.handler_essentials import CommandHandlerEssentials
from tengine.command.handler_password import CommandHandlerPassword
from tengine.command.handler_config import CommandHandlerConfig
from tengine.command.command_parser import CommandParser
from tengine.command.param import CommandParam
from tengine.command.card import CommandCard
from tengine.command.command_hub import CommandHub
from tengine.hasher import Hasher
from tengine.csv_log.csv_logger import CsvLogger
from tengine.csv_log.messages_logger import MessagesLogger
from tengine.preserve.preserver import Preserver
from tengine.preserve.chat_id_preserver import ChatIdPreserver
from tengine.hack import jsonstore_hack

jsonstore_hack.fix_jsonstore_dumps()

logging.getLogger(__name__).addHandler(logging.NullHandler())

