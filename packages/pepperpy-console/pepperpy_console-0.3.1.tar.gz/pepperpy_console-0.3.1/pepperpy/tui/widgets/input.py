"""Input widget for PepperPy Console."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.validation import Failure, ValidationResult, Validator
from textual.widgets import Input

from .base import EventData, PepperWidget

if TYPE_CHECKING:
    from collections.abc import Callable


class InvalidFieldTypeError(ValueError):
    """Raised when an invalid field type is provided."""

    def __init__(self, field_type: str) -> None:
        """Initialize the error.

        Args:
            field_type: The invalid field type.

        """
        super().__init__(f"Invalid field type: {field_type}")


class TypedValidator(Validator):
    """Validator for typed input values."""

    def __init__(self, validator_func: Callable[[str], bool], message: str) -> None:
        """Initialize the validator.

        Args:
            validator_func: Function to validate the input value.
            message: Error message to display on validation failure.

        """
        super().__init__()
        self.validator_func = validator_func
        self.message = message

    def validate(self, value: str) -> ValidationResult:
        """Validate the input value.

        Args:
            value: Value to validate.

        Returns:
            ValidationResult indicating if the value is valid.

        """
        try:
            is_valid = self.validator_func(value)
            if is_valid:
                return ValidationResult([])
            return ValidationResult([Failure(self, value, self.message)])
        except (ValueError, TypeError):
            return ValidationResult([Failure(self, value, self.message)])


class ValidatedInput(PepperWidget, Input):
    """Input widget with validation.

    Attributes:
        field_type (str): Type of field (text, number, etc.)
        required (bool): Whether the field is required
        validators (List[Validator]): List of validators to apply
        value (Any): Current value of the field

    """

    VALID_TYPES: ClassVar[set[str]] = {"text", "number"}

    def __init__(
        self,
        *args: tuple[()],
        field_type: str = "text",
        required: bool = False,
        validators: list[Validator] | None = None,
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize the input widget.

        Args:
            field_type: Type of field (text, number, etc.)
            required: Whether the field is required
            validators: List of validators to apply
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        """
        super().__init__(*args, **kwargs)
        if field_type not in self.VALID_TYPES:
            raise InvalidFieldTypeError(field_type)

        self.field_type = field_type
        self.required = required
        self._validators = validators or []

    def get_validators(self) -> list[Validator]:
        """Get the list of validators.

        Returns:
            List of validators to apply.

        """
        validators: list[Validator] = []
        if self.required:
            validators.append(
                TypedValidator(
                    lambda x: bool(x.strip()),
                    "This field is required",
                ),
            )

        if self.field_type == "number":
            validators.append(
                TypedValidator(
                    lambda x: bool(x.strip() and x.replace(".", "").isdigit()),
                    "Please enter a valid number",
                ),
            )

        validators.extend(self._validators)
        return validators

    def validate(self, value: str) -> ValidationResult | None:
        """Validate the input value.

        Args:
            value: Value to validate.

        Returns:
            ValidationResult indicating if the value is valid.

        """
        for validator in self.get_validators():
            result = validator.validate(value)
            if not result.is_valid:
                return result
        return None

    def get_value(self) -> str | int | float | bool | None:
        """Get the current value.

        Returns:
            Current value of the field.

        """
        if not self.value:
            return None

        if self.field_type == "number":
            try:
                value_str = str(self.value)
                if "." in value_str:
                    return float(value_str)
                return int(value_str)
            except (ValueError, TypeError):
                return None

        return self.value

    def set_value(self, value: str | float | bool | None) -> None:
        """Set the current value.

        Args:
            value: Value to set.

        """
        if value is None:
            self.value = ""
            return

        if self.field_type == "number":
            try:
                float(value)  # Validate number
                self.value = str(value)
            except (ValueError, TypeError):
                self.value = ""
        else:
            self.value = str(value)
