"""Notification system for TUI applications."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar, Literal

import structlog
from rich.text import Text
from textual.containers import Container
from textual.widgets import Static

from .base import EventData, PepperWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult


logger = structlog.get_logger(__name__)


NotificationSeverity = Literal["information", "warning", "error"]
NotificationType = Literal["info", "warning", "error"]


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
    type: NotificationType = "info"
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float | None = 5.0


class NotificationWidget(PepperWidget, Static):
    """Widget for displaying a single notification.

    Attributes:
        notification (Notification): Notification to display

    """

    # Class variables for Widget protocol
    DEFAULT_CLASSES: ClassVar[set[str]] = {"notification"}

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

    def __init__(
        self,
        *args: tuple[()],
        notification: Notification,
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize the notification widget.

        Args:
            notification: The notification to display.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        # Initialize base classes with required attributes
        super().__init__(*args, **kwargs)

        # Set required Widget attributes
        self.id = f"notification-{notification.timestamp.strftime('%Y%m%d%H%M%S%f')}"
        self.classes = self.DEFAULT_CLASSES | {f"-{notification.type}"}
        self.styles = {}

        # Set notification-specific attributes
        self.notification = notification
        self._cleanup_task: asyncio.Task[None] | None = None

        # Start cleanup task if duration is set
        if notification.duration is not None:
            self._cleanup_task = asyncio.create_task(self._auto_cleanup())

    def render(self) -> Text:
        """Render the notification.

        Returns:
            Text: Rich text representation

        """
        style = {"info": "blue", "warning": "yellow", "error": "red"}.get(
            self.notification.type,
            "white",
        )

        return Text.assemble(
            (f"[{self.notification.timestamp.strftime('%H:%M:%S')}] ", "dim"),
            (self.notification.message, style),
        )

    async def _auto_cleanup(self) -> None:
        """Auto cleanup after duration."""
        if self.notification.duration is not None:
            await asyncio.sleep(self.notification.duration)
            if self.app and isinstance(
                self.app.notification_center, NotificationCenter
            ):
                await self.app.notification_center.remove_notification(
                    self.notification
                )

    def on_unmount(self) -> None:
        """Handle widget unmount."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None


class NotificationCenter(PepperWidget, Container):
    """Notification center for managing multiple notifications.

    Attributes:
        max_notifications (int): Maximum number of visible notifications
        notifications (List[Notification]): Active notifications

    """

    # Class variables for Widget protocol
    DEFAULT_CLASSES: ClassVar[set[str]] = {"notification-center"}

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

    SEVERITY_TO_TYPE: dict[NotificationSeverity, NotificationType] = {
        "information": "info",
        "warning": "warning",
        "error": "error",
    }

    def __init__(
        self,
        *args: tuple[()],
        max_notifications: int = 5,
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize the notification center.

        Args:
            max_notifications: The maximum number of notifications to display.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        # Initialize base classes with required attributes
        super().__init__(*args, **kwargs)

        # Set required Widget attributes
        self.id = "notification-center"
        self.classes = self.DEFAULT_CLASSES
        self.styles = {}

        # Set notification center specific attributes
        self.max_notifications = max_notifications
        self.notifications: list[Notification] = []

    def compose(self) -> ComposeResult:
        """Compose the notification center layout."""
        for notification in reversed(self.notifications):
            yield NotificationWidget(notification=notification)

    async def notify(
        self,
        message: str,
        severity: NotificationSeverity = "information",
    ) -> None:
        """Show a notification.

        Args:
            message: The notification message.
            severity: The severity level of the notification.
        """
        # Map severity to notification type
        notification_type = self.SEVERITY_TO_TYPE[severity]

        # Create notification
        notification = Notification(message=message, type=notification_type)
        self.notifications.append(notification)

        # Remove old notifications if over limit
        while len(self.notifications) > self.max_notifications:
            oldest = self.notifications.pop(0)
            logger.debug("Removing old notification", message=oldest.message)

        # Refresh display
        await self.refresh_notifications()

        # Emit event
        await self.emit_event(
            "notification", {"message": message, "severity": severity}
        )

    async def remove_notification(self, notification: Notification) -> None:
        """Remove a notification.

        Args:
            notification: Notification to remove

        """
        if notification in self.notifications:
            self.notifications.remove(notification)
            logger.debug("Removing notification", message=notification.message)
            await self.refresh_notifications()

    async def refresh_notifications(self) -> None:
        """Refresh the notification display."""
        # Remove all existing notification widgets
        for widget in self.query("NotificationWidget"):
            widget.remove()

        # Mount new notification widgets
        for notification in reversed(self.notifications):
            await self.mount(NotificationWidget(notification=notification))

    def clear_all(self) -> None:
        """Clear all notifications."""
        logger.debug("Clearing all notifications", count=len(self.notifications))
        self.notifications.clear()
        self.remove_children()
