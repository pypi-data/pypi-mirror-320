"""Event system for TUI applications."""

from typing import Any, Dict, List, Optional, Callable, Awaitable

import structlog

logger = structlog.get_logger(__name__)


class EventManager:
    """Event manager for handling application events.

    Attributes:
        listeners (Dict[str, List[Callable[..., Awaitable[None]]]]): Event listeners
    """

    def __init__(self) -> None:
        """Initialize the event manager."""
        self.listeners: Dict[str, List[Callable[..., Awaitable[None]]]] = {}

    def on(self, event: str, handler: Callable[..., Awaitable[None]]) -> None:
        """Register an event handler.

        Args:
            event: Event name
            handler: Event handler
        """
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(handler)
        logger.debug(f"Registered event handler for {event}")

    def off(self, event: str, handler: Optional[Callable[..., Awaitable[None]]] = None) -> None:
        """Remove an event handler.

        Args:
            event: Event name
            handler: Optional event handler to remove
        """
        if event in self.listeners:
            if handler:
                self.listeners[event].remove(handler)
            else:
                self.listeners[event] = []
            logger.debug(f"Removed event handler for {event}")

    async def emit(self, event: str, data: Any = None) -> None:
        """Emit an event.

        Args:
            event: Event name
            data: Optional event data
        """
        if event in self.listeners:
            for handler in self.listeners[event]:
                try:
                    if data is not None:
                        await handler(data)
                    else:
                        await handler()
                except Exception as e:
                    logger.error(f"Error handling event {event}: {e}")


event_manager = EventManager() 