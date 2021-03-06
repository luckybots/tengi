import json
from json import JSONDecodeError
from telebot import types
from typing import Union, Iterable, List, Optional


def encode_button_data(handler: str,
                       case_id: str,
                       response: str) -> str:
    data_dict = dict(h=handler,
                     c=case_id,
                     r=response)
    data_str = json.dumps(data_dict, separators=(',', ':'))
    data_bytes = data_str.encode('utf-8')
    # Keyboard button data should be <=64 bytes https://core.telegram.org/bots/api#inlinekeyboardbutton
    assert len(data_bytes) <= 64, f'data is too long, {len(data_bytes)} > 64'
    return data_str


def is_button_data_encoded(data: str) -> bool:
    try:
        data_dict = json.loads(data)
        result = all([key in data_dict for key in ['h', 'c', 'r']])
    except JSONDecodeError:
        result = False
    return result


def decode_button_data(data: str):
    data_dict = json.loads(data)
    return data_dict['h'], data_dict['c'], data_dict['r']


def encode_case_id(chat_id, message_id) -> str:
    return f'{chat_id}_{message_id}'


def decode_case_id(case_id: str):
    parts = case_id.split('_')
    assert len(parts) == 2
    chat_id, message_id = int(parts[0]), int(parts[1])
    return chat_id, message_id


def flat_trim_message(message: types.Message, max_len: int, terminator='…'):
    text = message.text
    if text is None:
        text = message.caption

    if text is not None:
        # Make flat
        text = ' '.join(text.split())
        if len(text) > max_len:
            trimmed_len = max_len - len(terminator)
            text = text[:trimmed_len] + terminator
    return text


def get_file_id(message: types.Message):
    file_id = None
    if message.content_type == 'photo':
        photos = message.json['photo']
        file_id = photos[0]['file_id']
    elif message.content_type == 'video':
        file_id = message.video.file_id
    elif message.content_type == 'audio':
        file_id = message.audio.file_id
    elif message.content_type == 'document':
        file_id = message.document.file_id
    elif message.content_type == 'sticker':
        file_id = message.sticker.file_id
    elif message.content_type == 'video_note':
        file_id = message.video_note.file_id
    elif message.content_type == 'voice':
        file_id = message.voice.file_id
    elif message.content_type == 'animation':
        file_id = message.animation.file_id
    return file_id


def message_contains_link(message: types.Message, link_entities=None):
    if link_entities is None:
        link_entities = ['text_link', 'url', 'phone_number', 'mention', 'email']

    return message_contains_entity(message, entity_types=link_entities)


def message_contains_entity(message: types.Message, entity_types: Iterable[str]) -> bool:
    message_entities: List[dict] = list()
    if 'entities' in message.json:
        message_entities.extend(message.json['entities'])
    if 'caption_entities' in message.json:
        message_entities.extend(message.json['caption_entities'])

    has_one_of_entities = any([m['type'] in entity_types for m in message_entities])
    return has_one_of_entities


def is_private_message(message: types.Message):
    if (message.chat is None) or (message.chat.type != 'private'):
        return False
    return True


def is_group_message(message: types.Message):
    if (message.chat is None) or (message.chat.type not in ['group', 'supergroup']):
        return False
    return True


def is_int_chat_id(str_chat_id: str):
    try:
        int(str_chat_id)
        result = True
    except ValueError:
        result = False
    return result


def is_proper_chat_id(str_chat_id: str):
    result = is_int_chat_id(str_chat_id) or \
             (str_chat_id and (str_chat_id[0] == '@'))
    return result


def to_int_chat_id_if_possible(str_chat_id: str) -> Union[str, int]:
    result = str_chat_id
    if is_int_chat_id(str_chat_id):
        result = int(str_chat_id)
    return result


def get_short_chat_id(chat_id: int):
    result = chat_id
    str_chat_id = str(chat_id)
    prefix = '-100'
    if str_chat_id.startswith(prefix):
        short_str_chat_id = str_chat_id[len(prefix):]
        result = int(short_str_chat_id)
    return result


def escape_html_tags(text: str) -> str:
    """
    Current escaping is a hotfix. The issue with replacement is that with a proper symbol escaping the message entities
    (offset and length) should also be updated.
    The hotfix idea is  to remove special symbols and keep message length the same.
    Proper escaping should do:
    & -> &amp;
    < -> &lt;
    > -> &gt;
    """
    text = text \
        .replace('&', '_') \
        .replace('<', '_') \
        .replace('>', '_')
    return text


def message_html_text_fixed(msg: types.Message) -> Optional[str]:
    if msg.text is None:
        return None
    msg_copy = types.Message.de_json(msg.json)
    msg_copy.text = escape_html_tags(msg_copy.text)
    return msg_copy.html_text


def message_html_caption_fixed(msg: types.Message) -> Optional[str]:
    if msg.caption is None:
        return None
    msg_copy = types.Message.de_json(msg.json)
    msg_copy.caption = escape_html_tags(msg_copy.caption)
    return msg_copy.html_caption


def try_get_chat_from_update(update: types.Update) -> Optional[types.Chat]:
    fields_to_check = ['message', 'edited_message', 'channel_post', 'edited_channel_post', 'my_chat_member',
                       'chat_member']
    for field in fields_to_check:
        inner_obj = getattr(update, field, None)
        if inner_obj is not None:
            chat = getattr(inner_obj, 'chat', None)
            return chat


def try_get_message_from_update(update: types.Update) -> Optional[types.Message]:
    fields_to_check = ['message', 'edited_message', 'channel_post', 'edited_channel_post']
    for field in fields_to_check:
        message = getattr(update, field, None)
        if message is not None:
            return message


def try_get_type_from_update(update: types.Update) -> Optional[str]:
    fields_to_check = ['message', 'edited_message', 'channel_post', 'edited_channel_post', 'inline_query',
                       'chosen_inline_result', 'callback_query', 'shipping_query', 'pre_checkout_query',
                       'poll', 'poll_answer', 'my_chat_member', 'chat_member']
    for field in fields_to_check:
        inner_obj = getattr(update, field, None)
        if inner_obj is not None:
            return field
