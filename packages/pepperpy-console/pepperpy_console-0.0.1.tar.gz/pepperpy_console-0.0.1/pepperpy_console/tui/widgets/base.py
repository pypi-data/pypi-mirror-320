"""Base widget for PepperPy TUI."""

from typing import Any, Dict, List

from textual.widget import Widget


class PepperWidget(Widget):
    """Base widget class for PepperPy TUI.

    Attributes:
        events (List[Dict[str, Any]]): Event history
    """

    def __init__(self) -> None:
        """Initialize the widget."""
        super().__init__()
        self.events: List[Dict[str, Any]] = []

    def emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit an event.

        Args:
            event_type: Type of event
            data: Event data
        """
        self.events.append({"type": event_type, "data": data})

    def clear_events(self) -> None:
        """Clear all events."""
        self.events.clear()

    def get_events(self) -> List[Dict[str, Any]]:
        """Get all events.

        Returns:
            List[Dict[str, Any]]: List of events
        """
        return self.events.copy()
