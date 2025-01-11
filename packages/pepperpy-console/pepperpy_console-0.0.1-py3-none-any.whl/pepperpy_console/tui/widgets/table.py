"""Table widget for data display."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import structlog
from rich.table import Table as RichTable
from textual.widgets import Static

from .base import PepperWidget

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
    width: Optional[int] = None
    align: str = "left"
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

    def __init__(self, *args: Any, columns: List[Column], **kwargs: Any) -> None:
        """Initialize the table widget.

        Args:
            *args: Positional arguments
            columns: Table columns
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.columns = columns
        self.data: List[Dict[str, Any]] = []
        self.sort_key: Optional[str] = None
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

    async def load_data(self, data: List[Dict[str, Any]]) -> None:
        """Load table data.

        Args:
            data: List of data rows
        """
        self.data = data
        self.refresh()
        await self.events.emit("data_loaded", len(data))

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
        await self.events.emit("sorted", {"key": key, "reverse": self.sort_reverse})

    def _get_sorted_data(self) -> List[Dict[str, Any]]:
        """Get sorted data rows.

        Returns:
            List[Dict[str, Any]]: Sorted data
        """
        if not self.sort_key:
            return self.data

        return sorted(
            self.data,
            key=lambda x: x.get(self.sort_key, ""),
            reverse=self.sort_reverse,
        )
