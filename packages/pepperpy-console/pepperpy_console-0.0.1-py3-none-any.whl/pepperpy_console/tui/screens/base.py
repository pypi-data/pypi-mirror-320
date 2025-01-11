"""Base screen for PepperPy TUI."""

from textual.screen import Screen
from textual.widgets import Static


class PepperScreen(Screen):
    """Base screen class for PepperPy TUI."""

    async def compose(self):
        """Compose the screen layout.

        Yields:
            Base screen widgets
        """
        yield Static("Base PepperPy Screen") 