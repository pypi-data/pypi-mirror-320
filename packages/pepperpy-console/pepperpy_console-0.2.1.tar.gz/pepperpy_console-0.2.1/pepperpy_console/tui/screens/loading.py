"""Loading screen for PepperPy TUI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Label, LoadingIndicator

from .base import PepperScreen

if TYPE_CHECKING:
    from textual.app import ComposeResult


class LoadingScreen(PepperScreen):
    """Loading screen with customizable message."""

    def __init__(self, message: str = "Loading...") -> None:
        """Initialize the loading screen.

        Args:
            message: The loading message to display.

        """
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        """Compose the loading screen layout.

        Returns:
            The compose result.

        """
        yield Label(self.message)
        yield LoadingIndicator()
