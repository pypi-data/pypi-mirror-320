"""Event system for TUI applications."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

import structlog

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


logger = structlog.get_logger(__name__)


class EventData(Protocol):
    """Protocol for event data."""

    def __str__(self) -> str:
        """Convert the event data to a string.

        Returns:
            The string representation of the event data.

        """
        ...


class EventManager:
    """Event manager for handling application events.

    Attributes:
        listeners (Dict[str, List[Callable[..., Awaitable[None]]]]): Event listeners

    """

    def __init__(self) -> None:
        """Initialize the event manager."""
        self.listeners: dict[str, list[Callable[..., Awaitable[None]]]] = {}

    def register(self, event: str, handler: Callable[..., Awaitable[None]]) -> None:
        """Register an event handler.

        Args:
            event: Event name.
            handler: Event handler function.

        """
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(handler)
        logger.debug("Registered event handler", event=event)

    def off(
        self,
        event: str,
        handler: Callable[..., Awaitable[None]] | None = None,
    ) -> None:
        """Remove an event handler.

        Args:
            event: Event name.
            handler: Event handler to remove.

        """
        if handler is None:
            self.listeners[event] = []
        else:
            self.listeners[event].remove(handler)

    async def emit(self, event: str, data: EventData | None = None) -> None:
        """Emit an event.

        Args:
            event: Event name.
            data: Event data.

        """
        if event in self.listeners:
            for handler in self.listeners[event]:
                try:
                    if data is not None:
                        await handler(data)
                    else:
                        await handler()
                except Exception:
                    logger.exception("Error handling event", event=event)


event_manager = EventManager()
