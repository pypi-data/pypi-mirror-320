"""Search bar widget for PepperPy Console."""

from __future__ import annotations

import structlog
from textual.containers import Container

logger = structlog.get_logger(__name__)


class FilterableList(Container):
    """Filterable list widget."""

    def __init__(
        self,
        items: list[str],
        *,
        _name: str | None = None,
    ) -> None:
        """Initialize filterable list.

        Args:
            items: List items.
            _name: Optional widget name.

        """
        super().__init__()
        self.items = items
