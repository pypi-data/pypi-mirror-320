"""Dropdown widget for selecting from a list of options."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container
from textual.widgets import Button, Input, Static

from .base import EventData, PepperWidget

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from textual.message import Message


class DropdownOption(PepperWidget, Static):
    """Dropdown option widget.

    Attributes:
        label (str): Option label
        value (Any): Option value
        is_selected (bool): Whether option is selected

    """

    DEFAULT_CSS = """
    DropdownOption {
        width: 100%;
        height: 1;
        color: $text;
        background: $surface;
        content-align: left middle;
        padding: 0 1;
    }

    DropdownOption:hover {
        background: $surface-lighten-1;
    }

    DropdownOption.-selected {
        background: $selection;
        color: $text;
    }
    """

    def __init__(
        self,
        *args: tuple[()],
        label: str,
        value: str | float | bool | None = None,
        is_selected: bool = False,
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize dropdown option.

        Args:
            label: The label to display for this option.
            value: The value associated with this option.
            is_selected: Whether this option is selected.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.label = label
        self.value = value if value is not None else label
        self.is_selected = is_selected

        if is_selected:
            self.add_class("-selected")

    def render(self) -> str:
        """Render the option.

        Returns:
            str: Rendered content

        """
        return self.label


class Dropdown(PepperWidget, Container):
    """Dropdown widget for selecting from a list of options.

    Attributes:
        options (List[DropdownOption]): Available options
        selected_option (Optional[DropdownOption]): Currently selected option
        placeholder (str): Placeholder text when no option is selected
        on_select (Optional[Callable]): Callback for when an option is selected
        is_open (bool): Whether dropdown is open

    """

    DEFAULT_CSS = """
    Dropdown {
        layout: vertical;
        width: 100%;
        height: auto;
        background: $surface;
        border: tall $primary;
        padding: 0;
        margin: 1 0;
    }

    #dropdown-container {
        layout: horizontal;
        height: 1;
        width: 100%;
        padding: 0;
        margin: 0;
    }

    #dropdown-input {
        width: 90%;
        height: 1;
        border: none;
        padding: 0 1;
    }

    #dropdown-toggle {
        width: 10%;
        height: 1;
        border: none;
        padding: 0;
        content-align: center middle;
    }

    #options {
        layout: vertical;
        width: 100%;
        height: auto;
        max-height: 10;
        overflow-y: scroll;
        border-top: tall $primary;
        padding: 0;
        margin: 0;
    }
    """

    def __init__(
        self,
        *args: tuple[()],
        options: list[str | tuple[str, str | int | float | bool | None]],
        placeholder: str = "Select an option...",
        on_select: Callable[[str | int | float | bool | None], None] | None = None,
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize dropdown.

        Args:
            options: List of options to display. Each option can be a string or a tuple
                of (label, value).
            placeholder: Text to display when no option is selected.
            on_select: Callback for when an option is selected.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.options: list[DropdownOption] = []
        self.selected_option: DropdownOption | None = None
        self.placeholder = placeholder
        self.on_select = on_select
        self.is_open = False

        for option in options:
            if isinstance(option, tuple):
                label, value = option
            else:
                label = value = option
            self.options.append(DropdownOption(label=label, value=value))

    def compose(self) -> Generator[Container | DropdownOption, None, None]:
        """Compose the dropdown layout."""
        yield Container(
            Input(
                placeholder=self.placeholder,
                id="dropdown-input",
                value=self.selected_option.label if self.selected_option else "",
            ),
            Button("▼", id="dropdown-toggle"),
            id="dropdown-container",
        )

        if self.is_open:
            with Container(id="options"):
                yield from self.options

    def toggle(self) -> None:
        """Toggle dropdown open/closed."""
        self.is_open = not self.is_open
        self.refresh()

    def select_option(self, option: DropdownOption) -> None:
        """Select a dropdown option.

        Args:
            option: Option to select

        """
        if self.selected_option:
            self.selected_option.remove_class("-selected")
        option.add_class("-selected")
        self.selected_option = option
        self.is_open = False
        self.refresh()

        if self.on_select:
            self.on_select(option.value)

    async def on_button_click(self, event: Message) -> None:
        """Handle button click events."""
        sender = getattr(event, "sender", None)
        if sender and getattr(sender, "id", None) == "dropdown-toggle":
            self.toggle()

    async def on_static_click(self, event: Message) -> None:
        """Handle option click events."""
        sender = getattr(event, "sender", None)
        if sender and isinstance(sender, DropdownOption):
            self.select_option(sender)
