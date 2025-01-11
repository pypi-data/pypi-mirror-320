"""PepperPy Console package."""

from .cli.command import Command, CommandGroup
from .cli.parser import CommandParser, ParsedCommand
from .core.plugin import Plugin, PluginConfig, PluginManager
from .tui.app import PepperApp
from .tui.screens import ErrorScreen, LoadingScreen, PepperScreen
from .tui.theme import Theme, ThemeManager
from .tui.widgets.base import PepperWidget

__version__ = "0.1.0"

__all__ = [
    "Command",
    "CommandGroup",
    "CommandParser",
    "ParsedCommand",
    "Plugin",
    "PluginConfig",
    "PluginManager",
    "PepperApp",
    "ErrorScreen",
    "LoadingScreen",
    "PepperScreen",
    "Theme",
    "ThemeManager",
    "PepperWidget",
]
