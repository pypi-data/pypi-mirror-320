"""Command management module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine, Sequence


CommandResult = TypeVar("CommandResult", str, int, float, bool, None)


class CommandProtocol(Protocol):
    """Protocol for command execution."""

    async def execute(
        self,
        *args: str | float | bool | None,
        **kwargs: str | float | bool | None,
    ) -> str | int | float | bool | None:
        """Execute the command with arguments."""


class InvalidCommandResultError(TypeError):
    """Error raised when a command returns an invalid type."""

    def __init__(self, result_type: type) -> None:
        """Initialize the error.

        Args:
            result_type: The invalid result type.

        """
        super().__init__(f"Command returned invalid type: {result_type}")


class Command:
    """Base class for all commands."""

    def __init__(
        self,
        name: str,
        callback: Callable[..., Coroutine[Any, Any, str | int | float | bool | None]],
        description: str = "",
        aliases: Sequence[str] | None = None,
    ) -> None:
        """Initialize a command.

        Args:
            name: The name of the command.
            callback: The function to execute when the command is called.
            description: A description of what the command does.
            aliases: Alternative names for the command.

        """
        self.name = name
        self._callback = callback
        self.description = description
        self.aliases = aliases or []

    @property
    def callback(
        self,
    ) -> Callable[..., Coroutine[Any, Any, str | int | float | bool | None]]:
        """Get the command callback.

        Returns:
            The command callback.

        """
        return self._callback

    async def execute(
        self,
        *args: str | float | bool | None,
        **kwargs: str | float | bool | None,
    ) -> str | int | float | bool | None:
        """Execute the command with arguments.

        Args:
            *args: Positional arguments for the command.
            **kwargs: Keyword arguments for the command.

        Returns:
            The result of executing the command.

        Raises:
            InvalidCommandResultError: If the command returns an invalid type.

        """
        result = await self.callback(*args, **kwargs)
        if not isinstance(result, str | int | float | bool) and result is not None:
            raise InvalidCommandResultError(type(result))
        return result


class CommandGroup:
    """Group of related commands."""

    def __init__(self) -> None:
        """Initialize a command group."""
        self.commands: dict[str, Command] = {}

    def add_command(self, command: Command) -> None:
        """Add a command to the group.

        Args:
            command: The command to add.

        """
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias] = command

    def get_command(self, name: str) -> Command | None:
        """Get a command by name.

        Args:
            name: The name of the command.

        Returns:
            The command if found, None otherwise.

        """
        return self.commands.get(name)

    def get_commands(self) -> list[Command]:
        """Get all commands in the group.

        Returns:
            A list of all commands.

        """
        return list(self.commands.values())
