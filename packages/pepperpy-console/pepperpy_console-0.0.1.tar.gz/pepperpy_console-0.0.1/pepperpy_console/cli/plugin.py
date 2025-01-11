"""Plugin management for PepperPy CLI."""

from pathlib import Path
from typing import Dict

from .command import Command


class Plugin:
    """Plugin class for PepperPy CLI.

    Attributes:
        name (str): Plugin name
        commands (Dict[str, Command]): Plugin commands
    """

    def __init__(self, name: str) -> None:
        """Initialize the plugin.

        Args:
            name: Plugin name
        """
        self.name = name
        self.commands: Dict[str, Command] = {}


class PluginManager:
    """Plugin manager for PepperPy CLI.

    Attributes:
        plugins (Dict[str, Plugin]): Plugin map
    """

    def __init__(self) -> None:
        """Initialize the plugin manager."""
        self.plugins: Dict[str, Plugin] = {}

    async def load_plugins(self, directory: Path) -> None:
        """Load plugins from a directory.

        Args:
            directory: Plugin directory path
        """
        # Load plugins from the directory
        for path in directory.glob("*.py"):
            if path.stem != "__init__":
                plugin = Plugin(path.stem)
                self.plugins[plugin.name] = plugin

    def get_plugin(self, name: str) -> Plugin:
        """Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin: Plugin instance

        Raises:
            ValueError: If plugin not found
        """
        if name not in self.plugins:
            raise ValueError(f"Plugin not found: {name}")
        return self.plugins[name]

    def list_plugins(self) -> Dict[str, Plugin]:
        """List all plugins.

        Returns:
            Dict[str, Plugin]: Plugin map
        """
        return self.plugins 