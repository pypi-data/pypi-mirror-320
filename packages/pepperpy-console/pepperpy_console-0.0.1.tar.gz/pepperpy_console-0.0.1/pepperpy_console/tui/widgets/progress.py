"""Progress indicator widgets for TUI applications."""

from typing import Any, Optional

import structlog
from rich.progress import Progress as RichProgress
from rich.progress import TaskID
from textual.widgets import LoadingIndicator
from textual.widgets import Static

from .base import PepperWidget

logger = structlog.get_logger(__name__)


class Progress(PepperWidget, Static):
    """Enhanced progress bar with status messages.

    Attributes:
        total (float): Total progress value
        status (str): Current status message
    """

    def __init__(
        self, *args: Any, total: float = 100.0, status: str = "", **kwargs: Any
    ) -> None:
        """Initialize the progress widget.

        Args:
            *args: Positional arguments
            total: Total progress value
            status: Initial status message
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.total = total
        self.status = status
        self.percentage = 0.0
        self._loading = LoadingIndicator()

    def compose(self) -> None:
        """Compose the progress widget layout."""
        yield self._loading

    async def update(self, progress: float, status: Optional[str] = None) -> None:
        """Update progress and status.

        Args:
            progress: New progress value
            status: Optional new status message
        """
        self.percentage = min(100, (progress / self.total) * 100)

        if status is not None:
            self.status = status
            self.update(f"{self.status} ({self.percentage:.1f}%)")

        await self.events.emit(
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
        self, *args: Any, message: str = "", spinner_style: str = "dots", **kwargs: Any
    ) -> None:
        """Initialize the spinner widget.

        Args:
            *args: Positional arguments
            message: Display message
            spinner_style: Rich spinner style
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.message = message
        self.spinner_style = spinner_style
        self._progress = RichProgress()
        self._task: Optional[TaskID] = None

    def start(self) -> None:
        """Start the spinner animation."""
        if not self._task:
            self._task = self._progress.add_task(
                self.message, total=None, spinner_style=self.spinner_style
            )

    def stop(self) -> None:
        """Stop the spinner animation."""
        if self._task:
            self._progress.remove_task(self._task)
            self._task = None

    def update_message(self, message: str) -> None:
        """Update the display message.

        Args:
            message: New message
        """
        self.message = message
        if self._task:
            self._progress.update(self._task, description=message)
