"""Theme management for PepperPy TUI."""

from pathlib import Path
from typing import Dict, Optional, Any
import yaml


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
        with open(path) as f:
            data = yaml.safe_load(f)
            if "metrics" in data:
                del data["metrics"]  # Remove metrics as it's not part of the theme
        return cls(**data)

    def __init__(self, name: str, colors: Dict[str, str], styles: Dict[str, Any]):
        """Initialize a theme.

        Args:
            name: Theme name
            colors: Color definitions
            styles: Style definitions
        """
        self.name = name
        self.colors = colors
        self.styles = styles


class ThemeManager:
    """Manager for PepperPy themes."""

    def __init__(self):
        """Initialize the theme manager."""
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None

    async def load_themes(self, themes_dir: Path) -> None:
        """Load all themes from a directory.

        Args:
            themes_dir: Directory containing theme files
        """
        for theme_file in themes_dir.glob("*.yaml"):
            theme = await Theme.load(theme_file)
            self.themes[theme.name] = theme

    async def load_theme(self, path: Path) -> Theme:
        """Load a theme from a file.

        Args:
            path: Path to theme file

        Returns:
            Loaded theme instance
        """
        theme = await Theme.load(path)
        self.themes[theme.name] = theme
        return theme

    def set_theme(self, name: str) -> None:
        """Set the current theme.

        Args:
            name: Theme name
        """
        if name not in self.themes:
            raise ValueError(f"Theme not found: {name}")
        self.current_theme = self.themes[name]

    def get_theme(self, name: str) -> Theme:
        """Get a theme by name.

        Args:
            name: Theme name

        Returns:
            Theme instance
        """
        if name not in self.themes:
            raise ValueError(f"Theme not found: {name}")
        return self.themes[name]
