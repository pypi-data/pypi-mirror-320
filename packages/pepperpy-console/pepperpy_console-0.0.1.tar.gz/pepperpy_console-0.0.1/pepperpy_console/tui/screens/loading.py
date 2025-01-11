"""Loading screen for PepperPy TUI."""

from typing import AsyncGenerator

from textual.widget import Widget
from textual.widgets import Label, LoadingIndicator

from .base import PepperScreen


class LoadingScreen(PepperScreen):
    """Loading screen with customizable message."""

    def __init__(self, message: str = "Loading..."):
        """Initialize the loading screen.

        Args:
            message: Loading message to display
        """
        super().__init__()
        self.message = message

    async def compose(self) -> AsyncGenerator[Widget, None]:
        """Compose the loading screen layout.

        Yields:
            Loading screen widgets
        """
        yield Label(self.message)
        yield LoadingIndicator() 