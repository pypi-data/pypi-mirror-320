"""Keyboard management for CLI applications."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class KeyBinding:
    """Keyboard binding definition.

    Attributes:
        key (str): Key combination
        description (str): Binding description
        callback (Callable): Callback function
        group (Optional[str]): Binding group name
    """

    key: str
    description: str = ""
    callback: Optional[Callable] = None
    group: Optional[str] = None

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the binding callback.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Any: Callback result
        """
        if self.callback:
            return await self.callback(*args, **kwargs)
        return None


@dataclass
class KeyBindingGroup:
    """Group of related key bindings.

    Attributes:
        name (str): Group name
        description (str): Group description
        bindings (List[KeyBinding]): Bindings in the group
    """

    name: str
    description: str = ""
    bindings: List[KeyBinding] = field(default_factory=list)

    def add_binding(self, binding: KeyBinding) -> None:
        """Add a binding to the group.

        Args:
            binding: Binding to add
        """
        binding.group = self.name
        self.bindings.append(binding)


class KeyboardManager:
    """Manager for keyboard bindings and groups.

    Attributes:
        bindings (Dict[str, KeyBinding]): Registered bindings
        groups (Dict[str, KeyBindingGroup]): Binding groups
    """

    def __init__(self) -> None:
        """Initialize the keyboard manager."""
        self.bindings: Dict[str, KeyBinding] = {}
        self.groups: Dict[str, KeyBindingGroup] = {}

    def register_binding(self, binding: KeyBinding) -> None:
        """Register a key binding.

        Args:
            binding: Binding to register
        """
        self.bindings[binding.key] = binding
        if binding.group and binding.group not in self.groups:
            self.groups[binding.group] = KeyBindingGroup(name=binding.group)
            self.groups[binding.group].add_binding(binding)

    def register_group(self, group: KeyBindingGroup) -> None:
        """Register a binding group.

        Args:
            group: Group to register
        """
        self.groups[group.name] = group
        for binding in group.bindings:
            self.bindings[binding.key] = binding

    def get_binding(self, key: str) -> Optional[KeyBinding]:
        """Get a binding by key.

        Args:
            key: Key combination

        Returns:
            Optional[KeyBinding]: Binding if found
        """
        return self.bindings.get(key)

    def get_group(self, name: str) -> Optional[KeyBindingGroup]:
        """Get a binding group by name.

        Args:
            name: Group name

        Returns:
            Optional[KeyBindingGroup]: Group if found
        """
        return self.groups.get(name)

    def list_bindings(self) -> List[KeyBinding]:
        """List all registered bindings.

        Returns:
            List[KeyBinding]: List of bindings
        """
        return list(self.bindings.values())

    def list_groups(self) -> List[KeyBindingGroup]:
        """List all binding groups.

        Returns:
            List[KeyBindingGroup]: List of groups
        """
        return list(self.groups.values()) 