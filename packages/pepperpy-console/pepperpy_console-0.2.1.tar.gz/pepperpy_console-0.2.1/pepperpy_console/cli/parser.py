"""Command parser for PepperPy CLI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ParsedCommand:
    """Parsed command data.

    Attributes:
        name (str): Command name
        args (List[str]): Command arguments

    """

    name: str
    args: list[str]


class CommandParser:
    """Parser for command strings."""

    async def parse(self, command_str: str) -> tuple[str, dict] | None:
        """Parse a command string.

        Args:
            command_str: Command string to parse

        Returns:
            Tuple of command name and arguments, or None if input is empty

        """
        # Handle empty input
        if not command_str or command_str.isspace():
            return None

        # Split command string into parts
        parts = command_str.strip().split()
        if not parts:
            return None

        command_name = parts[0]
        args = parts[1:]

        if args:
            return command_name, {"args": args}
        return command_name, {}

    def _split_args(self, args_str: str) -> list[str]:
        """Split argument string into individual arguments.

        Args:
            args_str: Argument string

        Returns:
            List[str]: List of arguments

        """
        args = []
        current_arg = []
        in_quotes = False
        quote_char = None

        for char in args_str:
            if char in ('"', "'"):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                else:
                    current_arg.append(char)
            elif char.isspace() and not in_quotes:
                if current_arg:
                    args.append("".join(current_arg))
                    current_arg = []
            else:
                current_arg.append(char)

        if current_arg:
            args.append("".join(current_arg))

        return args
