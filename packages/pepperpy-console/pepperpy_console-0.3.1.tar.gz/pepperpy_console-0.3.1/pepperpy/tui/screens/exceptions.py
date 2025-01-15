"""Screen-related exceptions."""

from __future__ import annotations


class ScreenError(Exception):
    """Base class for screen-related exceptions."""

    pass


class ScreenNotFoundError(ScreenError):
    """Raised when a screen is not found."""

    pass
