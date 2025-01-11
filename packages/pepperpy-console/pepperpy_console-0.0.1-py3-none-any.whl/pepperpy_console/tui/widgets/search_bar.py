"""SearchBar widget for filtering and searching content."""

from typing import Any, Callable, List, Optional

import structlog
from textual.containers import Horizontal, Container
from textual.message import Message
from textual.widgets import Input, Static

from .base import PepperWidget

logger = structlog.get_logger(__name__)


class SearchBar(PepperWidget, Horizontal):
    """Search bar widget with filtering capabilities.

    Attributes:
        placeholder (str): Input placeholder text
        on_search (Optional[Callable[[str], None]]): Search callback
        on_clear (Optional[Callable[[], None]]): Clear callback
        debounce_ms (int): Debounce delay in milliseconds
    """

    DEFAULT_CSS = """
    SearchBar {
        width: 100%;
        height: 3;
        background: $surface;
        border: tall $primary;
        margin: 1 0;
    }

    SearchBar #search-input {
        width: 1fr;
        height: 3;
        background: $surface;
        border: none;
        content-align: left middle;
        padding: 0 1;
    }

    SearchBar #clear-button {
        width: auto;
        height: 3;
        background: $surface;
        color: $text-muted;
        content-align: center middle;
        padding: 0 1;
    }

    SearchBar #clear-button:hover {
        color: $text;
        background: $surface-lighten-1;
    }
    """

    class SearchChanged(Message):
        """Search changed message.

        Attributes:
            value (str): Search value
        """

        def __init__(self, value: str) -> None:
            """Initialize search changed message.

            Args:
                value: Search value
            """
            super().__init__()
            self.value = value

    class SearchCleared(Message):
        """Search cleared message."""

    def __init__(
        self,
        *args: Any,
        placeholder: str = "Search...",
        on_search: Optional[Callable[[str], None]] = None,
        on_clear: Optional[Callable[[], None]] = None,
        debounce_ms: int = 300,
        **kwargs: Any,
    ) -> None:
        """Initialize search bar.

        Args:
            *args: Positional arguments
            placeholder: Input placeholder text
            on_search: Optional search callback
            on_clear: Optional clear callback
            debounce_ms: Debounce delay in milliseconds
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.placeholder = placeholder
        self.on_search = on_search
        self.on_clear = on_clear
        self.debounce_ms = debounce_ms

    def compose(self) -> None:
        """Compose the search bar layout."""
        yield Input(
            placeholder=self.placeholder,
            id="search-input",
        )
        yield Static("✕", id="clear-button")

    async def on_input_changed(self, message: Message) -> None:
        """Handle input changes."""
        if isinstance(message.sender, Input):
            value = message.sender.value.strip()
            await self.emit_no_wait(self.SearchChanged(value))
            if self.on_search:
                self.call_after(self.debounce_ms / 1000, self.on_search, value)

    async def on_click(self, message: Message) -> None:
        """Handle clear button clicks."""
        if message.sender.id == "clear-button":
            input_widget = self.query_one("#search-input", Input)
            input_widget.value = ""
            await self.emit_no_wait(self.SearchCleared())
            if self.on_clear:
                self.on_clear()


class FilterableList(PepperWidget, Static):
    """List widget with search filtering.

    Attributes:
        items (List[str]): List items
        filtered_items (List[str]): Filtered list items
    """

    DEFAULT_CSS = """
    FilterableList {
        width: 100%;
        height: auto;
        background: $surface;
        border: tall $primary;
        padding: 0;
        margin: 1 0;
    }

    FilterableList #items {
        width: 100%;
        height: auto;
        padding: 0;
    }

    FilterableList .item {
        width: 100%;
        height: 1;
        padding: 0 1;
    }

    FilterableList .item:hover {
        background: $surface-lighten-1;
    }

    FilterableList #no-results {
        width: 100%;
        height: 3;
        color: $text-muted;
        content-align: center middle;
        padding: 1;
    }
    """

    def __init__(
        self,
        *args: Any,
        items: List[str],
        **kwargs: Any,
    ) -> None:
        """Initialize filterable list.

        Args:
            *args: Positional arguments
            items: List items
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.items = items
        self.filtered_items = items.copy()

    def compose(self) -> None:
        """Compose the list layout."""
        with Container(id="items"):
            if self.filtered_items:
                for item in self.filtered_items:
                    yield Static(item, classes="item")
            else:
                yield Static("No results found", id="no-results")

    def filter_items(self, search_text: str) -> None:
        """Filter list items.

        Args:
            search_text: Search text
        """
        if not search_text:
            self.filtered_items = self.items.copy()
        else:
            search_text = search_text.lower()
            self.filtered_items = [
                item for item in self.items if search_text in item.lower()
            ]
        self.refresh()

    def on_search_bar_search_changed(self, event: SearchBar.SearchChanged) -> None:
        """Handle search changes."""
        self.filter_items(event.value)

    def on_search_bar_search_cleared(self, event: SearchBar.SearchCleared) -> None:
        """Handle search clear."""
        self.filter_items("")
