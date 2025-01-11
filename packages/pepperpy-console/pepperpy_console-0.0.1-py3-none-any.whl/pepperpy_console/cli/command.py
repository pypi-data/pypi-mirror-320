"""Command classes for PepperPy CLI."""

from typing import Any, Callable, Dict, List, Optional, Awaitable


class Command:
    """Command class for PepperPy CLI.

    Attributes:
        name (str): Command name
        callback (Callable): Command callback function
        description (str): Command description
        aliases (List[str]): Command aliases
    """

    def __init__(
        self,
        name: str,
        callback: Callable[..., Awaitable[Any]],
        description: str = "",
        aliases: Optional[List[str]] = None,
    ):
        """Initialize a command.

        Args:
            name: Command name
            callback: Async callback function
            description: Command description
            aliases: Optional list of command aliases
        """
        self.name = name
        self.callback = callback
        self.description = description
        self.aliases = aliases or []

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the command with arguments.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result of the callback function
        """
        return await self.callback(*args, **kwargs)


class CommandGroup:
    """Group of related commands."""

    def __init__(self):
        """Initialize a command group."""
        self.commands: Dict[str, Command] = {}

    def add_command(self, command: Command) -> None:
        """Add a command to the group.

        Args:
            command: Command to add
        """
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias] = command

    def get_command(self, name: str) -> Optional[Command]:
        """Get a command by name.

        Args:
            name: Command name

        Returns:
            Optional[Command]: Command if found
        """
        return self.commands.get(name)

    def list_commands(self) -> Dict[str, Command]:
        """List all commands in the group.

        Returns:
            Dict[str, Command]: Group commands
        """
        return self.commands
