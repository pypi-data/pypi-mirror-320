"""Dialog system for user interactions."""

from dataclasses import dataclass
from typing import Any, Callable, List, Optional

import structlog
from textual.containers import Container
from textual.widgets import Button, Label

from .base import PepperWidget

logger = structlog.get_logger(__name__)


@dataclass
class DialogButton:
    """Dialog button configuration.

    Attributes:
        label (str): Button label
        action (Optional[Callable]): Button action
        variant (str): Button style variant
    """

    label: str
    action: Optional[Callable] = None
    variant: str = "default"


class Dialog(PepperWidget, Container):
    """Base dialog widget.

    Attributes:
        title (str): Dialog title
        content (str): Dialog content
        buttons (List[DialogButton]): Dialog buttons
    """

    DEFAULT_CSS = """
    Dialog {
        background: $background;
        border: solid $primary;
        padding: 1;
        width: 60%;
        height: auto;
        align: center middle;
    }

    Dialog #title {
        background: $primary;
        color: $text;
        text-align: center;
        padding: 1;
        width: 100%;
    }

    Dialog #content {
        margin: 1;
        width: 100%;
    }

    Dialog Button {
        margin: 1 1 0 0;
    }
    """

    def __init__(
        self,
        *args: Any,
        title: str,
        content: str,
        buttons: List[DialogButton],
        **kwargs: Any,
    ) -> None:
        """Initialize the dialog.

        Args:
            *args: Positional arguments
            title: Dialog title
            content: Dialog content
            buttons: Dialog buttons
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.title = title
        self.content = content
        self.buttons = buttons

    def compose(self) -> None:
        """Compose the dialog layout."""
        yield Label(self.title, id="title")
        yield Label(self.content, id="content")

        for button in self.buttons:
            yield Button(
                button.label,
                variant=button.variant,
                id=f"button_{button.label.lower()}",
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        if button_id and button_id.startswith("button_"):
            label = button_id[7:].title()
            button = next((b for b in self.buttons if b.label == label), None)
            if button and button.action:
                button.action()


class ConfirmDialog(Dialog):
    """Confirmation dialog with Yes/No buttons."""

    def __init__(
        self,
        *args: Any,
        title: str,
        content: str,
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the confirmation dialog.

        Args:
            *args: Positional arguments
            title: Dialog title
            content: Dialog content
            on_confirm: Confirmation callback
            on_cancel: Cancellation callback
            **kwargs: Keyword arguments
        """
        buttons = [
            DialogButton("Yes", on_confirm, "primary"),
            DialogButton("No", on_cancel, "error"),
        ]
        super().__init__(*args, title=title, content=content, buttons=buttons, **kwargs)


class AlertDialog(Dialog):
    """Alert dialog with OK button."""

    def __init__(
        self,
        *args: Any,
        title: str,
        content: str,
        on_close: Optional[Callable] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the alert dialog.

        Args:
            *args: Positional arguments
            title: Dialog title
            content: Dialog content
            on_close: Close callback
            **kwargs: Keyword arguments
        """
        buttons = [DialogButton("OK", on_close, "primary")]
        super().__init__(*args, title=title, content=content, buttons=buttons, **kwargs)
