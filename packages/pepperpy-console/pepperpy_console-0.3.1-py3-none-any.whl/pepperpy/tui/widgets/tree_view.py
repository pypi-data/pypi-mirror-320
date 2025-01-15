"""TreeView widget for displaying hierarchical data."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog
from textual.containers import Container
from textual.message import Message
from textual.widgets import Static

from .base import EventData, PepperWidget

if TYPE_CHECKING:
    from collections.abc import Generator


logger = structlog.get_logger(__name__)

type NodeData = str | int | float | bool | None | dict[str, NodeData] | list[NodeData]


class TreeNode(PepperWidget, Static):
    """Tree node widget.

    Attributes:
        label (str): Node label
        children (List[TreeNode]): Child nodes
        is_expanded (bool): Whether node is expanded
        level (int): Node indentation level
        data (Any): Optional associated data

    """

    class NodeClicked(Message):
        """Node clicked message.

        Attributes:
            node (TreeNode): Clicked node

        """

        def __init__(self, node: "TreeNode") -> None:
            """Initialize node clicked message.

            Args:
                node: Clicked node

            """
            super().__init__()
            self.node = node

    DEFAULT_CSS = """
    TreeNode {
        width: 100%;
        height: 1;
        color: $text;
        background: $surface;
        content-align: left middle;
        padding-left: 2;
    }

    TreeNode:hover {
        background: $surface-lighten-1;
    }

    TreeNode.-selected {
        background: $selection;
        color: $text;
    }

    TreeNode.-has-children {
        height: auto;
    }
    """

    def __init__(
        self,
        *args: tuple[()],
        label: str,
        children: list["TreeNode"] | None = None,
        is_expanded: bool = False,
        level: int = 0,
        data: NodeData = None,
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize tree node.

        Args:
            label: The label to display for this node.
            children: Child nodes of this node.
            is_expanded: Whether this node is expanded.
            level: The indentation level of this node.
            data: Custom data associated with this node.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.label = label
        self._children = children or []
        self.is_expanded = is_expanded
        self.level = level
        self.data = data

        if self._children:
            self.add_class("-has-children")

    @property
    def children(self) -> list["TreeNode"]:
        """Get child nodes."""
        return self._children

    def render(self) -> str:
        """Render the node.

        Returns:
            str: Rendered content

        """
        indent = "  " * self.level
        icon = "▼ " if self.is_expanded else "▶ " if self.children else "  "
        return f"{indent}{icon}{self.label}"

    def toggle(self) -> None:
        """Toggle node expansion."""
        if self.children:
            self.is_expanded = not self.is_expanded
            self.refresh()

    async def on_click(self) -> None:
        """Handle click events."""
        self.toggle()
        await self.emit_event("clicked", {"node": self.label})


class TreeView(PepperWidget, Container):
    """Tree view widget for displaying hierarchical data.

    Attributes:
        nodes (List[TreeNode]): Root level nodes
        selected_node (Optional[TreeNode]): Currently selected node

    """

    DEFAULT_CSS = """
    TreeView {
        layout: vertical;
        width: 100%;
        height: auto;
        background: $surface;
        border: tall $primary;
        padding: 0;
        margin: 1 0;
        overflow-y: scroll;
    }
    """

    def __init__(
        self,
        *args: tuple[()],
        data: dict[str, NodeData] | list[NodeData],
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize tree view.

        Args:
            data: The data to display in the tree.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.data = data
        self.nodes: list[TreeNode] = []
        self.selected_node: TreeNode | None = None

    def _build_tree(
        self,
        data: dict[str, NodeData] | list[NodeData],
        level: int = 0,
    ) -> list[TreeNode]:
        """Build tree structure from data.

        Args:
            data: Tree data structure
            level: Current indentation level

        Returns:
            List[TreeNode]: Created tree nodes

        """
        nodes = []

        if isinstance(data, dict):
            items = [(k, v) for k, v in data.items()]
        else:
            items = [(str(i), item) for i, item in enumerate(data)]

        for key, value in items:
            if isinstance(value, dict | list):
                children = self._build_tree(value, level + 1)
                node = TreeNode(
                    label=key,
                    children=children,
                    level=level,
                    data=value,
                )
            else:
                node = TreeNode(label=key, level=level, data=value)
            nodes.append(node)

        return nodes

    def compose(self) -> Generator[TreeNode, None, None]:
        """Compose the tree view layout."""
        for node in self.nodes:
            yield node
            if node.is_expanded:
                yield from node.children

    def select_node(self, node: TreeNode) -> None:
        """Select a tree node.

        Args:
            node: Node to select

        """
        if self.selected_node:
            self.selected_node.remove_class("-selected")
        node.add_class("-selected")
        self.selected_node = node

    async def on_tree_node_node_clicked(self, message: TreeNode.NodeClicked) -> None:
        """Handle node click events."""
        self.select_node(message.node)

    def _get_visible_nodes(self) -> Generator[TreeNode, None, None]:
        """Get all visible nodes in the tree."""
        for node in self.nodes:
            yield node
            if node.is_expanded:
                yield from node.children
