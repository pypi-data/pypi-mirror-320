"""Accordion widget for expandable content."""

from typing import Any, List

import structlog
from textual.containers import Container
from textual.widgets import Static

from .base import PepperWidget

logger = structlog.get_logger(__name__)


class AccordionItem(PepperWidget, Container):
    """Accordion item widget.

    Attributes:
        title (str): Item title
        content (Container): Item content
        is_expanded (bool): Whether item is expanded
    """

    DEFAULT_CSS = """
    AccordionItem {
        layout: vertical;
        width: 100%;
        height: auto;
        background: $surface;
        border-bottom: tall $surface-darken-1;
    }

    AccordionItem:hover {
        background: $surface-lighten-1;
    }

    AccordionItem #header {
        width: 100%;
        height: 3;
        background: $surface;
        content-align: left middle;
        padding: 0 1;
    }

    AccordionItem #header:hover {
        background: $surface-lighten-1;
    }

    AccordionItem #content {
        width: 100%;
        height: auto;
        display: none;
        padding: 1;
        background: $surface-darken-1;
    }

    AccordionItem.-expanded #header {
        background: $surface-lighten-1;
        border-left: thick $primary;
    }

    AccordionItem.-expanded #content {
        display: block;
    }
    """

    def __init__(
        self,
        *args: Any,
        title: str,
        content: Container,
        is_expanded: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize accordion item.

        Args:
            *args: Positional arguments
            title: Item title
            content: Item content
            is_expanded: Whether item is expanded
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.title = title
        self.content = content
        self.is_expanded = is_expanded
        if is_expanded:
            self.add_class("-expanded")

    def compose(self) -> None:
        """Compose the item layout."""
        yield Static(
            f"▼ {self.title}" if self.is_expanded else f"▶ {self.title}", id="header"
        )
        with Container(id="content"):
            yield self.content

    def toggle(self) -> None:
        """Toggle item expansion."""
        self.is_expanded = not self.is_expanded
        header = self.query_one("#header", Static)
        header.update(f"▼ {self.title}" if self.is_expanded else f"▶ {self.title}")
        if self.is_expanded:
            self.add_class("-expanded")
        else:
            self.remove_class("-expanded")

    def on_click(self) -> None:
        """Handle click events."""
        self.toggle()
        self.emit_no_wait("accordion_item_clicked", self)


class Accordion(PepperWidget, Container):
    """Accordion widget for expandable content.

    Attributes:
        items (List[AccordionItem]): Accordion items
        allow_multiple (bool): Allow multiple items expanded
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
        *args: Any,
        items: List[tuple[str, Container]],
        allow_multiple: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize accordion.

        Args:
            *args: Positional arguments
            items: List of (title, content) tuples
            allow_multiple: Allow multiple items expanded
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.allow_multiple = allow_multiple
        self.items: List[AccordionItem] = []
        self._setup_items(items)

    def _setup_items(self, items: List[tuple[str, Container]]) -> None:
        """Setup accordion items.

        Args:
            items: List of (title, content) tuples
        """
        for title, content in items:
            item = AccordionItem(title=title, content=content)
            self.items.append(item)

    def compose(self) -> None:
        """Compose the accordion layout."""
        for item in self.items:
            yield item

    def on_accordion_item_clicked(self, event: Any) -> None:
        """Handle item clicks."""
        clicked_item = event.sender
        if not self.allow_multiple:
            # Collapse other items
            for item in self.items:
                if item != clicked_item and item.is_expanded:
                    item.toggle()
