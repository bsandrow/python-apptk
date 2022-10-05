import argparse
import dataclasses
import sys
import typing

from apptk.coerce import to_dataclass
from apptk.func import cached_property

ActionType = typing.Literal[
    "store", "store_const", "store_true", "store_false", "append", "append_const", "count", "help", "version", "extend"
]
SubcommandMap = dict[str, typing.Type["Command"]]


@dataclasses.dataclass
class ParserArgs:
    prog: str = None
    usage: str = None
    description: str = None
    epilog: str = None
    parents: list[argparse.ArgumentParser] = dataclasses.field(default_factory=list)
    formatter_class: typing.Type[argparse.HelpFormatter] = argparse.HelpFormatter
    prefix_chars: str = "-"
    fromfile_prefix_chars: str = None
    conflict_handler: typing.Literal["error", "resolve"] = "error"
    argument_default: typing.Any = None
    add_help: bool = True
    allow_abbrev: bool = True
    exit_on_error: bool = True

    def as_kwargs(self):
        return dataclasses.asdict(self)


@dataclasses.dataclass
class SubParserArgs:
    title: str = "Subcommands"
    description: str = None
    action: ActionType = "parsers"
    dest: str = "subparser_name"
    required: bool = False
    help = None
    metavar: str = None

    def as_kwargs(self):
        return dataclasses.asdict(self)


class Command:
    options: argparse.Namespace
    parser_args: typing.Union[dict, ParserArgs] = None
    subparsers_args: typing.Union[dict, SubParserArgs] = None
    subcommands: SubcommandMap = None

    def __init__(self):
        self.subcommands = self.subcommands or {}
        self.parser_args = self.parser_args or ParserArgs()
        self.subparsers_args = self.subparsers_args or SubParserArgs()

    @cached_property
    def argument_parser(self) -> argparse.ArgumentParser:
        parser_args = to_dataclass(self.parser_args or ParserArgs(), ParserArgs)
        parser = argparse.ArgumentParser(**parser_args.as_kwargs())
        self.add_arguments(parser)

        if self.subcommands:
            subparsers = self.add_subparser_action(parser)

            for name, command in self.subcommands.items():
                parser_kwargs = to_dataclass(command.parser_args or ParserArgs(), ParserArgs).as_kwargs()
                _parser = subparsers.add_parser(name, **parser_kwargs)
                command().add_arguments(_parser)

        return parser

    def add_subparser_action(self, parser):
        subparsers_args = to_dataclass(self.subparsers_args or SubParserArgs(), SubParserArgs)
        return parser.add_subparsers(**subparsers_args.as_kwargs())

    # noinspection PyMethodMayBeStatic
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-v", "--verbose", action="count", default=0)

    def parse_args(self, args: typing.Iterable = None) -> argparse.Namespace:
        args = sys.argv[1:] if args is None else tuple(args)
        self.options = self.argument_parser.parse_args(args)
        return self.options

    def handle(self) -> None:
        pass

    def run(self, args: typing.Iterable = None) -> None:
        self.parse_args(args)
        command = self

        if self.subcommands:
            subcommand = self.subcommands[self.options.subparser_name]
            command = subcommand()
            command.options = self.options

        command.handle()
