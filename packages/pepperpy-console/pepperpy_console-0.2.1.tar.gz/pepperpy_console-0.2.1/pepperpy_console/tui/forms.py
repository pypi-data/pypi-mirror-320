"""Form widgets for PepperPy Console."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Container

from .widgets.base import PepperWidget

if TYPE_CHECKING:
    from collections.abc import Iterator


class PepperForm(PepperWidget, Container):
    """Base form widget for PepperPy Console."""

    def compose(self) -> Iterator[Container]:
        """Compose the form layout.

        Returns:
            Iterator[Container]: Form layout components.

        """
        yield Container()

    async def on_submit(self, data: dict[str, str | float | bool | None]) -> None:
        """Handle form submission.

        Args:
            data: Form data.

        """
        pass
