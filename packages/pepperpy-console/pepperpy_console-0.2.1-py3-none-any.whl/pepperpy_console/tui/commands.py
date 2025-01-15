"""Command management for PepperPy Console."""

from __future__ import annotations

from typing import Protocol

import structlog

logger = structlog.get_logger()


class Command(Protocol):
    """Command protocol."""

    name: str
    description: str
    category: str | None
    shortcut: str | None

    async def execute(self, *args: object, **kwargs: object) -> None:
        """Execute command."""
        ...


class CommandManager:
    """Command manager for PepperPy Console."""

    def __init__(self) -> None:
        """Initialize command manager."""
        self.commands: dict[str, Command] = {}

    def register_command(self, command: Command) -> None:
        """Register command.

        Args:
            command: Command to register.

        """
        logger.debug("Registered command: %s", command.name)
        self.commands[command.name] = command

    def get_command(self, name: str) -> Command:
        """Get command by name.

        Args:
            name: Command name.

        Returns:
            Command instance.

        Raises:
            KeyError: If command not found.

        """
        if name not in self.commands:
            error_msg = f"Command '{name}' not found"
            raise KeyError(error_msg)
        return self.commands[name]

    async def execute_command(self, name: str, *args: object, **kwargs: object) -> None:
        """Execute command.

        Args:
            name: Command name.
            *args: Command arguments.
            **kwargs: Command keyword arguments.

        """
        try:
            command = self.get_command(name)
            await command.execute(*args, **kwargs)
        except Exception:
            logger.exception("Error executing command %s", name)
            raise
