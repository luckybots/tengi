from typing import Any
import argparse


class CommandParam:
    def __init__(self, name: str, help_str: str, param_type: Any):
        assert name.startswith('--')

        self.name = name
        self.help_str = help_str
        self.param_type = param_type

    def add_to_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument(self.name,
                            type=str,
                            metavar='',
                            help=self.help_str)
