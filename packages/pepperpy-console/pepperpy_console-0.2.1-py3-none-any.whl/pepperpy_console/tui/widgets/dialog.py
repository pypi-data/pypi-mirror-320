"""Dialog widgets for user interaction."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import structlog
from rich.text import Text
from textual.containers import Container
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Static

from .base import EventData, PepperWidget

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from textual.app import ComposeResult
    from textual.await_complete import AwaitComplete


logger = structlog.get_logger(__name__)

T = TypeVar("T")


class DialogButton(PepperWidget, Button):
    """Dialog button widget."""

    class Clicked(Message):
        """Message sent when a dialog button is clicked."""

        def __init__(self, sender: "DialogButton") -> None:
            """Initialize clicked message.

            Args:
                sender: The button that was clicked.

            """
            super().__init__()
            self.sender = sender

    def __init__(
        self,
        *args: tuple[()],
        label: str,
        variant: str = "default",
        button_id: str | None = None,
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize dialog button.

        Args:
            label: Button label.
            variant: Button style variant.
            button_id: Button ID.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.label = label
        self.variant = variant
        if button_id:
            self.widget_id = button_id


class Dialog(PepperWidget, Screen[T]):
    """Base dialog widget."""

    def __init__(
        self,
        *args: tuple[()],
        title: str,
        content: Static,
        buttons: list[DialogButton],
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize the dialog.

        Args:
            title: The title to display in the header.
            content: The content to display in the body.
            buttons: The buttons to display in the footer.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.title = title
        self.content = content
        self.buttons = buttons

    def compose(self) -> ComposeResult:
        """Compose the dialog layout."""
        header_text = Text(str(self.title))
        yield Static(header_text, widget_id="header")
        yield self.content
        with Container(widget_id="footer"):
            yield from self.buttons

    def dismiss(self, result: T | None = None) -> AwaitComplete:
        """Dismiss the dialog.

        Args:
            result: Optional result to return.

        Returns:
            The await complete result.

        """
        self._result = result
        if self.app is not None:
            return self.app.pop_screen()
        return AwaitComplete()


class ConfirmDialog(Dialog[bool]):
    """Confirmation dialog with confirm/cancel buttons."""

    def __init__(
        self,
        *args: tuple[()],
        title: str,
        content: Static,
        on_confirm: Callable[[], Coroutine[Any, Any, None]] | None = None,
        on_cancel: Callable[[], Coroutine[Any, Any, None]] | None = None,
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize the confirmation dialog.

        Args:
            title: The title to display in the header.
            content: The content to display in the body.
            on_confirm: Optional async callback for confirm button.
            on_cancel: Optional async callback for cancel button.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        buttons = [
            DialogButton(label="Confirm", variant="primary", button_id="confirm"),
            DialogButton(label="Cancel", variant="error", button_id="cancel"),
        ]
        super().__init__(*args, title=title, content=content, buttons=buttons, **kwargs)
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

    async def on_dialog_button_clicked(self, event: DialogButton.Clicked) -> None:
        """Handle button clicks."""
        button = event.sender
        if button.widget_id == "confirm" and self.on_confirm is not None:
            await self.on_confirm()
            await self.dismiss(result=True)
        elif button.widget_id == "cancel" and self.on_cancel is not None:
            await self.on_cancel()
            await self.dismiss(result=False)


class AlertDialog(Dialog[None]):
    """Alert dialog with close button."""

    def __init__(
        self,
        *args: tuple[()],
        title: str,
        content: Static,
        on_close: Callable[[], Coroutine[Any, Any, None]] | None = None,
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize the alert dialog.

        Args:
            title: The title to display in the header.
            content: The content to display in the body.
            on_close: Optional async callback for close button.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        buttons = [DialogButton(label="Close", variant="primary", button_id="close")]
        super().__init__(*args, title=title, content=content, buttons=buttons, **kwargs)
        self.on_close = on_close

    async def on_dialog_button_clicked(self, _event: DialogButton.Clicked) -> None:
        """Handle button clicks."""
        if self.on_close is not None:
            await self.on_close()
        await self.dismiss()

    async def wait_for_dismiss(self) -> None:
        """Wait for the dialog to be dismissed."""
        # This is a placeholder - in a real implementation we would
        # use an event or other mechanism to wait for dismissal
