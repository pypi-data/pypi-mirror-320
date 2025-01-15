"""PepperPy TUI application."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Protocol, TypeVar, cast, overload

from pepperpy_core.plugin import PluginConfig, PluginManager
from textual.app import App, AwaitMount
from textual.widgets import Static

from pepperpy.theme import ThemeManager
from pepperpy.tui.help import HelpViewer
from pepperpy.tui.screens.exceptions import ScreenNotFoundError
from pepperpy.tui.widgets.dialog import AlertDialog
from pepperpy.tui.widgets.notification import NotificationCenter

from .commands import CommandManager
from .screens import PepperScreen

if TYPE_CHECKING:
    from asyncio import Future
    from collections.abc import Awaitable, Callable

    from textual.screen import Screen
    from textual.widget import Widget


ScreenResultType = TypeVar("ScreenResultType")


class DialogCallback(Protocol):
    """Protocol for dialog callbacks."""

    async def __call__(
        self,
        *args: str | float | bool | None,
        **kwargs: str | float | bool | None,
    ) -> None:
        """Execute the dialog callback."""


class PepperApp(App[Any]):
    """Base application class for PepperPy TUI."""

    def __init__(
        self,
        screen_map: dict[str, type[PepperScreen]] | None = None,
    ) -> None:
        """Initialize the application.

        Args:
            screen_map: A mapping of screen names to screen classes.

        """
        super().__init__()
        self.screen_map = screen_map or {}
        self.plugin_manager = PluginManager()
        self.theme_manager = ThemeManager()
        self.help_viewer = HelpViewer()
        self.command_manager = CommandManager()
        self.notification_center = NotificationCenter()
        self.themes = self.theme_manager
        self._screen_stack: list[Screen[Any]] = []

    if not TYPE_CHECKING:

        async def on_mount(self) -> None:
            """Handle application mount event."""
            await super().on_mount()  # type: ignore
            self.notification_center = NotificationCenter()
            await self.mount(self.notification_center)

    async def show_dialog(
        self,
        title: str,
        content: str | Widget,
        callback: DialogCallback | None = None,
        *,
        wait_for_dismiss: bool = False,
    ) -> None:
        """Show a dialog.

        Args:
            title: Dialog title.
            content: Dialog content.
            callback: Dialog callback.
            wait_for_dismiss: Whether to wait for dialog dismissal.

        """
        dialog_content = (
            content if isinstance(content, Static) else Static(str(content))
        )
        dialog = AlertDialog(title=title, content=dialog_content, on_close=callback)
        await self.push_screen(dialog)
        if wait_for_dismiss:
            await dialog.wait_for_dismiss()

    async def load_plugins(self, plugins_dir: Path | str) -> None:
        """Load plugins from a directory.

        Args:
            plugins_dir: The directory containing plugins

        """
        # Configure plugin manager
        config = PluginConfig(name="pepperpy-console", plugin_dir=str(plugins_dir))
        self.plugin_manager = PluginManager(config=config)

        # Initialize plugins
        await self.plugin_manager.initialize()

    async def load_themes(self, themes_dir: Path | str) -> None:
        """Load themes from a directory.

        Args:
            themes_dir: The directory containing themes

        """
        if isinstance(themes_dir, str):
            themes_dir = Path(themes_dir)
        await self.theme_manager.load_themes(themes_dir)

    @overload
    def push_screen(
        self,
        screen: Screen[ScreenResultType] | str,
        callback: (
            Callable[[ScreenResultType | None], None]
            | Callable[[ScreenResultType | None], Awaitable[None]]
            | None
        ) = None,
        wait_for_dismiss: Literal[False] = False,
    ) -> AwaitMount: ...

    @overload
    def push_screen(
        self,
        screen: Screen[ScreenResultType] | str,
        callback: (
            Callable[[ScreenResultType | None], None]
            | Callable[[ScreenResultType | None], Awaitable[None]]
            | None
        ) = None,
        wait_for_dismiss: Literal[True] = True,
    ) -> Future[ScreenResultType]: ...

    def push_screen(
        self,
        screen: Screen[ScreenResultType] | str,
        callback: (
            Callable[[ScreenResultType | None], None]
            | Callable[[ScreenResultType | None], Awaitable[None]]
            | None
        ) = None,
        wait_for_dismiss: bool = False,
    ) -> AwaitMount | Future[ScreenResultType]:
        """Push a screen onto the screen stack.

        Args:
            screen: Screen to push onto the stack
            callback: Optional callback to execute when screen is dismissed
            wait_for_dismiss: Whether to wait for screen dismissal

        Returns:
            The await mount result if not waiting for dismissal,
            or a Future if waiting.

        Raises:
            ScreenError: If the screen is not found.

        """
        if isinstance(screen, str):
            if screen not in self.screen_map:
                raise ScreenNotFoundError(f"Screen {screen} not found")
            screen = self.screen_map[screen]()

        screen_name = screen.__class__.__name__
        if isinstance(screen, PepperScreen):
            self.screen_map[screen_name] = screen.__class__

        self._screen_stack.append(screen)
        if wait_for_dismiss:
            return cast(
                "Future[ScreenResultType]",
                super().push_screen(screen, callback, wait_for_dismiss=True),
            )
        return super().push_screen(screen, callback, wait_for_dismiss=False)

    def pop_screen(self) -> Any:
        """Pop a screen from the screen stack.

        Returns:
            The await mount result.

        """
        if len(self._screen_stack) > 1:
            screen = self._screen_stack.pop()
            screen.remove()
            return self.mount(self._screen_stack[-1])
        return self.mount(self._screen_stack[-1])

    def switch_screen(
        self,
        screen: Screen[ScreenResultType] | str,
    ) -> Any:
        """Switch to a new screen.

        Args:
            screen: Screen to switch to

        Returns:
            The await mount result.

        Raises:
            ScreenError: If the screen is not found.

        """
        if isinstance(screen, str):
            if screen not in self.screen_map:
                raise ScreenNotFoundError(f"Screen {screen} not found")
            screen = self.screen_map[screen]()

        if self._screen_stack:
            current_screen = self._screen_stack.pop()
            current_screen.remove()

        self._screen_stack.append(screen)
        return self.mount(screen)
