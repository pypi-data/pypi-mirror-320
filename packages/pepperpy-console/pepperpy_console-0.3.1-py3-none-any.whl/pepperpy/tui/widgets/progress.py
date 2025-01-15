"""Progress indicator widgets for TUI applications."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import structlog
from rich.progress import Progress as RichProgress
from rich.progress import TaskID
from textual.containers import Container
from textual.widgets import Static

from .base import EventData, PepperWidget

if TYPE_CHECKING:
    from rich.console import ConsoleRenderable, RichCast
    from textual.app import ComposeResult
    from textual.visual import SupportsVisual


logger = structlog.get_logger(__name__)


class Progress(PepperWidget, Static):
    """Enhanced progress bar with status messages.

    Attributes:
        total (float): Total progress value
        status (str): Current status message

    """

    def __init__(
        self,
        *args: tuple[()],
        total: float = 100.0,
        status: str = "",
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize the progress widget.

        Args:
            total: The total value for 100% progress.
            status: The status text to display.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.total = total
        self.current = 0.0
        self.status = status
        self.percentage = 0.0

    def compose(self) -> ComposeResult:
        """Compose the progress widget layout."""
        container = Container()
        yield container

    def update(
        self,
        content: ConsoleRenderable | RichCast | str | SupportsVisual | None = None,
    ) -> None:
        """Update widget content.

        Args:
            content: New content to display

        """
        if content is not None:
            self.status = str(content)
        super().update(self.status)

    async def update_progress(self, progress: float, status: str | None = None) -> None:
        """Update progress and status.

        Args:
            progress: New progress value
            status: Optional new status message

        """
        self.current = progress
        self.percentage = min(100, (progress / self.total) * 100)

        if status is not None:
            self.status = status

        await self.emit_event(
            "progress",
            {
                "value": progress,
                "total": self.total,
                "percentage": self.percentage,
                "status": self.status,
            },
        )


class SpinnerProgress(PepperWidget):
    """Spinner progress indicator for indeterminate operations.

    Attributes:
        message (str): Display message
        spinner_style (str): Rich spinner style

    """

    def __init__(
        self,
        *args: tuple[()],
        message: str = "",
        spinner_style: str = "dots",
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize the spinner widget.

        Args:
            message: The message to display.
            spinner_style: The style of spinner to use.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.message = message
        self.spinner_style = spinner_style
        self._progress = RichProgress()
        self._task: asyncio.Task[Any] | None = None
        self._task_id: TaskID | None = None

    def start(self) -> None:
        """Start the spinner animation."""
        if not self._task:
            self._task_id = self._progress.add_task(
                self.message,
                total=None,
                spinner_style=self.spinner_style,
            )
            self._task = asyncio.create_task(self._run_spinner())

    def stop(self) -> None:
        """Stop the spinner animation."""
        if self._task:
            self._task.cancel()
            self._task = None
            if self._task_id is not None:
                self._progress.remove_task(self._task_id)
                self._task_id = None

    def update_message(self, message: str) -> None:
        """Update the display message.

        Args:
            message: New message

        """
        self.message = message
        if self._task_id is not None:
            self._progress.update(self._task_id, description=message)

    async def _run_spinner(self) -> None:
        """Run the spinner animation."""
        while True:
            await asyncio.sleep(0.1)
            if self._task_id is not None:
                self._progress.update(self._task_id)
