"""TreeView widget for displaying hierarchical data."""

from typing import Any, Dict, List, Optional, Union

import structlog
from textual.containers import Container
from textual.message import Message
from textual.widgets import Static

from .base import PepperWidget

logger = structlog.get_logger(__name__)


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
        *args: Any,
        label: str,
        children: Optional[List["TreeNode"]] = None,
        is_expanded: bool = False,
        level: int = 0,
        data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Initialize tree node.

        Args:
            *args: Positional arguments
            label: Node label
            children: Optional child nodes
            is_expanded: Whether node is expanded
            level: Node indentation level
            data: Optional associated data
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.label = label
        self.children = children or []
        self.is_expanded = is_expanded
        self.level = level
        self.data = data

        if self.children:
            self.add_class("-has-children")

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
        await self.emit_no_wait(self.NodeClicked(self))


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
        *args: Any,
        data: Union[List[Dict[str, Any]], Dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        """Initialize tree view.

        Args:
            *args: Positional arguments
            data: Tree data structure
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.nodes: List[TreeNode] = []
        self.selected_node: Optional[TreeNode] = None
        self._build_tree(data)

    def _build_tree(
        self, data: Union[List[Dict[str, Any]], Dict[str, Any]], level: int = 0
    ) -> List[TreeNode]:
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
            if isinstance(value, (dict, list)):
                children = self._build_tree(value, level + 1)
                node = TreeNode(
                    label=key,
                    children=children,
                    level=level,
                    data=value,
                )
                nodes.append(node)
            else:
                node = TreeNode(
                    label=f"{key}: {value}",
                    level=level,
                    data=value,
                )
                nodes.append(node)

        return nodes

    def compose(self) -> None:
        """Compose the tree view layout."""
        for node in self.nodes:
            yield node
            if node.is_expanded:
                for child in node.children:
                    yield child

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
