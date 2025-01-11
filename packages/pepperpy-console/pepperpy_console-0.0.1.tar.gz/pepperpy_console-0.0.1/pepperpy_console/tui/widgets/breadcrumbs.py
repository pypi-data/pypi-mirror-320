"""Breadcrumbs widget for navigation."""

from typing import Any, Callable, List, Optional

import structlog
from textual.containers import Horizontal
from textual.widgets import Static

from .base import PepperWidget

logger = structlog.get_logger(__name__)


class BreadcrumbItem(PepperWidget, Static):
    """Individual breadcrumb item.

    Attributes:
        label (str): Item label
        action (Optional[Callable]): Click action
    """

    DEFAULT_CSS = """
    BreadcrumbItem {
        color: $text-muted;
        text-style: none;
        padding: 0 1;
    }

    BreadcrumbItem:hover {
        color: $accent;
        text-style: underline;
    }

    BreadcrumbItem.-current {
        color: $text;
        text-style: bold;
    }

    BreadcrumbItem.-separator {
        color: $text-disabled;
        text-style: none;
        padding: 0;
    }
    """

    def __init__(
        self,
        *args: Any,
        label: str,
        action: Optional[Callable] = None,
        is_current: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize breadcrumb item.

        Args:
            *args: Positional arguments
            label: Item label
            action: Optional click action
            is_current: Whether this is the current item
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.label = label
        self.action = action
        if is_current:
            self.add_class("-current")

    def render(self) -> str:
        """Render the item.

        Returns:
            str: Rendered content
        """
        return self.label

    async def on_click(self) -> None:
        """Handle click events."""
        if self.action:
            await self.action()
            await self.events.emit("breadcrumb_clicked", self.label)


class Breadcrumbs(PepperWidget, Horizontal):
    """Breadcrumbs navigation widget.

    Attributes:
        items (List[BreadcrumbItem]): Navigation items
        separator (str): Item separator
    """

    DEFAULT_CSS = """
    Breadcrumbs {
        width: auto;
        height: 3;
        background: $surface;
        border: tall $primary;
        padding: 0 1;
        margin: 1 0;
        content-align: left middle;
    }
    """

    def __init__(
        self,
        *args: Any,
        items: List[tuple[str, Optional[Callable]]],
        separator: str = "›",
        **kwargs: Any,
    ) -> None:
        """Initialize breadcrumbs.

        Args:
            *args: Positional arguments
            items: List of (label, action) tuples
            separator: Item separator
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.items = []
        self.separator = separator
        self._setup_items(items)

    def _setup_items(self, items: List[tuple[str, Optional[Callable]]]) -> None:
        """Setup breadcrumb items.

        Args:
            items: List of (label, action) tuples
        """
        for i, (label, action) in enumerate(items):
            is_current = i == len(items) - 1
            item = BreadcrumbItem(label=label, action=action, is_current=is_current)
            self.items.append(item)

    def compose(self) -> None:
        """Compose the breadcrumbs layout."""
        for i, item in enumerate(self.items):
            yield item
            if i < len(self.items) - 1:
                yield BreadcrumbItem(
                    label=self.separator,
                    classes="-separator",
                )

    def update_path(self, items: List[tuple[str, Optional[Callable]]]) -> None:
        """Update navigation path.

        Args:
            items: New list of (label, action) tuples
        """
        self.items.clear()
        self._setup_items(items)
        self.refresh()
