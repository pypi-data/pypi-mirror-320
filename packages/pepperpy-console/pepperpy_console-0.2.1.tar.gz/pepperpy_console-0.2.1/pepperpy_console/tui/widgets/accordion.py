"""Accordion widget for collapsible content."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog
from textual.containers import Container
from textual.message import Message
from textual.widgets import Static

from .base import EventData, PepperWidget

if TYPE_CHECKING:
    from collections.abc import Generator


logger = structlog.get_logger(__name__)


class AccordionItem(PepperWidget, Container):
    """Accordion item widget.

    Attributes:
        title (str): Item title
        content (Container): Item content
        is_expanded (bool): Whether item is expanded

    """

    class Clicked(Message):
        """Message sent when an accordion item is clicked."""

        def __init__(self, sender: "AccordionItem") -> None:
            """Initialize clicked message.

            Args:
                sender: The accordion item that was clicked.

            """
            super().__init__()
            self.sender = sender

    DEFAULT_CSS = """
    AccordionItem {
        layout: vertical;
        width: 100%;
        height: auto;
        background: $surface;
        border: tall $primary;
        padding: 0;
        margin: 1 0;
    }

    AccordionItem > Header {
        width: 100%;
        height: 1;
        background: $primary;
        color: $text;
        content-align: left middle;
        padding: 0 1;
    }

    AccordionItem > Content {
        width: 100%;
        height: auto;
        background: $surface;
        color: $text;
        padding: 1;
        display: none;
    }

    AccordionItem.-expanded > Content {
        display: block;
    }
    """

    def __init__(
        self,
        *args: tuple[()],
        title: str,
        content: Container,
        is_expanded: bool = False,
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize accordion item.

        Args:
            title: The title to display in the header.
            content: The content to display when expanded.
            is_expanded: Whether this item starts expanded.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.title = title
        self.content = content
        self.is_expanded = is_expanded

        if is_expanded:
            self.add_class("-expanded")

    def toggle(self) -> None:
        """Toggle item expansion."""
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.add_class("-expanded")
        else:
            self.remove_class("-expanded")

    def compose(self) -> Generator[Static | Container, None, None]:
        """Compose the item layout."""
        yield Static(
            f"▼ {self.title}" if self.is_expanded else f"▶ {self.title}",
            widget_id="header",
        )
        with Container(widget_id="content"):
            yield self.content

    async def on_click(self) -> None:
        """Handle click events."""
        self.toggle()
        await self.post_message(self.Clicked(self))


class Accordion(PepperWidget, Container):
    """Accordion widget for collapsible content.

    Attributes:
        items (List[AccordionItem]): Accordion items
        allow_multiple (bool): Whether multiple items can be expanded

    """

    DEFAULT_CSS = """
    Accordion {
        layout: vertical;
        width: 100%;
        height: auto;
        background: $surface;
        border: tall $primary;
        padding: 0;
        margin: 1 0;
    }
    """

    def __init__(
        self,
        *args: tuple[()],
        items: list[tuple[str, Container]],
        allow_multiple: bool = True,
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize accordion.

        Args:
            items: List of (title, content) tuples.
            allow_multiple: Whether multiple items can be expanded.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.items = [
            AccordionItem(title=title, content=content) for title, content in items
        ]
        self.allow_multiple = allow_multiple

    def compose(self) -> Generator[AccordionItem, None, None]:
        """Compose the accordion layout."""
        yield from self.items

    async def on_accordion_item_clicked(self, event: AccordionItem.Clicked) -> None:
        """Handle item clicks."""
        clicked_item = event.sender
        if not self.allow_multiple:
            for item in self.items:
                if item != clicked_item and item.is_expanded:
                    item.toggle()

        await self.emit_event(
            "item_toggled",
            {
                "title": clicked_item.title,
                "expanded": clicked_item.is_expanded,
            },
        )
