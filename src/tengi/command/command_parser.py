import argparse
import shlex
import re
from typing import Iterable
import itertools

from tengi.command.param import CommandParam
from tengi.command.handler_pool import CommandHandlerPool


class CommandParser(argparse.ArgumentParser):
    secret_pattern_str = r'(?i)([^\w_]+(password|bot_token)\s+)(\S+)'
    secret_pattern = re.compile(secret_pattern_str)

    def __init__(self, handler_pool: CommandHandlerPool, params: Iterable[CommandParam]):
        super().__init__(add_help=False, formatter_class=argparse.RawTextHelpFormatter)

        self.error_message = None

        cards = itertools.chain(*[h.get_cards() for h in handler_pool.handlers])
        arr_command_str = [x.command_str for x in cards]
        self.add_argument('command',
                          choices=arr_command_str,
                          type=str.lower)

        for p in params:
            p.add_to_parser(self)

        self.usage = f'[command] [parameters]'

    def validate_and_fix_params(self, params):
        pass  # Empty for now

    @classmethod
    def unify_whitespace(cls, s):
        # Ws can be obtained using the following code
        #       all_unicode = ''.join(chr(c) for c in range(sys.maxunicode+1))
        #       ws = ''.join(re.findall(r'\s', all_unicode))
        ws = '\t\n\x0b\x0c\r\x1c\x1d\x1e\x1f \x85\xa0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008' \
             '\u2009\u200a\u2028\u2029\u202f\u205f\u3000'
        unified_ws = ' '
        s2 = s.translate(s.maketrans(ws, unified_ws * len(ws)))
        return s2

    def parse_command(self, command):
        try:
            # We unify whitespace as shlex can't parse Unicode whitespaces properly
            command = self.unify_whitespace(command)
            # Fix back Telegram auto replace
            command = command.replace('—', '--')
            args = shlex.split(command)

            return self.parse_args(args)
        except Exception as e:
            self.error_message = str(e)

    def parse_args(self, *args, **kwargs):
        self.error_message = None
        try:
            params = super().parse_args(*args, **kwargs)
            # Make checks for command mandatory params to be set
            self.validate_and_fix_params(params)
            return params
        except Exception as e:
            self.error_message = str(e)

    def is_command(self, text, return_first_word=False):
        if text is None:
            return False
        text_cropped = self.unify_whitespace(text)
        text_cropped = text_cropped.strip()
        first_word = text_cropped.split(' ')[0]
        is_command = first_word[0] == '/'
        if return_first_word:
            return is_command, first_word
        else:
            return is_command

    def contains_secret(self, text):
        if text is None:
            return False
        result = self.secret_pattern.search(text) is not None
        return result

    def hide_secret(self, text):
        # \1 represents text before password(or other secret), \2 (the replaced text) -- the password itself
        text_w_hide = self.secret_pattern.sub(r'\1[HIDDEN]', text)
        return text_w_hide

    def error(self, message):
        """
        Overwrite the default parser behaviour in case of error - throws an exception instead of making exit
        """
        message = f'{message}\n*use "help" command to get help*'
        raise Exception(message)

    def format_help(self):
        help_str = super().format_help()
        # default "optional arguments" name isn't suitable for us as some of these arguments are mandatory for some
        #   commands
        help_str = help_str.replace("optional arguments", "parameters")
        # in our case "positional arguments" are used to set the command
        help_str = help_str.replace("positional arguments", "command")
        return help_str
