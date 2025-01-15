"""Keyboard management for CLI applications."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

import structlog

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine


logger = structlog.get_logger(__name__)


class KeyBindingProtocol(Protocol):
    """Protocol for key binding execution."""

    async def execute(
        self,
        *args: str | float | bool | None,
        **kwargs: str | float | bool | None,
    ) -> str | int | float | bool | None:
        """Execute the key binding with arguments."""
        ...


class KeyBinding:
    """Key binding class for PepperPy CLI.

    Attributes:
        key: The key combination that triggers this binding
        callback: The function to call when the key is pressed
        description: A description of what the binding does

    """

    def __init__(
        self,
        key: str,
        callback: Callable[..., Coroutine[None, None, str | int | float | bool | None]],
        description: str = "",
    ) -> None:
        """Initialize a key binding.

        Args:
            key: The key combination that triggers this binding
            callback: The function to call when the key is pressed
            description: A description of what the binding does

        """
        self.key = key
        self.callback = callback
        self.description = description

    async def execute(
        self,
        *args: str | float | bool | None,
        **kwargs: str | float | bool | None,
    ) -> str | int | float | bool | None:
        """Execute the key binding with arguments.

        Args:
            *args: Positional arguments for the callback
            **kwargs: Keyword arguments for the callback

        Returns:
            The result of executing the callback

        """
        return await self.callback(*args, **kwargs)


class KeyBindingManager:
    """Manager for keyboard bindings."""

    def __init__(self) -> None:
        """Initialize the key binding manager."""
        self.bindings: dict[str, KeyBinding] = {}

    def add_binding(self, binding: KeyBinding) -> None:
        """Add a key binding.

        Args:
            binding: The key binding to add

        """
        self.bindings[binding.key] = binding

    def get_binding(self, key: str) -> KeyBinding | None:
        """Get a key binding by key.

        Args:
            key: The key combination

        Returns:
            The key binding if found, None otherwise

        """
        return self.bindings.get(key)

    def get_bindings(self) -> list[KeyBinding]:
        """Get all key bindings.

        Returns:
            A list of all key bindings

        """
        return list(self.bindings.values())

    async def handle_action(
        self,
        action: str,
        *args: str | float | bool | None,
        **kwargs: str | float | bool | None,
    ) -> None:
        """Handle a key action.

        Args:
            action: The key combination that was pressed
            *args: Additional arguments for the binding
            **kwargs: Additional keyword arguments for the binding

        """
        binding = self.get_binding(action)
        if binding:
            await binding.execute(*args, **kwargs)
