import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException
from typing import Collection, List
import logging

from tengi import event
from tengi.telegram import telegram_error, telegram_bot_utils

logger = logging.getLogger(__file__)

EV_TEL_SENT_MESSAGE = 'telegram.send_message'
EV_TEL_RECEIVED_MESSAGES = 'telegram.received_messages'


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class TelegramBot:
    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token, parse_mode='HTML')
        self.last_bot_update_id = None

    def send_text(self,
                  chat_id,
                  text,
                  reply_to_message_id=None,
                  buttons: Collection[str] = None,
                  buttons_data: Collection[str] = None,
                  buttons_columns=2):
        reply_markup = self._build_reply_markup(buttons=buttons,
                                                buttons_data=buttons_data,
                                                buttons_columns=buttons_columns)

        sent_message = self.bot.send_message(chat_id=chat_id,
                                             text=text,
                                             reply_to_message_id=reply_to_message_id,
                                             reply_markup=reply_markup)
        event.emitter.emit(EV_TEL_SENT_MESSAGE, sent_message)

    def resend_message(self,
                       chat_id,
                       src_message: types.Message,
                       buttons: Collection[str] = None,
                       buttons_data: Collection[str] = None,
                       buttons_columns=2):
        reply_markup = self._build_reply_markup(buttons=buttons,
                                                buttons_data=buttons_data,
                                                buttons_columns=buttons_columns)
        reply_to_message_id = None if (src_message.reply_to_message is None) \
            else src_message.reply_to_message.message_id

        params_dict = dict(chat_id=chat_id,
                           reply_markup=reply_markup,
                           reply_to_message_id=reply_to_message_id)
        if src_message.text is not None:
            params_dict['text'] = telegram_bot_utils.message_html_text_fixed(src_message)
        elif src_message.caption is not None:
            params_dict['caption'] = telegram_bot_utils.message_html_caption_fixed(src_message)

        if src_message.content_type == 'text':
            send_func = self.bot.send_message
        elif src_message.content_type == 'photo':
            photos = src_message.json['photo']
            params_dict['photo'] = photos[0]['file_id']
            send_func = self.bot.send_photo
        elif src_message.content_type == 'video':
            params_dict['data'] = src_message.video.file_id
            send_func = self.bot.send_video
        elif src_message.content_type == 'audio':
            params_dict['audio'] = src_message.audio.file_id
            send_func = self.bot.send_audio
        elif src_message.content_type == 'document':
            params_dict['data'] = src_message.document.file_id
            send_func = self.bot.send_document
        elif src_message.content_type == 'sticker':
            params_dict['data'] = src_message.sticker.file_id
            send_func = self.bot.send_sticker
        elif src_message.content_type == 'video_note':
            params_dict['data'] = src_message.video_note.file_id
            send_func = self.bot.send_video_note
        elif src_message.content_type == 'voice':
            params_dict['voice'] = src_message.voice.file_id
            send_func = self.bot.send_voice
        elif src_message.content_type == 'location':
            params_dict['location'] = src_message.location
            send_func = self.bot.send_location
        elif src_message.content_type == 'contact':
            params_dict['phone_number'] = src_message.contact.phone_number
            params_dict['first_name'] = src_message.contact.first_name
            params_dict['last_name'] = src_message.contact.last_name
            params_dict['vcard'] = src_message.contact.vcard
            send_func = self.bot.send_contact
        else:
            raise ValueError(f'Resending of {src_message.content_type} content not supported')

        assert send_func is not None
        sent_message = send_func(**params_dict)
        event.emitter.emit(EV_TEL_SENT_MESSAGE, sent_message)

    def edit_message_text(self,
                          text,
                          content_type,
                          chat_id,
                          message_id):
        if content_type == 'text':
            self.bot.edit_message_text(text=text,
                                       chat_id=chat_id,
                                       message_id=message_id)
        else:
            self.bot.edit_message_caption(chat_id=chat_id,
                                          message_id=message_id,
                                          caption=text)

    def forward_message(self, to_chat_id, from_chat_id, message_id):
        sent_message = self.bot.forward_message(to_chat_id, from_chat_id, message_id)
        event.emitter.emit(EV_TEL_SENT_MESSAGE, sent_message)

    def delete_message(self, chat_id, message_id):
        self.bot.delete_message(chat_id, message_id)

    def answer_callback_query(self, callback_query_id, text=None):
        self.bot.answer_callback_query(callback_query_id=callback_query_id, text=text)

    def get_updates(self,
                    offset=None,
                    limit=None,
                    long_polling_timeout=20,
                    try_delete_webhook=True,
                    allowed_updates=None):
        """
        :param offset:
        :param limit:
        :param long_polling_timeout:
        :param try_delete_webhook: fixes an issue with a parallel bot setup a webhook which is incompatible approach to
                   get_updates
        :param allowed_updates:
        :return:
        """
        try:
            updates: List[types.Update] = self.bot.get_updates(offset=offset,
                                                               limit=limit,
                                                               long_polling_timeout=long_polling_timeout,
                                                               allowed_updates=allowed_updates)
        except ApiTelegramException as ex:
            if try_delete_webhook and (ex.error_code == telegram_error.CONFLICT):
                logger.info(f'Got Telegram exception on get updates, will try to remove webhook & repeat: {ex}')
                self.bot.delete_webhook(drop_pending_updates=False)
                updates = self.get_updates(offset=offset,
                                           limit=limit,
                                           long_polling_timeout=long_polling_timeout,
                                           try_delete_webhook=False)
            else:
                raise ex

        received_messages = [u.message for u in updates if u.message is not None]
        if received_messages:
            event.emitter.emit(EV_TEL_RECEIVED_MESSAGES, received_messages)

        return updates

    @staticmethod
    def _build_reply_markup(buttons: Collection[str],
                            buttons_data: Collection[str],
                            buttons_columns: int):
        reply_markup = None
        if buttons is not None:
            if buttons_data is None:
                buttons_data = buttons
            assert len(buttons) == len(buttons_data), \
                f'Buttons & buttons data size mismatch: {len(buttons)} != {len(buttons_data)}'

            reply_markup = types.InlineKeyboardMarkup()

            buttons_obj = [types.InlineKeyboardButton(text=text, callback_data=data)
                           for text, data in zip(buttons, buttons_data)]
            buttons_rows = list(chunks(buttons_obj, n=buttons_columns))

            for row in buttons_rows:
                reply_markup.add(*row)
        return reply_markup
