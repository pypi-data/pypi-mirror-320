"""Clock plugin for displaying current time."""

from datetime import datetime
from typing import Any

import structlog
from pepperpy_core.plugin import PluginConfig
from pepperpy_core.plugin import plugin as Plugin
from textual.widgets import Static

from pepperpy_console.tui.widgets.base import PepperWidget

logger = structlog.get_logger(__name__)


class ClockWidget(PepperWidget, Static):
    """Widget for displaying current time."""

    def __init__(self, *args: Any, format: str = "%H:%M:%S", **kwargs: Any) -> None:
        """Initialize the clock widget."""
        super().__init__(*args, **kwargs)
        self.format = format
        self.update_timer = None

    def compose(self) -> None:
        """Compose the widget layout."""
        self.update_display()

    def on_mount(self) -> None:
        """Handle widget mount event."""
        self.update_timer = self.set_interval(1.0, self.update_display)

    def update_display(self) -> None:
        """Update the time display."""
        current_time = datetime.now().strftime(self.format)
        self.update(current_time)


class ClockPlugin(Plugin):
    """Clock plugin implementation using pepperpy-core Plugin base."""

    def configure(self) -> PluginConfig:
        """Configure the plugin."""
        return PluginConfig(
            name="clock",
            version="1.0.0",
            description="Live clock widget plugin",
            requires=[],
            hooks=["app.startup", "app.shutdown"],
            settings={"format": "%H:%M:%S", "enabled": True},
        )

    async def initialize(self) -> None:
        """Initialize the plugin."""
        # Create clock widget
        self.widget = ClockWidget(format=self.settings["format"])

        # Add to header right
        header = self.app.query_one("Header")
        header.mount(self.widget)

        logger.info("Clock plugin initialized")

    async def cleanup(self) -> None:
        """Clean up plugin resources."""
        if hasattr(self, "widget") and self.widget.update_timer:
            self.widget.update_timer.stop()
        logger.info("Clock plugin cleaned up")

    @Plugin.hook("app.startup")
    async def on_startup(self) -> None:
        """Handle application startup."""
        logger.info("Clock plugin starting up")

    @Plugin.hook("app.shutdown")
    async def on_shutdown(self) -> None:
        """Handle application shutdown."""
        logger.info("Clock plugin shutting down")
