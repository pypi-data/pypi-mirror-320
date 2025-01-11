"""Main application for PepperPy TUI."""

from pathlib import Path
from typing import Dict, Type

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Static

from ..cli.command import CommandGroup
from ..cli.help import HelpManager
from ..cli.keyboard import KeyboardManager
from ..cli.plugin import PluginManager
from .screens import LoadingScreen, PepperScreen
from .theme import ThemeManager


class PepperApp(App):
    """Main application class for PepperPy TUI.

    Attributes:
        screen_map (Dict[str, Type[PepperScreen]]): Map of screen names to screen classes
        themes (ThemeManager): Theme manager
        keyboard (KeyboardManager): Keyboard manager
        commands (CommandGroup): Command group
        help (HelpManager): Help manager
        plugins (PluginManager): Plugin manager
    """

    def __init__(self) -> None:
        """Initialize the application."""
        super().__init__()
        self.screen_map: Dict[str, Type[PepperScreen]] = {}
        self.themes = ThemeManager()
        self.keyboard = KeyboardManager()
        self.commands = CommandGroup()
        self.help = HelpManager()
        self.plugins = PluginManager()
        self.current_screen = None

    def compose(self) -> ComposeResult:
        """Compose the application layout.

        Returns:
            ComposeResult: Application composition result
        """
        yield Static("Welcome to PepperPy!")

    async def push_screen(self, screen: Screen) -> None:
        """Push a screen onto the stack.

        Args:
            screen: Screen to push
        """
        if self.current_screen:
            await self.current_screen.remove()
        self.current_screen = screen
        self.screen = screen

    async def pop_screen(self) -> None:
        """Pop the top screen from the stack."""
        if self.current_screen:
            await self.current_screen.remove()
            self.current_screen = None

    async def show_loading(self, message: str = "Loading...") -> None:
        """Show the loading screen.

        Args:
            message: Loading message to display
        """
        screen = LoadingScreen(message=message)
        await self.push_screen(screen)

    async def load_plugins(self, plugin_dir: Path) -> None:
        """Load plugins from a directory.

        Args:
            plugin_dir: Plugin directory path
        """
        await self.plugins.load_plugins(plugin_dir)

    async def load_themes(self, themes_dir: Path) -> None:
        """Load themes from a directory.

        Args:
            themes_dir: Themes directory path
        """
        await self.themes.load_themes(themes_dir)
