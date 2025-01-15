"""Keyboard handling for PepperPy Console."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

import structlog

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


logger = structlog.get_logger(__name__)


class EventEmitter(Protocol):
    """Event emitter protocol."""

    async def emit(self, event: str, data: dict[str, Any]) -> None:
        """Emit an event."""
        ...


class KeyBinding:
    """Key binding for keyboard shortcuts."""

    def __init__(
        self,
        key: str,
        action: Callable[..., Any],
        description: str = "",
    ) -> None:
        """Initialize key binding.

        Args:
            key: Key combination.
            action: Action to execute.
            description: Description of what the key binding does.

        """
        self.key = key
        self.action = action
        self.description = description


class KeyboardManager:
    """Keyboard manager for PepperPy Console."""

    def __init__(self) -> None:
        """Initialize keyboard manager."""
        self.bindings: dict[str, tuple[Callable[[], Awaitable[None]], str]] = {}
        # TODO(@pimentel): Add event manager
        #   https://github.com/felipepimentel/pepperpy/issues/1
        self.events: EventEmitter | None = None

    async def register_binding(
        self,
        key: str,
        action: Callable[[], Awaitable[None]],
        description: str = "",
    ) -> None:
        """Register a key binding.

        Args:
            key: Key to bind.
            action: Action to execute.
            description: Description of what the key binding does.

        """
        self.bindings[key] = (action, description)
        logger.debug("Registered key binding: %s -> %s", key, action)

    async def handle_key(self, key: str) -> None:
        """Handle a key press.

        Args:
            key: Pressed key.

        """
        if key in self.bindings:
            action, _ = self.bindings[key]
            try:
                await action()
            except (ValueError, TypeError) as e:
                logger.exception("Error handling key action %s", key)
                if self.events:
                    await self.events.emit(
                        "key_error",
                        {"action": key, "error": str(e)},
                    )
