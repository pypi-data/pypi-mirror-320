"""Keyboard shortcut system for TUI applications."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import structlog

from .events import event_manager

logger = structlog.get_logger(__name__)


@dataclass
class KeyBinding:
    """Keyboard binding configuration.

    Attributes:
        key (str): Key combination (e.g., "ctrl+s")
        action (str): Action identifier
        description (str): Action description
        handler (Optional[Callable]): Action handler
        show (bool): Show in help screen
    """

    key: str
    action: str
    description: str
    handler: Optional[Callable] = None
    show: bool = True


class KeyboardManager:
    """Keyboard shortcut manager.

    Attributes:
        bindings (Dict[str, KeyBinding]): Registered key bindings
    """

    def __init__(self) -> None:
        """Initialize the keyboard manager."""
        self.bindings: Dict[str, KeyBinding] = {}
        self.events = event_manager

    def register(self, binding: KeyBinding) -> None:
        """Register a key binding.

        Args:
            binding: Key binding configuration
        """
        self.bindings[binding.action] = binding
        logger.debug(f"Registered key binding: {binding.key} -> {binding.action}")

    def register_many(self, bindings: List[KeyBinding]) -> None:
        """Register multiple key bindings.

        Args:
            bindings: List of key bindings
        """
        for binding in bindings:
            self.register(binding)

    def get_binding(self, action: str) -> Optional[KeyBinding]:
        """Get binding by action.

        Args:
            action: Action identifier

        Returns:
            Optional[KeyBinding]: Key binding if found
        """
        return self.bindings.get(action)

    def get_bindings(self) -> List[KeyBinding]:
        """Get all bindings.

        Returns:
            List[KeyBinding]: List of key bindings
        """
        return list(self.bindings.values())

    async def handle_action(self, action: str, *args: Any, **kwargs: Any) -> None:
        """Handle a key action.

        Args:
            action: Action identifier
            *args: Additional arguments
            **kwargs: Additional keyword arguments
        """
        binding = self.get_binding(action)
        if binding and binding.handler:
            try:
                await binding.handler(*args, **kwargs)
                await self.events.emit(
                    "key_action",
                    {
                        "action": action,
                        "key": binding.key,
                        "args": args,
                        "kwargs": kwargs,
                    },
                )
            except Exception as e:
                logger.error(f"Error handling key action {action}: {e}")
                await self.events.emit("key_error", {"action": action, "error": str(e)})
