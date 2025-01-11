"""Navigation components for TUI applications."""

from dataclasses import dataclass
from typing import Any, Callable, List, Optional

import structlog
from textual.widgets import Tree
from textual.widgets.tree import TreeNode, NodeSelected

from .base import PepperWidget

logger = structlog.get_logger(__name__)


@dataclass
class MenuItem:
    """Menu item configuration.

    Attributes:
        label (str): Display label
        action (Optional[Callable]): Action to execute
        children (List[MenuItem]): Submenu items
        icon (Optional[str]): Optional icon
    """

    label: str
    action: Optional[Callable] = None
    children: List["MenuItem"] = None
    icon: Optional[str] = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.children is None:
            self.children = []


class Navigation(PepperWidget, Tree):
    """Navigation menu with hierarchical structure.

    Attributes:
        items (List[MenuItem]): Menu items
        current_path (List[str]): Current navigation path
    """

    def __init__(self, *args: Any, items: List[MenuItem], **kwargs: Any) -> None:
        """Initialize the navigation widget.

        Args:
            *args: Positional arguments
            items: Menu items
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.items = items
        self.current_path: List[str] = []

    def compose(self) -> None:
        """Compose the navigation layout."""
        self.root.expand()
        for item in self.items:
            self._add_menu_item(self.root, item)

    def _add_menu_item(self, parent: TreeNode, item: MenuItem) -> None:
        """Add a menu item to the tree.

        Args:
            parent: Parent tree node
            item: Menu item to add
        """
        node = parent.add(item.label, data={"action": item.action}, expand=True)
        if item.icon:
            node.set_icon(item.icon)

        for child in item.children:
            self._add_menu_item(node, child)

    async def on_tree_node_selected(self, event: NodeSelected) -> None:
        """Handle node selection events.

        Args:
            event: Node selection event
        """
        node = event.node
        action = node.data.get("action")

        if action:
            try:
                if callable(action):
                    await action()
                await self.events.emit(
                    "action",
                    {
                        "path": self.current_path + [node.label],
                        "action": action.__name__
                        if hasattr(action, "__name__")
                        else str(action),
                    },
                )
            except Exception as e:
                logger.error(f"Error executing action: {e}")
                await self.events.emit("error", str(e))

        self.current_path = self._get_path(node)
        await self.events.emit("path_changed", self.current_path)

    def _get_path(self, node: TreeNode) -> List[str]:
        """Get the path to a node.

        Args:
            node: Tree node

        Returns:
            List[str]: Path components
        """
        path = []
        current = node
        while current.parent is not None:
            path.insert(0, current.label)
            current = current.parent
        return path
