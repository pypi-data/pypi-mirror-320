"""Dropdown widget for selecting options."""

from typing import Any, Callable, List, Optional, Union

import structlog
from textual.containers import Container
from textual.message import Message
from textual.widgets import Static

from .base import PepperWidget

logger = structlog.get_logger(__name__)


class DropdownOption(PepperWidget, Static):
    """Dropdown option widget.

    Attributes:
        label (str): Option label
        value (Any): Option value
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
        *args: Any,
        label: str,
        value: Any = None,
        is_selected: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize dropdown option.

        Args:
            *args: Positional arguments
            label: Option label
            value: Option value
            is_selected: Whether option is selected
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.label = label
        self.value = value if value is not None else label
        if is_selected:
            self.add_class("-selected")

    def render(self) -> str:
        """Render the option.

        Returns:
            str: Rendered content
        """
        return self.label


class Dropdown(PepperWidget, Container):
    """Dropdown widget for selecting options.

    Attributes:
        options (List[DropdownOption]): Available options
        selected_option (Optional[DropdownOption]): Currently selected option
        is_open (bool): Whether dropdown is open
        placeholder (str): Placeholder text
        on_select (Optional[Callable[[Any], None]]): Selection callback
    """

    DEFAULT_CSS = """
    Dropdown {
        layout: vertical;
        width: 100%;
        height: auto;
        background: $surface;
        border: tall $primary;
        margin: 1 0;
    }

    Dropdown #header {
        width: 100%;
        height: 3;
        background: $surface;
        content-align: left middle;
        padding: 0 1;
    }

    Dropdown #header:hover {
        background: $surface-lighten-1;
    }

    Dropdown #options {
        width: 100%;
        max-height: 10;
        background: $surface;
        border-top: tall $primary;
        display: none;
        overflow-y: scroll;
    }

    Dropdown.-open #options {
        display: block;
    }

    Dropdown #placeholder {
        color: $text-muted;
    }
    """

    class OptionSelected(Message):
        """Option selected message.

        Attributes:
            option (DropdownOption): Selected option
        """

        def __init__(self, option: "DropdownOption") -> None:
            """Initialize option selected message.

            Args:
                option: Selected option
            """
            super().__init__()
            self.option = option

    def __init__(
        self,
        *args: Any,
        options: List[Union[str, tuple[str, Any]]],
        placeholder: str = "Select an option...",
        on_select: Optional[Callable[[Any], None]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize dropdown.

        Args:
            *args: Positional arguments
            options: List of options (strings or label-value tuples)
            placeholder: Placeholder text
            on_select: Optional selection callback
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.options: List[DropdownOption] = []
        self.selected_option: Optional[DropdownOption] = None
        self.is_open = False
        self.placeholder = placeholder
        self.on_select = on_select
        self._setup_options(options)

    def _setup_options(self, options: List[Union[str, tuple[str, Any]]]) -> None:
        """Setup dropdown options.

        Args:
            options: List of options
        """
        for option in options:
            if isinstance(option, tuple):
                label, value = option
            else:
                label = value = option
            self.options.append(DropdownOption(label=label, value=value))

    def compose(self) -> None:
        """Compose the dropdown layout."""
        with Static(id="header"):
            if self.selected_option:
                yield Static(self.selected_option.label)
            else:
                yield Static(self.placeholder, id="placeholder")

        with Container(id="options"):
            for option in self.options:
                yield option

    def toggle(self) -> None:
        """Toggle dropdown state."""
        self.is_open = not self.is_open
        if self.is_open:
            self.add_class("-open")
        else:
            self.remove_class("-open")

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
        self.remove_class("-open")
        self.refresh()

        self.emit_no_wait("option_selected", option)
        if self.on_select:
            self.on_select(option.value)

    def on_click(self, event: Static.Clicked) -> None:
        """Handle click events."""
        if event.target.id == "header":
            self.toggle()
        elif isinstance(event.target, DropdownOption):
            self.select_option(event.target)
