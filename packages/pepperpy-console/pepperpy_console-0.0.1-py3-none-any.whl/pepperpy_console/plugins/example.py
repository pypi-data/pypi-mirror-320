"""Example plugin for PepperPy Console."""

from typing import Any

import structlog

from ..tui.commands import Command
from ..tui.plugins import PluginProtocol
from ..tui.widgets import NotificationCenter

logger = structlog.get_logger(__name__)


class ExamplePlugin(PluginProtocol):
    """Example plugin implementation.

    This plugin demonstrates the basic plugin functionality.
    """

    def __init__(self) -> None:
        """Initialize the plugin."""
        self.app = None

    def initialize(self, app: Any) -> None:
        """Initialize the plugin.

        Args:
            app: Application instance
        """
        self.app = app
        logger.info("Example plugin initialized")

        # Register commands
        self.app.commands.register_many([
            Command(
                "Example Command",
                "Example plugin command",
                self.example_command,
            ),
        ])

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        logger.info("Example plugin cleaned up")

    async def example_command(self) -> None:
        """Example command handler."""
        await self.app.query_one(NotificationCenter).notify(
            "Example plugin command executed!", type="info"
        )
