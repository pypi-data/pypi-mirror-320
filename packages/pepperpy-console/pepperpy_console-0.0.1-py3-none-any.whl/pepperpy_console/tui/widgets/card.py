"""Card widget for displaying content in a box."""

from typing import Any, Optional

import structlog
from textual.containers import Container
from textual.widgets import Label, Static

from .base import PepperWidget

logger = structlog.get_logger(__name__)


class Card(PepperWidget, Container):
    """Card widget with title and content.

    Attributes:
        title (str): Card title
        content (str): Card content
        variant (str): Card style variant
    """

    DEFAULT_CSS = """
    Card {
        layout: vertical;
        background: $surface;
        border: tall $primary;
        padding: 1;
        margin: 1;
        min-width: 30;
        max-width: 100;
        height: auto;
    }

    Card:hover {
        border: tall $accent;
    }

    Card.-primary {
        border: tall $primary;
    }

    Card.-success {
        border: tall $success;
    }

    Card.-warning {
        border: tall $warning;
    }

    Card.-error {
        border: tall $error;
    }

    Card.-info {
        border: tall $info;
    }

    Card #title {
        background: $surface-darken-1;
        color: $text;
        text-style: bold;
        width: 100%;
        height: 3;
        content-align: center middle;
        padding: 0 1;
    }

    Card #content {
        background: $surface;
        color: $text;
        width: 100%;
        min-height: 3;
        padding: 1;
    }
    """

    def __init__(
        self,
        *args: Any,
        title: str,
        content: str = "",
        variant: str = "primary",
        **kwargs: Any,
    ) -> None:
        """Initialize the card.

        Args:
            *args: Positional arguments
            title: Card title
            content: Card content
            variant: Card style variant
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.title = title
        self.content = content
        self.variant = variant

    def compose(self) -> None:
        """Compose the card layout."""
        self.add_class(f"-{self.variant}")
        yield Label(self.title, id="title")
        yield Static(self.content, id="content")

    def update_content(self, content: str) -> None:
        """Update card content.

        Args:
            content: New content
        """
        self.content = content
        content_widget = self.query_one("#content", Static)
        content_widget.update(content)

    def set_variant(self, variant: str) -> None:
        """Set card style variant.

        Args:
            variant: New variant
        """
        self.remove_class(f"-{self.variant}")
        self.variant = variant
        self.add_class(f"-{self.variant}")


class StatusCard(Card):
    """Card for displaying status information.

    Attributes:
        status (str): Current status
        details (Optional[str]): Additional details
    """

    def __init__(
        self,
        *args: Any,
        title: str,
        status: str,
        details: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the status card.

        Args:
            *args: Positional arguments
            title: Card title
            status: Current status
            details: Additional details
            **kwargs: Keyword arguments
        """
        content = self._format_content(status, details)
        variant = self._get_variant(status)
        super().__init__(*args, title=title, content=content, variant=variant, **kwargs)
        self.status = status
        self.details = details

    def _format_content(self, status: str, details: Optional[str] = None) -> str:
        """Format card content.

        Args:
            status: Current status
            details: Additional details

        Returns:
            str: Formatted content
        """
        content = f"Status: {status}"
        if details:
            content += f"\n{details}"
        return content

    def _get_variant(self, status: str) -> str:
        """Get card variant based on status.

        Args:
            status: Current status

        Returns:
            str: Card variant
        """
        status = status.lower()
        if "error" in status or "failed" in status:
            return "error"
        elif "warning" in status:
            return "warning"
        elif "success" in status or "completed" in status:
            return "success"
        elif "info" in status or "running" in status:
            return "info"
        else:
            return "primary"

    def update_status(self, status: str, details: Optional[str] = None) -> None:
        """Update card status.

        Args:
            status: New status
            details: New details
        """
        self.status = status
        self.details = details
        content = self._format_content(status, details)
        self.update_content(content)
        self.set_variant(self._get_variant(status))
