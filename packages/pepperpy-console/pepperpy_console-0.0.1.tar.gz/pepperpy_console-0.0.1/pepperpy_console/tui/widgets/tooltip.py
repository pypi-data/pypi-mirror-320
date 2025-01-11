"""Tooltip widget for contextual help."""

from typing import Any, Optional

import structlog
from textual.containers import Container
from textual.widgets import Static

from .base import PepperWidget

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
        *args: Any,
        text: str,
        position: str = "bottom",
        **kwargs: Any,
    ) -> None:
        """Initialize tooltip.

        Args:
            *args: Positional arguments
            text: Tooltip text
            position: Tooltip position (top, bottom, left, right)
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.text = text
        self.position = position
        self.add_class(f"-{position}")

    def render(self) -> str:
        """Render the tooltip.

        Returns:
            str: Rendered content
        """
        return self.text


class TooltipContainer(PepperWidget, Container):
    """Container with tooltip support.

    Attributes:
        tooltip (Optional[Tooltip]): Associated tooltip
    """

    def __init__(
        self,
        *args: Any,
        tooltip_text: Optional[str] = None,
        tooltip_position: str = "bottom",
        **kwargs: Any,
    ) -> None:
        """Initialize tooltip container.

        Args:
            *args: Positional arguments
            tooltip_text: Optional tooltip text
            tooltip_position: Tooltip position
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.tooltip: Optional[Tooltip] = None
        if tooltip_text:
            self.tooltip = Tooltip(text=tooltip_text, position=tooltip_position)

    def compose(self) -> None:
        """Compose the container layout."""
        if self.tooltip:
            yield self.tooltip

    def show_tooltip(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Show the tooltip.

        Args:
            x: Optional x position
            y: Optional y position
        """
        if self.tooltip:
            self.tooltip.add_class("-visible")
            if x is not None and y is not None:
                self.tooltip.styles.margin = (y, x)

    def hide_tooltip(self) -> None:
        """Hide the tooltip."""
        if self.tooltip:
            self.tooltip.remove_class("-visible")

    def on_enter(self) -> None:
        """Handle mouse enter events."""
        self.show_tooltip()

    def on_leave(self) -> None:
        """Handle mouse leave events."""
        self.hide_tooltip()

    def on_click(self) -> None:
        """Handle click events."""
        if self.tooltip and "-visible" in self.tooltip.classes:
            self.hide_tooltip()
        else:
            self.show_tooltip()
