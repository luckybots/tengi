import logging
from typing import Optional

from tengi.setup.config import Config

logger = logging.getLogger(__file__)


def get_protected_vars(config: Config) -> list:
    result = config['protected_vars'] if ('protected_vars' in config) else []
    return result


def is_variable_protected(config: Config, variable: str) -> bool:
    protected_vars = get_protected_vars(config)
    return variable in protected_vars


def get_remembered_passwords(config: Config) -> dict:
    result = config['remembered_passwords'] if ('remembered_passwords' in config) else dict()
    return result


def update_remembered_passwords(config: Config, remembered_passwords: dict):
    config['remembered_passwords'] = remembered_passwords


def delete_remembered_password(config: Config, chat_id):
    assert has_remembered_password(config=config, chat_id=chat_id)
    remembered_passwords = get_remembered_passwords(config)
    str_chat_id = str(chat_id)
    del remembered_passwords[str_chat_id]
    update_remembered_passwords(config=config, remembered_passwords=remembered_passwords)


def has_remembered_password(config: Config, chat_id) -> bool:
    remembered_passwords = get_remembered_passwords(config)
    str_chat_id = str(chat_id)
    return str_chat_id in remembered_passwords


def remember_password(config: Config, chat_id, password: str):
    remembered_passwords = get_remembered_passwords(config)
    str_chat_id = str(chat_id)
    remembered_passwords[str_chat_id] = password
    update_remembered_passwords(config=config, remembered_passwords=remembered_passwords)


def try_get_remembered_password(config: Config, chat_id) -> Optional[str]:
    arr_rem_passwords = get_remembered_passwords(config)
    chat_id_str = str(chat_id)
    rem_password = arr_rem_passwords.get(chat_id_str, None)
    return rem_password


def try_get_admin_password(config: Config):
    return config.try_get_warny('admin_password', operation_name='control access to admin commands')


def get_response_command_parser_error(config: Config, command: str):
    format_str = config['response_command_parser_error'] if ('response_command_parser_error' in config) else \
        '{command} error'
    result = format_str.format(command=command)
    return result


def get_response_unknown_command(config: Config, command: str):
    format_str = config['response_unknown_command'] if ('response_unknown_command' in config) else '{command} unknown'
    result = format_str.format(command=command)
    return result


def try_get_response_start(config: Config) -> Optional[str]:
    return config.try_get_warny('response_start', operation_name='respond to /start')


def try_get_response_help(config: Config) -> Optional[str]:
    return config.try_get_warny('response_help', operation_name='respond to /help')
