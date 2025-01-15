"""Tooltip widget for contextual help."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import structlog
from rich.text import Text
from textual.containers import Container
from textual.widgets import Static

from .base import EventData, PepperWidget

if TYPE_CHECKING:
    from rich.console import ConsoleRenderable, RichCast
    from textual.app import ComposeResult


logger = structlog.get_logger(__name__)


class Tooltip(PepperWidget, Static):
    """Tooltip widget for displaying help text.

    Attributes:
        text (str): Tooltip text
        position (str): Tooltip position

    """

    DEFAULT_CSS = """
    Tooltip {
        layout: vertical;
        width: auto;
        min-width: 20;
        max-width: 60;
        height: auto;
        background: $surface-darken-1;
        color: $text;
        border: tall $primary;
        padding: 1;
        margin: 0;
        dock: auto;
        layer: tooltip;
        display: none;
    }

    Tooltip.-visible {
        display: block;
    }

    Tooltip.-top {
        dock: top;
    }

    Tooltip.-bottom {
        dock: bottom;
    }

    Tooltip.-left {
        dock: left;
    }

    Tooltip.-right {
        dock: right;
    }
    """

    def __init__(
        self,
        *args: tuple[()],
        text: str,
        position: Literal["top", "bottom", "left", "right"] = "bottom",
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize tooltip.

        Args:
            text: The text to display in the tooltip.
            position: The position of the tooltip relative to its container.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.text = text
        self.position = position
        self.add_class(f"-{position}")

    def render(self) -> ConsoleRenderable | RichCast:
        """Render the tooltip.

        Returns:
            The rendered tooltip.

        """
        return Text(self._text)

    def set_text(self, value: str) -> None:
        """Set the tooltip text.

        Args:
            value: The tooltip text.

        """
        self._text = value
        self.refresh()

    @property
    def text(self) -> str:
        """Get the tooltip text.

        Returns:
            The tooltip text.

        """
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        """Set the tooltip text.

        Args:
            value: The tooltip text.

        """
        self._text = value
        self.refresh()


class TooltipContainer(PepperWidget, Container):
    """Container with tooltip support.

    Attributes:
        tooltip (Optional[Tooltip]): Associated tooltip

    """

    def __init__(
        self,
        *args: tuple[()],
        tooltip_text: str | None = None,
        tooltip_position: Literal["top", "bottom", "left", "right"] = "bottom",
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize tooltip container.

        Args:
            tooltip_text: The text to display in the tooltip.
            tooltip_position: The position of the tooltip relative to its container.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self._tooltip_widget: Tooltip | None = None
        if tooltip_text:
            self._tooltip_widget = Tooltip(text=tooltip_text, position=tooltip_position)

    @property
    def tooltip_text(self) -> str | None:
        """Get the tooltip text.

        Returns:
            The tooltip text if set, None otherwise.

        """
        return self._tooltip_widget.text if self._tooltip_widget else None

    def compose(self) -> ComposeResult:
        """Compose the container layout."""
        if self._tooltip_widget:
            yield self._tooltip_widget

    def show_tooltip(self, x: int | None = None, y: int | None = None) -> None:
        """Show the tooltip.

        Args:
            x: Optional x position
            y: Optional y position

        """
        if self._tooltip_widget:
            self._tooltip_widget.add_class("-visible")
            if x is not None and y is not None:
                self._tooltip_widget.styles.margin = (y, x)

    def hide_tooltip(self) -> None:
        """Hide the tooltip."""
        if self._tooltip_widget:
            self._tooltip_widget.remove_class("-visible")

    def on_enter(self) -> None:
        """Handle mouse enter events."""
        self.show_tooltip()

    def on_leave(self) -> None:
        """Handle mouse leave events."""
        self.hide_tooltip()

    def on_click(self) -> None:
        """Handle click events."""
        if self._tooltip_widget and "-visible" in self._tooltip_widget.classes:
            self.hide_tooltip()
        else:
            self.show_tooltip()
