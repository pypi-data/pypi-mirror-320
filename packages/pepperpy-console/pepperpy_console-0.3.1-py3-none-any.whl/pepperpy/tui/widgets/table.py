"""Table widget for data display."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import structlog
from rich.table import Table as RichTable
from textual.widgets import Static

from .base import EventData, PepperWidget

logger = structlog.get_logger(__name__)


@dataclass
class Column:
    """Table column configuration.

    Attributes:
        key (str): Data key
        label (str): Column label
        width (Optional[int]): Column width
        align (str): Text alignment
        style (str): Cell style

    """

    key: str
    label: str
    width: int | None = None
    align: Literal["left", "center", "right"] = "left"
    style: str = ""


class PepperTable(PepperWidget, Static):
    """Enhanced table widget with sorting and filtering.

    Attributes:
        columns (List[Column]): Table columns
        data (List[Dict[str, Any]]): Table data
        sort_key (Optional[str]): Current sort column
        sort_reverse (bool): Sort direction

    """

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

    PepperTable {
        background: $selection;
        color: $text;
        border: solid $primary;
        padding: 0;
        width: 100%;
        height: auto;
    }

    PepperTable > Header {
        background: $primary;
        color: $text;
    }
    """

    def __init__(
        self,
        *args: tuple[()],
        columns: list[Column],
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize the table widget.

        Args:
            columns: The columns to display in the table.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.columns = columns
        self.rows: list[list[str]] = []
        self.sort_key: str | None = None
        self.sort_reverse = False

    def render(self) -> RichTable:
        """Render the table.

        Returns:
            RichTable: Rich table instance

        """
        table = RichTable(
            expand=True,
            show_header=True,
            show_edge=True,
            show_lines=True,
            border_style="#bd93f9",
        )

        # Add columns
        for col in self.columns:
            table.add_column(
                col.label,
                width=col.width,
                justify=col.align,
                style=col.style or "white",
            )

        # Add rows
        for row in self._get_sorted_data():
            table.add_row(*[str(row.get(col.key, "")) for col in self.columns])

        return table

    async def load_data(
        self,
        data: list[dict[str, str | int | float | bool | None]],
    ) -> None:
        """Load table data.

        Args:
            data: List of data rows

        """
        self.data = data
        self.refresh()
        await self.emit_event("data_loaded", {"count": len(data)})

    async def sort_by(self, key: str) -> None:
        """Sort table by column.

        Args:
            key: Column key

        """
        if self.sort_key == key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_key = key
            self.sort_reverse = False

        self.refresh()
        await self.emit_event("sorted", {"key": key, "reverse": self.sort_reverse})

    def _get_sorted_data(self) -> list[dict[str, str | int | float | bool | None]]:
        """Get sorted data rows.

        Returns:
            List[Dict[str, Any]]: Sorted data

        """
        if not self.sort_key:
            return self.data

        def sort_key(row: dict[str, str | int | float | bool | None]) -> str:
            return str(row.get(self.sort_key, "")) if self.sort_key else ""

        return sorted(
            self.data,
            key=sort_key,
            reverse=self.sort_reverse,
        )
