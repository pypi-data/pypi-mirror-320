"""Navigation widget for PepperPy Console."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from textual.widgets import Tree

from .base import EventData, PepperWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from textual.widgets.tree import TreeNode


class Navigation(PepperWidget):
    """Navigation widget for PepperPy Console.

    Attributes:
        _tree: The navigation tree.
        current_path: The current path in the tree.

    """

    def __init__(self, *args: tuple[()], **kwargs: dict[str, EventData]) -> None:
        """Initialize the navigation widget.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self._tree: Tree[Any] = Tree("Navigation")
        self.current_path: list[str] = []

    def compose(self) -> ComposeResult:
        """Compose the navigation widget.

        Returns:
            The compose result.

        """
        yield self._tree

    def find_node_by_path(self, path: str) -> TreeNode[Any] | None:
        """Find a node in the tree by its path.

        Args:
            path: The path to find.

        Returns:
            The node if found, None otherwise.

        """
        if not self._tree.root:
            return None

        current = self._tree.root
        parts = path.split("/")

        for part in parts:
            if not part:
                continue

            found = False
            for child in current.children:
                if child.label == part:
                    current = child
                    found = True
                    break

            if not found:
                return None

        return current

    def _get_path(self, node: TreeNode[Any]) -> list[str]:
        """Get the path to a node.

        Args:
            node: The node to get the path for.

        Returns:
            The path to the node.

        """
        path: list[str] = []
        current = node
        while current.parent is not None:
            path.insert(0, str(current.label))
            current = current.parent
        return path

    def on_tree_node_selected(self, event: Tree.NodeSelected[Any]) -> None:
        """Handle tree node selection.

        Args:
            event: The node selected event.

        """
        self.current_path = self._get_path(event.node)
