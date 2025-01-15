"""Base widget for PepperPy TUI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.events import Mount
from textual.message import Message
from textual.widget import Widget

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


EventData = str | int | float | bool | None | dict[str, str | int | float | bool | None]


class PepperWidget(Widget):
    """Base widget class for PepperPy TUI.

    Attributes:
        events (list[tuple[str, dict[str, EventData]]]): Event history

    """

    class PepperEvent(Message):
        """Base event message for PepperPy widgets."""

        def __init__(self, event_type: str, data: Mapping[str, EventData]) -> None:
            """Initialize event message.

            Args:
                event_type: Type of event
                data: Event data

            """
            super().__init__()
            self.event_type = event_type
            self.event_data = data

    def __init__(self) -> None:
        """Initialize the widget."""
        super().__init__()
        self.events: list[tuple[str, dict[str, EventData]]] = []

    async def emit_event(self, event_type: str, data: dict[str, EventData]) -> None:
        """Emit an event.

        Args:
            event_type: Type of event
            data: Event data

        """
        self.events.append((event_type, data))
        await self.post_message(self.PepperEvent(event_type, data))

    def clear_events(self) -> None:
        """Clear all events."""
        self.events.clear()

    def get_events(
        self,
    ) -> Sequence[tuple[str, dict[str, EventData]]]:
        """Get all events.

        Returns:
            List of events as (type, data) tuples.

        """
        return self.events.copy()

    async def _on_mount(self, event: Mount) -> None:
        """Handle widget mount event."""
        await self.post_message(self.PepperEvent("mounted", {}))
