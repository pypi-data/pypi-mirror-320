"""Plugin system for PepperPy Console."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import structlog
import yaml

logger = structlog.get_logger(__name__)


@dataclass
class PluginConfig:
    """Plugin configuration.

    Attributes:
        name (str): Plugin name
        description (str): Plugin description
        version (str): Plugin version
        author (str): Plugin author
        dependencies (List[str]): Plugin dependencies
        settings (Dict[str, Any]): Plugin settings
    """

    name: str
    description: str = ""
    version: str = "0.1.0"
    author: str = ""
    dependencies: List[str] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "PluginConfig":
        """Load plugin configuration from file.

        Args:
            path: Configuration file path

        Returns:
            PluginConfig: Loaded configuration
        """
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
            return cls(**data)
        except Exception as e:
            logger.error(f"Error loading plugin config from {path}: {e}")
            raise ValueError(f"Invalid plugin config: {e}")


class Plugin:
    """Base plugin class.

    All plugins should inherit from this class and implement the required methods.

    Attributes:
        config (PluginConfig): Plugin configuration
        enabled (bool): Whether the plugin is enabled
    """

    def __init__(self, config: PluginConfig) -> None:
        """Initialize the plugin.

        Args:
            config: Plugin configuration
        """
        self.config = config
        self.enabled = True

    async def initialize(self, app: Any) -> None:
        """Initialize the plugin.

        This method is called when the plugin is loaded.

        Args:
            app: Application instance
        """
        pass

    async def cleanup(self) -> None:
        """Clean up plugin resources.

        This method is called when the plugin is unloaded.
        """
        pass

    def enable(self) -> None:
        """Enable the plugin."""
        self.enabled = True
        logger.info(f"Enabled plugin {self.config.name}")

    def disable(self) -> None:
        """Disable the plugin."""
        self.enabled = False
        logger.info(f"Disabled plugin {self.config.name}")


class PluginManager:
    """Manager for plugin loading and lifecycle.

    Attributes:
        plugins (Dict[str, Plugin]): Loaded plugins
    """

    def __init__(self) -> None:
        """Initialize the plugin manager."""
        self.plugins: Dict[str, Plugin] = {}

    async def load_plugins(self, directory: Path) -> None:
        """Load plugins from directory.

        Args:
            directory: Plugin directory path
        """
        try:
            for path in directory.glob("*/plugin.yaml"):
                config = PluginConfig.load(path)
                plugin_class = self._load_plugin_class(path.parent)
                if plugin_class:
                    plugin = plugin_class(config)
                    self.plugins[config.name] = plugin
                    logger.info(f"Loaded plugin {config.name}")
        except Exception as e:
            logger.error(f"Error loading plugins: {e}")

    def _load_plugin_class(self, directory: Path) -> Optional[Type[Plugin]]:
        """Load plugin class from directory.

        Args:
            directory: Plugin directory path

        Returns:
            Optional[Type[Plugin]]: Plugin class if found
        """
        try:
            # TODO: Implement plugin class loading
            return None
        except Exception as e:
            logger.error(f"Error loading plugin class from {directory}: {e}")
            return None

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Optional[Plugin]: Plugin if found
        """
        return self.plugins.get(name)

    def list_plugins(self) -> List[Plugin]:
        """List all loaded plugins.

        Returns:
            List[Plugin]: List of plugins
        """
        return list(self.plugins.values()) 