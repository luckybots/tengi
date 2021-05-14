import json
from pathlib import Path
from telebot.types import Update


def test_data_path():
    return Path(__file__).parent / 'data'


def get_telegram_message_update() -> Update:
    with open(test_data_path() / 'telegram_message_update.json', 'r') as f:
        j = json.load(f)
        u = Update.de_json(j)
    return u
