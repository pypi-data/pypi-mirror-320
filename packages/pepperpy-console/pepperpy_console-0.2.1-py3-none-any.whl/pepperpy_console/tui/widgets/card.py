"""Card widgets for displaying content."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import structlog
from textual.containers import Container
from textual.widgets import Static

from .base import EventData, PepperWidget

if TYPE_CHECKING:
    from collections.abc import Generator


logger = structlog.get_logger(__name__)


class Card(PepperWidget, Container):
    """Card widget for displaying content.

    Attributes:
        title (str): Card title
        content (str): Card content
        variant (str): Card style variant

    """

    DEFAULT_CSS = """
    Card {
        layout: vertical;
        width: 100%;
        height: auto;
        background: $surface;
        border: tall $primary;
        padding: 0;
        margin: 1 0;
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

    Card > Header {
        width: 100%;
        height: 1;
        background: $primary;
        color: $text;
        content-align: left middle;
        padding: 0 1;
    }

    Card.-success > Header {
        background: $success;
    }

    Card.-warning > Header {
        background: $warning;
    }

    Card.-error > Header {
        background: $error;
    }

    Card > Content {
        width: 100%;
        height: auto;
        background: $surface;
        color: $text;
        padding: 1;
    }
    """

    def __init__(
        self,
        *args: tuple[()],
        title: str,
        content: str = "",
        variant: Literal["primary", "success", "warning", "error"] = "primary",
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize the card.

        Args:
            title: The title to display in the header.
            content: The content to display in the body.
            variant: The style variant to use.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.title = title
        self.content = content
        self.variant = variant
        self.add_class(f"-{variant}")

    def compose(self) -> Generator[Static, None, None]:
        """Compose the card layout."""
        yield Static(self.title, id="header")
        yield Static(self.content, id="content")


class StatusCard(Card):
    """Card for displaying status information.

    Attributes:
        title (str): Card title
        status (str): Status message
        details (Optional[str]): Additional details

    """

    def __init__(
        self,
        *args: tuple[()],
        title: str,
        status: str,
        details: str | None = None,
        variant: Literal["primary", "success", "warning", "error"] = "primary",
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize the status card.

        Args:
            title: The title to display in the header.
            status: The status message to display.
            details: Optional additional details.
            variant: The style variant to use.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        content = f"{status}\n{details}" if details else status
        super().__init__(*args, title=title, content=content, variant=variant, **kwargs)
