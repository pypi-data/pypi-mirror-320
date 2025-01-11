"""Input widgets with validation."""

from typing import Any, Callable, List, Optional, Type

import structlog
from textual.widgets import Input

from .base import PepperWidget

logger = structlog.get_logger(__name__)


class ValidatedInput(PepperWidget, Input):
    """Input widget with validation.

    Attributes:
        type (Type): Expected value type
        required (bool): Whether input is required
        validators (List[callable]): Value validators
        error (Optional[str]): Current validation error
    """

    COMPONENT_CLASSES = {
        "input--placeholder": "Input placeholder",
        "validated-input--invalid": "Input is invalid",
        "validated-input--valid": "Input is valid",
    }

    DEFAULT_CSS = """
    ValidatedInput {
        background: $surface-darken-1;
        color: $text;
        border: tall $primary;
        padding: 1 2;
        margin: 0 1 1 1;
        min-width: 30;
        max-width: 100%;
        height: 3;
    }

    ValidatedInput:focus {
        border: tall $accent;
        background: $surface;
    }

    ValidatedInput.validated-input--invalid {
        border: tall $error;
        background: $error 10%;
    }

    ValidatedInput.validated-input--valid {
        border: tall $success;
        background: $success 10%;
    }

    ValidatedInput .input--placeholder {
        color: $text-muted;
        opacity: 0.7;
    }
    """

    def __init__(
        self,
        *args: Any,
        type: Type = str,
        required: bool = True,
        validators: Optional[List[Callable]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the input widget.

        Args:
            *args: Positional arguments
            type: Expected type
            required: Whether input is required
            validators: Optional value validators
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.type = type
        self.required = required
        self.validators = validators or []
        self.error: Optional[str] = None

    @property
    def typed_value(self) -> Any:
        """Get the typed value.

        Returns:
            Any: Converted value
        """
        try:
            return self.type(self.value) if self.value else None
        except (ValueError, TypeError):
            return None

    async def validate(self) -> bool:
        """Validate the input value.

        Returns:
            bool: Whether validation passed
        """
        self.error = None
        self.remove_class("validated-input--invalid")
        self.remove_class("validated-input--valid")

        # Check required
        if self.required and not self.value:
            self.error = "This field is required"
            self.add_class("validated-input--invalid")
            await self.events.emit("validation_error", self.error)
            return False

        # Check type conversion
        if self.value and self.typed_value is None:
            self.error = f"Invalid {self.type.__name__} value"
            self.add_class("validated-input--invalid")
            await self.events.emit("validation_error", self.error)
            return False

        # Run validators
        for validator in self.validators:
            try:
                result = validator(self.typed_value)
                if result is not True:
                    self.error = str(result)
                    self.add_class("validated-input--invalid")
                    await self.events.emit("validation_error", self.error)
                    return False
            except Exception as e:
                self.error = str(e)
                self.add_class("validated-input--invalid")
                await self.events.emit("validation_error", self.error)
                return False

        self.add_class("validated-input--valid")
        await self.events.emit("validation_success", self.typed_value)
        return True

    def clear(self) -> None:
        """Clear the input value."""
        self.value = ""
        self.error = None
        self.remove_class("validated-input--invalid")
        self.remove_class("validated-input--valid")


class ModelInput(ValidatedInput):
    """Input widget bound to a data model field.

    Attributes:
        model (Type): Data model class
        field (str): Model field name
    """

    def __init__(
        self,
        *args: Any,
        model: Type,
        field: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the model input.

        Args:
            *args: Positional arguments
            model: Data model class
            field: Model field name
            **kwargs: Keyword arguments
        """
        field_info = model.__fields__[field]
        super().__init__(
            *args,
            type=field_info.type_,
            required=field_info.required,
            validators=field_info.validators,
            **kwargs,
        )
        self.model = model
        self.field = field
