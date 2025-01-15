"""Theme management module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import aiofiles
import structlog
import yaml

if TYPE_CHECKING:
    from pathlib import Path


logger = structlog.get_logger(__name__)


class Theme:
    """Theme class for PepperPy Console."""

    def __init__(self, data: dict) -> None:
        """Initialize a theme.

        Args:
            data: Theme data.

        """
        self.name = data.get("name", "default")
        self.data = data

    @classmethod
    async def load(cls, path: Path) -> "Theme":
        """Load a theme from a file.

        Args:
            path: Path to theme file.

        Returns:
            Theme: Loaded theme.

        """
        async with aiofiles.open(path, encoding="utf-8") as f:
            content = await f.read()
            data = yaml.safe_load(content)
        return cls(data)


class ThemeManager:
    """Theme manager class."""

    def __init__(self) -> None:
        """Initialize the theme manager."""
        self.themes: dict[str, Theme] = {}
        self.current_theme: Theme | None = None

    async def load_themes(self, themes_dir: Path) -> None:
        """Load themes from a directory.

        Args:
            themes_dir: Directory containing theme files

        """
        for theme_file in themes_dir.glob("*.yaml"):
            theme = await Theme.load(theme_file)
            self.themes[theme.name] = theme

    def set_theme(self, name: str) -> None:
        """Set the current theme.

        Args:
            name: Theme name

        """
        if name in self.themes:
            self.current_theme = self.themes[name]

    def get_theme(self, name: str) -> Theme | None:
        """Get a theme by name.

        Args:
            name: Theme name

        Returns:
            The theme if found, None otherwise

        """
        return self.themes.get(name)
