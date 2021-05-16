from typing import Iterable
from telebot import types as bot_types
from telethon.tl import types as api_types


def api_to_bot_markup(api_markup: api_types.ReplyInlineMarkup) -> bot_types.InlineKeyboardMarkup:
    bot_markup = bot_types.InlineKeyboardMarkup()
    for api_r in api_markup.rows:
        bot_r = []
        for api_b in api_r.buttons:
            if isinstance(api_b, api_types.KeyboardButtonCallback):
                bot_b = bot_types.InlineKeyboardButton(text=api_b.text,
                                                       callback_data=api_b.data.decode(encoding='utf-8'))
            elif isinstance(api_b, api_types.KeyboardButtonUrl):
                bot_b = bot_types.InlineKeyboardButton(text=api_b.text,
                                                       url=api_b.url)
            else:
                raise TypeError(f'Unhandled button type: {type(api_b)}')
            bot_r.append(bot_b)
        bot_markup.add(*bot_r)
    return bot_markup


def iterate_buttons(message: api_types.Message) -> Iterable[api_types.KeyboardButton]:
    if message.reply_markup is not None:
        for row in message.reply_markup.rows:
            for b in row.buttons:
                yield b
