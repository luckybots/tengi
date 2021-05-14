from typing import Any
import argparse


class CommandParam:
    def __init__(self, name: str, help_str: str, param_type: Any, nargs=None):
        assert name.startswith('--')

        self.name = name
        self.help_str = help_str
        self.param_type = param_type
        self.nargs = nargs

    def add_to_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument(self.name,
                            type=self.param_type,
                            nargs=self.nargs,
                            metavar='',
                            help=self.help_str)
