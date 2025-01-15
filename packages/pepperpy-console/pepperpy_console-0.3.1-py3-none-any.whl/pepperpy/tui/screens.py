"""Screen classes for PepperPy Console."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.screen import Screen
from textual.widgets import LoadingIndicator, Static

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


class PepperScreen(Screen):
    """Base screen class for PepperPy TUI."""

    BINDINGS: ClassVar[list[tuple[str, str, str]]] = []
    DEFAULT_TEXT = "Base PepperPy Screen"

    async def compose(self) -> AsyncGenerator[Static, None]:
        """Compose the screen layout.

        Returns:
            AsyncGenerator[Static, None]: Screen composition result.

        """
        yield Static(self.DEFAULT_TEXT)


class LoadingScreen(PepperScreen):
    """Loading screen with customizable message."""

    def __init__(self, message: str = "Loading...") -> None:
        """Initialize the loading screen.

        Args:
            message: The loading message to display.

        """
        super().__init__()
        self.message = message

    async def compose(self) -> AsyncGenerator[Static | LoadingIndicator, None]:
        """Compose the loading screen layout.

        Returns:
            AsyncGenerator[Static | LoadingIndicator, None]: Loading screen layout.

        """
        yield Static(self.message)
        yield LoadingIndicator()

    async def remove(self) -> None:
        """Remove the loading screen from the app.

        This method is called when the loading screen needs to be removed from the app.
        It performs any necessary cleanup before the screen is removed.
        """


class ErrorScreen(PepperScreen):
    """Error screen with an error message.

    Attributes:
        message (str): Error message

    """

    def __init__(self, message: str) -> None:
        """Initialize the error screen.

        Args:
            message: Error message

        """
        super().__init__()
        self.message = message

    async def compose(self) -> AsyncGenerator[Static, None]:
        """Compose the error screen layout.

        Yields:
            Static: Screen widgets

        """
        yield Static(f"Error: {self.message}")
