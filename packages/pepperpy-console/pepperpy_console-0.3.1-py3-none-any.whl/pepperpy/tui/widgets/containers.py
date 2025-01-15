"""Base container widgets for PepperPy Console."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Set

import structlog
from textual.containers import Container
from textual.reactive import reactive
from textual.widget import Widget

from .base import PepperWidget

if TYPE_CHECKING:
    pass

logger = structlog.get_logger(__name__)


class PepperContainer(PepperWidget, Container):
    """Base container widget for PepperPy Console.

    Attributes:
        visible (bool): Whether the container is visible
        enabled (bool): Whether the container is enabled

    """

    # Class variables for Widget protocol
    DEFAULT_CLASSES: ClassVar[Set[str]] = {"pepper-container"}

    # Reactive attributes
    visible = reactive(True)
    enabled = reactive(True)

    def __init__(
        self,
        *children: Widget,
        widget_id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize the container.

        Args:
            children: Child widgets.
            widget_id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            disabled: Whether the widget is disabled or not.
        """
        super().__init__()
        Container.__init__(self, *children, widget_id=widget_id, classes=classes)

        # Set container specific attributes
        self.enabled = not disabled
        self.id = widget_id if widget_id else None
        self.classes = set(classes.split()) if classes else set()

    def watch_visible(self, visible: bool) -> None:
        """Handle visibility changes.

        Args:
            visible: New visibility state.

        """
        if visible:
            self.remove_class("-hidden")
        else:
            self.add_class("-hidden")

    def watch_enabled(self, enabled: bool) -> None:
        """Handle enabled state changes.

        Args:
            enabled: New enabled state.

        """
        if enabled:
            self.remove_class("-disabled")
        else:
            self.add_class("-disabled")


class PepperGrid(PepperContainer):
    """Grid container widget for PepperPy Console.

    Attributes:
        rows (int): Number of rows
        columns (int): Number of columns
        gap (int): Gap between cells

    """

    # Class variables for Widget protocol
    DEFAULT_CLASSES: ClassVar[Set[str]] = {"pepper-grid"}

    # Reactive attributes
    rows = reactive(1)
    columns = reactive(1)
    gap = reactive(1)

    DEFAULT_CSS = """
    PepperGrid {
        layout: grid;
        height: auto;
        width: 100%;
    }

    PepperGrid.-hidden {
        display: none;
    }

    PepperGrid.-disabled {
        opacity: 0.5;
        pointer-events: none;
    }
    """

    def __init__(
        self,
        *children: Widget,
        widget_id: str | None = None,
        classes: str | None = None,
        rows: int = 1,
        columns: int = 1,
        gap: int = 1,
        disabled: bool = False,
    ) -> None:
        """Initialize the grid container.

        Args:
            children: Child widgets.
            widget_id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            rows: Number of rows.
            columns: Number of columns.
            gap: Gap between cells.
            disabled: Whether the widget is disabled or not.
        """
        super().__init__(
            *children,
            widget_id=widget_id,
            classes=classes,
            disabled=disabled,
        )
        self.rows = rows
        self.columns = columns
        self.gap = gap

    def _update_grid_styles(self) -> None:
        """Update grid styles."""
        styles = getattr(self, "styles", {})
        if isinstance(styles, dict):
            styles.update(
                {
                    "grid-rows": str(self.rows),
                    "grid-columns": str(self.columns),
                    "grid-gap": str(self.gap),
                }
            )

    def watch_rows(self, rows: int) -> None:
        """Handle rows changes.

        Args:
            rows: New number of rows.

        """
        self._update_grid_styles()

    def watch_columns(self, columns: int) -> None:
        """Handle columns changes.

        Args:
            columns: New number of columns.

        """
        self._update_grid_styles()

    def watch_gap(self, gap: int) -> None:
        """Handle gap changes.

        Args:
            gap: New gap size.

        """
        self._update_grid_styles()
