"""Theme management for PepperPy Console."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import aiofiles
import structlog
import yaml

if TYPE_CHECKING:
    from pathlib import Path


logger = structlog.get_logger(__name__)


class Theme:
    """Theme class for PepperPy TUI.

    Attributes:
        name (str): Theme name
        colors (Dict[str, str]): Theme colors
        styles (Dict[str, str]): Theme styles

    """

    @classmethod
    async def load(cls, path: Path) -> "Theme":
        """Load a theme from a YAML file.

        Args:
            path: Path to theme file

        Returns:
            Loaded theme instance

        """
        async with aiofiles.open(path) as f:
            content = await f.read()
            data = yaml.safe_load(content)
            if "metrics" in data:
                del data["metrics"]  # Remove metrics as it's not part of the theme
            return cls(**data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Theme":
        """Create a theme from a dictionary.

        Args:
            data: Theme data dictionary.

        Returns:
            Theme: Created theme instance.

        """
        return cls(**data)

    def __init__(
        self,
        name: str,
        colors: dict[str, str],
        styles: dict[str, Any],
    ) -> None:
        """Initialize a theme.

        Args:
            name: Theme name
            colors: Theme colors
            styles: Theme styles

        """
        self.name = name
        self.colors = colors
        self.styles = styles


class ThemeManager:
    """Manager for PepperPy themes."""

    def __init__(self) -> None:
        """Initialize the theme manager."""
        self.themes: dict[str, Theme] = {}
        self.current_theme: Theme | None = None

    async def load_theme_file(self, path: Path) -> None:
        """Load a theme from a YAML file.

        Args:
            path: Path to the theme file.

        """
        async with aiofiles.open(path) as f:
            content = await f.read()
            data = yaml.safe_load(content)
            if "metrics" in data:
                self.metrics = data["metrics"]
            if "colors" in data:
                self.colors = data["colors"]

    async def load_themes(self, themes_dir: Path) -> None:
        """Load themes from a directory.

        Args:
            themes_dir: Directory containing theme files.

        Raises:
            ValueError: If theme directory not found.

        """
        if not themes_dir.exists():
            error_msg = "Theme directory not found"
            raise ValueError(error_msg)

        yaml_dir = themes_dir / "yaml"
        if not yaml_dir.exists():
            msg = f"Theme directory not found: {yaml_dir}"
            raise ValueError(msg)

        for theme_file in yaml_dir.glob("*.yaml"):
            await self.load_theme_file(theme_file)

    def set_theme(self, name: str) -> None:
        """Set the current theme.

        Args:
            name: Theme name.

        Raises:
            ValueError: If theme not found.

        """
        if name not in self.themes:
            error_msg = f"Theme not found: {name}"
            raise ValueError(error_msg)
        self.current_theme = self.themes[name]

    def get_theme(self, name: str) -> Theme:
        """Get a theme by name.

        Args:
            name: Theme name.

        Returns:
            The requested theme.

        Raises:
            ValueError: If theme not found.

        """
        if name not in self.themes:
            error_msg = f"Theme not found: {name}"
            raise ValueError(error_msg)
        return self.themes[name]
