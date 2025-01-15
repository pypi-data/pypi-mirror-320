"""Base screen for PepperPy Console."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from textual.screen import Screen
from textual.widgets import Static

from pepperpy.tui.widgets.base import PepperWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.binding import Binding


DEFAULT_TEXT = "Base PepperPy Screen"


class PepperScreen(PepperWidget, Screen[Any]):
    """Base screen for PepperPy TUI."""

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = []

    def compose(self) -> ComposeResult:
        """Compose the screen.

        Returns:
            The screen content.

        """
        yield Static(DEFAULT_TEXT)
