"""Breadcrumbs widget for PepperPy Console."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from textual.containers import Container
from textual.widgets import Static

from .base import EventData, PepperWidget

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class BreadcrumbItem:
    """Breadcrumb item configuration.

    Attributes:
        label: Display label
        action: Action to execute
        is_current: Whether this is the current item

    """

    label: str
    action: Callable[[], None]
    is_current: bool = False


class Breadcrumbs(PepperWidget, Container):
    """Breadcrumbs navigation widget.

    Attributes:
        items: List of breadcrumb items

    """

    def __init__(self, *args: tuple[()], **kwargs: dict[str, EventData]) -> None:
        """Initialize the breadcrumbs widget.

        Args:
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        """
        super().__init__(*args, **kwargs)
        self.items: list[BreadcrumbItem] = []

    def clear(self) -> None:
        """Clear all breadcrumb items."""
        self.items.clear()
        self.refresh()

    def add_item(
        self,
        label: str,
        action: Callable[[], None],
        *,
        is_current: bool = False,
    ) -> None:
        """Add a breadcrumb item.

        Args:
            label: Display label
            action: Action to execute
            is_current: Whether this is the current item

        """
        item = BreadcrumbItem(label=label, action=action, is_current=is_current)
        self.items.append(item)
        self.refresh()

    def compose(self) -> list[Static]:
        """Compose the breadcrumbs widget.

        Returns:
            List of breadcrumb items.

        """
        result: list[Static] = []
        for i, item in enumerate(self.items):
            if i > 0:
                result.append(Static(" > "))
            result.append(Static(item.label))
        return result
