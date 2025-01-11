"""Tabs widget for content organization."""

from typing import Any, Dict, List, Optional

import structlog
from textual.containers import Container, Horizontal
from textual.widgets import Static

from .base import PepperWidget

logger = structlog.get_logger(__name__)


class TabButton(PepperWidget, Static):
    """Tab button widget.

    Attributes:
        label (str): Tab label
        tab_id (str): Tab identifier
    """

    DEFAULT_CSS = """
    TabButton {
        width: auto;
        min-width: 16;
        height: 3;
        color: $text-muted;
        background: $surface-darken-1;
        border-bottom: tall $surface-darken-1;
        content-align: center middle;
        padding: 0 2;
    }

    TabButton:hover {
        color: $text;
        background: $surface;
    }

    TabButton.-active {
        color: $text;
        background: $surface;
        border-bottom: tall $primary;
    }
    """

    def __init__(
        self,
        *args: Any,
        label: str,
        tab_id: str,
        is_active: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize tab button.

        Args:
            *args: Positional arguments
            label: Tab label
            tab_id: Tab identifier
            is_active: Whether tab is active
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.label = label
        self.tab_id = tab_id
        if is_active:
            self.add_class("-active")

    def render(self) -> str:
        """Render the button.

        Returns:
            str: Rendered content
        """
        return self.label


class TabContent(PepperWidget, Container):
    """Tab content widget.

    Attributes:
        tab_id (str): Tab identifier
        content (Container): Content container
    """

    DEFAULT_CSS = """
    TabContent {
        width: 100%;
        height: auto;
        display: none;
    }

    TabContent.-active {
        display: block;
    }
    """

    def __init__(
        self,
        *args: Any,
        tab_id: str,
        content: Container,
        is_active: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize tab content.

        Args:
            *args: Positional arguments
            tab_id: Tab identifier
            content: Content container
            is_active: Whether tab is active
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.tab_id = tab_id
        self.content = content
        if is_active:
            self.add_class("-active")

    def compose(self) -> None:
        """Compose the tab content."""
        yield self.content


class Tabs(PepperWidget, Container):
    """Tabs widget for organizing content.

    Attributes:
        tabs (Dict[str, TabContent]): Tab contents by ID
        active_tab (Optional[str]): Currently active tab ID
    """

    DEFAULT_CSS = """
    Tabs {
        layout: vertical;
        width: 100%;
        height: auto;
        background: $surface;
        border: tall $primary;
        padding: 0;
        margin: 1 0;
    }

    Tabs #tab-bar {
        width: 100%;
        height: 3;
        background: $surface-darken-1;
    }

    Tabs #tab-content {
        width: 100%;
        height: auto;
        padding: 1;
    }
    """

    def __init__(
        self,
        *args: Any,
        tabs: List[tuple[str, str, Container]],
        active_tab: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize tabs.

        Args:
            *args: Positional arguments
            tabs: List of (id, label, content) tuples
            active_tab: Initially active tab ID
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.tabs: Dict[str, TabContent] = {}
        self.active_tab = active_tab or (tabs[0][0] if tabs else None)
        self._setup_tabs(tabs)

    def _setup_tabs(self, tabs: List[tuple[str, str, Container]]) -> None:
        """Setup tab contents.

        Args:
            tabs: List of (id, label, content) tuples
        """
        for tab_id, label, content in tabs:
            is_active = tab_id == self.active_tab
            self.tabs[tab_id] = TabContent(
                tab_id=tab_id,
                content=content,
                is_active=is_active,
            )

    def compose(self) -> None:
        """Compose the tabs layout."""
        with Horizontal(id="tab-bar"):
            for tab_id, tab in self.tabs.items():
                yield TabButton(
                    label=tab.content.label
                    if hasattr(tab.content, "label")
                    else tab_id,
                    tab_id=tab_id,
                    is_active=tab_id == self.active_tab,
                )

        with Container(id="tab-content"):
            for tab in self.tabs.values():
                yield tab

    def switch_tab(self, tab_id: str) -> None:
        """Switch to a different tab.

        Args:
            tab_id: Tab to switch to
        """
        if tab_id not in self.tabs:
            return

        # Update active states
        for button in self.query(TabButton):
            if button.tab_id == tab_id:
                button.add_class("-active")
            else:
                button.remove_class("-active")

        for content in self.query(TabContent):
            if content.tab_id == tab_id:
                content.add_class("-active")
            else:
                content.remove_class("-active")

        self.active_tab = tab_id

    def on_tab_button_click(self, event: TabButton.Clicked) -> None:
        """Handle tab button clicks."""
        button = event.button
        self.switch_tab(button.tab_id)
