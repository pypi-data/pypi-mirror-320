"""Tab widget implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container
from textual.message import Message
from textual.widgets import Static

from pepperpy_console.tui.widgets.base import PepperWidget

if TYPE_CHECKING:
    from collections.abc import Generator


class TabButton(PepperWidget, Static):
    """Tab button widget."""

    DEFAULT_CSS = """
    TabButton {
        padding: 1;
        margin: 0;
        border: none;
        text-align: center;
        min-width: 10;
    }

    TabButton:hover {
        background: $accent;
    }

    TabButton.-active {
        background: $accent;
    }
    """

    def __init__(self, label: str, tab_id: str) -> None:
        """Initialize the tab button.

        Args:
            label: Label to display on the button.
            tab_id: ID of the tab this button controls.

        """
        super().__init__()
        self.label = label
        self.tab_id = tab_id

    def compose(self) -> Generator[Static, None, None]:
        """Compose the tab button.

        Returns:
            Generator[Static, None, None]: The composed tab button.

        """
        yield Static(self.label)


class TabContent(PepperWidget, Container):
    """Tab content widget."""

    DEFAULT_CSS = """
    TabContent {
        display: none;
        padding: 1;
        border: none;
        height: auto;
    }

    TabContent.-active {
        display: block;
    }
    """

    def __init__(self, tab_id: str) -> None:
        """Initialize the tab content.

        Args:
            tab_id: ID of the tab this content belongs to.

        """
        super().__init__()
        self.tab_id = tab_id


class TabChanged(Message, bubble=True):
    """Message sent when a tab is changed."""

    def __init__(self, tab_id: str) -> None:
        """Initialize the tab changed message.

        Args:
            tab_id: ID of the tab that was changed to.

        """
        super().__init__()
        self.tab_id = tab_id


class Tabs(PepperWidget, Container):
    """Tab widget."""

    DEFAULT_CSS = """
    Tabs {
        layout: grid;
        grid-size: 1;
        grid-rows: auto 1fr;
        height: auto;
    }

    Tabs > .tabs {
        layout: horizontal;
        height: auto;
        border-bottom: solid $accent;
    }

    Tabs > .content {
        height: auto;
    }
    """

    def __init__(self) -> None:
        """Initialize the tabs widget."""
        super().__init__()
        self.buttons: list[TabButton] = []
        self.contents: list[TabContent] = []
        self._active_tab: str | None = None

    def compose(
        self,
    ) -> Generator[Container | TabButton | TabContent, None, None]:
        """Compose the tabs widget.

        Returns:
            Generator[Container | TabButton | TabContent, None, None]:
                The composed tabs widget.

        """
        with Container(classes="tabs"):
            yield from self.buttons
        with Container(classes="content"):
            yield from self.contents

    def add_tab(self, label: str, tab_id: str, content: TabContent) -> None:
        """Add a tab to the widget.

        Args:
            label: Label to display on the tab button.
            tab_id: ID of the tab.
            content: Content to display in the tab.

        """
        button = TabButton(label, tab_id)
        button.id = f"tab-{tab_id}"
        content.id = f"content-{tab_id}"
        self.buttons.append(button)
        self.contents.append(content)

        if not self._active_tab:
            self._active_tab = tab_id
            button.add_class("-active")
            content.add_class("-active")

    def on_click(self, event: Message) -> None:
        """Handle click events.

        Args:
            event: The click event.

        """
        if isinstance(event._sender, TabButton):
            self._set_active_tab(event._sender.tab_id)

    def _set_active_tab(self, tab_id: str) -> None:
        """Set the active tab.

        Args:
            tab_id: ID of the tab to set as active.

        """
        if tab_id == self._active_tab:
            return

        for button in self.buttons:
            if button.tab_id == tab_id:
                button.add_class("-active")
            else:
                button.remove_class("-active")

        for content in self.contents:
            if content.tab_id == tab_id:
                content.add_class("-active")
            else:
                content.remove_class("-active")

        self._active_tab = tab_id
        self.post_message(TabChanged(tab_id))
