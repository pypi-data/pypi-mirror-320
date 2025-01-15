"""Exceptions for the CLI module."""

from __future__ import annotations


class CommandNotFoundError(Exception):
    """Raised when a command is not found."""

    def __init__(self, command_name: str) -> None:
        """Initialize the exception.

        Args:
            command_name: The name of the command that was not found

        """
        super().__init__(f"Command not found: {command_name}")
