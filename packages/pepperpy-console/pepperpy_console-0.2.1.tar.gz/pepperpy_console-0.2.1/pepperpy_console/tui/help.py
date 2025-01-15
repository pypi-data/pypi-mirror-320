"""Help system for documentation and keyboard shortcuts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import structlog
from rich.markdown import Markdown
from textual.containers import Container, Vertical
from textual.widgets import Static

from .widgets.base import PepperWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from .keyboard import KeyBinding

logger = structlog.get_logger(__name__)


@dataclass
class HelpSection:
    """Help section configuration.

    Attributes:
        title (str): Section title
        content (str): Section content in markdown
        category (str): Section category
        order (int): Display order

    """

    title: str
    content: str
    category: str = "General"
    order: int = 0


class HelpContent(PepperWidget, Static):
    """Widget for displaying help content.

    Attributes:
        content (str): Current content

    """

    DEFAULT_CSS = """
    HelpContent {
        background: $background;
        color: $text;
        padding: 1;
    }
    """

    def __init__(
        self,
        *args: str | float | bool | None,
        content: str = "",
        **kwargs: str | float | bool | None,
    ) -> None:
        """Initialize the help content widget.

        Args:
            *args: Positional arguments
            content: Initial content
            **kwargs: Keyword arguments

        """
        super().__init__(*args, **kwargs)
        self.content = content

    def render(self) -> Markdown:
        """Render the content.

        Returns:
            Markdown: Rendered content

        """
        return Markdown(self.content)


class HelpViewer(PepperWidget, Container):
    """Help viewer with sections and navigation.

    Attributes:
        sections (Dict[str, HelpSection]): Available help sections
        current_section (Optional[str]): Currently displayed section

    """

    DEFAULT_CSS = """
    HelpViewer {
        background: $background;
        border: solid $primary;
        padding: 1;
        width: 60%;
        height: auto;
        align: center middle;
        display: none;
    }

    HelpViewer.-visible {
        display: block;
    }

    HelpViewer #content {
        height: 20;
        border: solid $primary;
        overflow-y: scroll;
    }
    """

    def __init__(
        self,
        *args: str | float | bool | None,
        **kwargs: str | float | bool | None,
    ) -> None:
        """Initialize the help viewer."""
        super().__init__(*args, **kwargs)
        self.sections: dict[str, HelpSection] = {}
        self.current_section: str | None = None
        self._content = Vertical(widget_id="content")

    def compose(self) -> ComposeResult:
        """Compose the help viewer layout."""
        yield self._content

    def add_section(self, section: HelpSection) -> None:
        """Add a help section.

        Args:
            section: Help section to add.

        """
        self.sections[section.title] = section
        logger.debug("Added help section: %s", section.title)

    async def show_section(self, title: str) -> None:
        """Show a help section.

        Args:
            title: Section title.

        """
        if title in self.sections:
            section = self.sections[title]
            await self._content.mount(HelpContent(content=section.content))
        else:
            logger.error("Help section not found: %s", title)

    def clear(self) -> None:
        """Clear the current section."""
        self.current_section = None
        self.remove_class("-visible")
        self._content.remove_children()


class KeyboardHelpSection(HelpSection):
    """Help section for keyboard shortcuts."""

    @classmethod
    def generate(cls, bindings: list["KeyBinding"]) -> "KeyboardHelpSection":
        """Generate keyboard help section.

        Args:
            bindings: List of key bindings

        Returns:
            KeyboardHelpSection: Generated help section

        """
        content = "# Keyboard Shortcuts\n\n"
        for binding in bindings:
            content += f"- **{binding.key}**: {binding.description}\n"

        return cls(
            title="Keyboard Shortcuts",
            content=content,
            category="Help",
            order=0,
        )
