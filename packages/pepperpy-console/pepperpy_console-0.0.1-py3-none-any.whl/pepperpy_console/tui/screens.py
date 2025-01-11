"""Screen classes for PepperPy Console."""

from typing import AsyncGenerator

from textual.screen import Screen
from textual.widgets import LoadingIndicator, Static


class PepperScreen(Screen):
    """Base screen class for PepperPy Console.

    All screens should inherit from this class.
    """

    BINDINGS = []

    async def compose(self) -> AsyncGenerator[Static, None]:
        """Compose the screen layout.

        This method should be overridden by subclasses.

        Yields:
            Static: Screen widgets
        """
        yield Static("Base PepperPy Screen")


class LoadingScreen(PepperScreen):
    """Loading screen widget.

    Attributes:
        message (str): Loading message to display
    """

    def __init__(self, message: str = "Loading...") -> None:
        """Initialize the loading screen.

        Args:
            message: Loading message to display
        """
        super().__init__()
        self.message = message

    async def compose(self) -> AsyncGenerator[Static | LoadingIndicator, None]:
        """Compose the loading screen.

        Returns:
            AsyncGenerator[Static | LoadingIndicator, None]: Loading screen composition result
        """
        yield Static(self.message)
        yield LoadingIndicator()

    async def remove(self) -> None:
        """Remove the loading screen from the app.
        
        This method is called when the loading screen needs to be removed from the app.
        It performs any necessary cleanup before the screen is removed.
        """
        pass


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
