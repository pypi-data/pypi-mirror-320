"""Notification system for TUI applications."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional

import structlog
from rich.text import Text
from textual.containers import Container
from textual.widgets import Static

from .base import PepperWidget

logger = structlog.get_logger(__name__)


@dataclass
class Notification:
    """Notification message configuration.

    Attributes:
        message (str): Notification message
        type (str): Message type (info, warning, error)
        timestamp (datetime): Creation timestamp
        duration (Optional[float]): Display duration in seconds
    """

    message: str
    type: str = "info"
    timestamp: datetime = None
    duration: Optional[float] = 5.0

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


class NotificationWidget(PepperWidget, Static):
    """Widget for displaying a single notification.

    Attributes:
        notification (Notification): Notification to display
    """

    DEFAULT_CSS = """
    $primary: #bd93f9;
    $secondary: #6272a4;
    $accent: #ff79c6;
    $background: #282a36;
    $text: #f8f8f2;
    $error: #ff5555;
    $warning: #ffb86c;
    $success: #50fa7b;
    $info: #8be9fd;
    $selection: #44475a;

    NotificationWidget {
        padding: 1 2;
        margin: 1 0;
        border: solid $primary;
    }

    NotificationWidget.-info {
        border: solid $info;
    }

    NotificationWidget.-warning {
        border: solid $warning;
    }

    NotificationWidget.-error {
        border: solid $error;
    }
    """

    def __init__(self, *args: Any, notification: Notification, **kwargs: Any) -> None:
        """Initialize the notification widget.

        Args:
            *args: Positional arguments
            notification: Notification to display
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.notification = notification
        self.add_class(f"-{notification.type}")

    def render(self) -> Text:
        """Render the notification.

        Returns:
            Text: Rich text representation
        """
        style = {"info": "blue", "warning": "yellow", "error": "red"}.get(
            self.notification.type, "white"
        )

        return Text.assemble(
            (f"[{self.notification.timestamp.strftime('%H:%M:%S')}] ", "dim"),
            (self.notification.message, style),
        )


class NotificationCenter(PepperWidget, Container):
    """Notification center for managing multiple notifications.

    Attributes:
        max_notifications (int): Maximum number of visible notifications
        notifications (List[Notification]): Active notifications
    """

    DEFAULT_CSS = """
    $primary: #bd93f9;
    $secondary: #6272a4;
    $accent: #ff79c6;
    $background: #282a36;
    $text: #f8f8f2;
    $error: #ff5555;
    $warning: #ffb86c;
    $success: #50fa7b;
    $info: #8be9fd;
    $selection: #44475a;

    NotificationCenter {
        dock: bottom;
        layer: notification;
        width: 100%;
        margin: 2 4;
    }
    """

    def __init__(self, *args: Any, max_notifications: int = 5, **kwargs: Any) -> None:
        """Initialize the notification center.

        Args:
            *args: Positional arguments
            max_notifications: Maximum visible notifications
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.max_notifications = max_notifications
        self.notifications: List[Notification] = []

    async def notify(
        self, message: str, type: str = "info", duration: Optional[float] = None
    ) -> None:
        """Show a new notification.

        Args:
            message: Notification message
            type: Message type
            duration: Optional display duration
        """
        notification = Notification(message, type, duration=duration)
        self.notifications.append(notification)

        # Remove old notifications if over limit
        while len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)

        await self.refresh_notifications()
        await self.events.emit("notification", notification)

        if duration:
            # Schedule removal
            async def remove():
                await self.remove_notification(notification)

            self.set_timer(duration, remove)

    async def remove_notification(self, notification: Notification) -> None:
        """Remove a notification.

        Args:
            notification: Notification to remove
        """
        if notification in self.notifications:
            self.notifications.remove(notification)
            await self.refresh_notifications()

    async def refresh_notifications(self) -> None:
        """Refresh the notification display."""
        self.remove_children()
        for notification in reversed(self.notifications):
            self.mount(NotificationWidget(notification=notification))

    def clear_all(self) -> None:
        """Clear all notifications."""
        self.notifications.clear()
        self.remove_children()
