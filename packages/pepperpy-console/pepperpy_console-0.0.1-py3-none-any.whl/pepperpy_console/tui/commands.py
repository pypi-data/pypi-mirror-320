"""Command system for TUI operations."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import structlog
from textual.containers import Container
from textual.message import Message
from textual.widgets import Input, ListView

from .widgets.base import PepperWidget

logger = structlog.get_logger(__name__)


@dataclass
class Command:
    """Command configuration.

    Attributes:
        name (str): Command name
        description (str): Command description
        handler (Callable): Command handler
        category (str): Command category
        shortcut (Optional[str]): Keyboard shortcut
    """

    name: str
    description: str
    handler: Callable
    category: str = "General"
    shortcut: Optional[str] = None


class CommandPalette(PepperWidget, Container):
    """Command palette for executing global commands.

    Attributes:
        commands (Dict[str, Command]): Available commands
        visible (bool): Whether palette is visible
    """

    class CommandExecuted(Message):
        """Command executed message.

        Attributes:
            name (str): Command name
            category (str): Command category
        """

        def __init__(self, name: str, category: str) -> None:
            """Initialize command executed message.

            Args:
                name: Command name
                category: Command category
            """
            super().__init__()
            self.name = name
            self.category = category

    class CommandError(Message):
        """Command error message.

        Attributes:
            name (str): Command name
            error (str): Error message
        """

        def __init__(self, name: str, error: str) -> None:
            """Initialize command error message.

            Args:
                name: Command name
                error: Error message
            """
            super().__init__()
            self.name = name
            self.error = error

    DEFAULT_CSS = """
    CommandPalette {
        dock: top;
        layer: command;
        width: 60%;
        margin: 1 0;
        background: $background;
        border: solid $primary;
        display: none;
    }

    CommandPalette.-visible {
        display: block;
    }

    CommandPalette Input {
        margin: 1;
    }

    CommandPalette ListView {
        height: 10;
        margin: 0 1;
    }
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the command palette."""
        super().__init__(*args, **kwargs)
        self.commands: Dict[str, Command] = {}
        self.visible = False
        self._search = Input(placeholder="Search commands...")
        self._list = ListView()
        self._filtered_commands: List[Command] = []

    def compose(self) -> None:
        """Compose the palette layout."""
        yield self._search
        yield self._list

    def register_command(self, command: Command) -> None:
        """Register a command.

        Args:
            command: Command configuration
        """
        self.commands[command.name] = command
        logger.debug(f"Registered command: {command.name}")

    def register_many(self, commands: List[Command]) -> None:
        """Register multiple commands.

        Args:
            commands: List of commands
        """
        for command in commands:
            self.register_command(command)

    async def show(self) -> None:
        """Show the command palette."""
        self.visible = True
        self.add_class("-visible")
        self._update_list()
        self._search.focus()
        await self.events.emit("palette_shown")

    async def hide(self) -> None:
        """Hide the command palette."""
        self.visible = False
        self.remove_class("-visible")
        self._search.value = ""
        await self.events.emit("palette_hidden")

    async def toggle(self) -> None:
        """Toggle palette visibility."""
        if self.visible:
            await self.hide()
        else:
            await self.show()

    async def on_input_changed(self, message: Message) -> None:
        """Handle search input changes."""
        if isinstance(message.sender, Input):
            self._update_list()

    async def on_list_view_selected(self, message: Message) -> None:
        """Handle command selection."""
        if isinstance(message.sender, ListView) and message.sender.highlighted is not None:
            command = self._filtered_commands[message.sender.highlighted]
            await self._execute_command(command)

    def _update_list(self) -> None:
        """Update the command list based on search."""
        query = self._search.value.lower()
        self._filtered_commands = [
            cmd
            for cmd in self.commands.values()
            if query in cmd.name.lower() or query in cmd.description.lower()
        ]

        self._list.clear()
        for cmd in self._filtered_commands:
            self._list.append(f"{cmd.name} - {cmd.description}")

    async def _execute_command(self, command: Command) -> None:
        """Execute a command.

        Args:
            command: Command to execute
        """
        try:
            await command.handler()
            await self.emit_no_wait(self.CommandExecuted(command.name, command.category))
            await self.hide()
        except Exception as e:
            logger.error(f"Error executing command {command.name}: {e}")
            await self.emit_no_wait(self.CommandError(command.name, str(e)))
