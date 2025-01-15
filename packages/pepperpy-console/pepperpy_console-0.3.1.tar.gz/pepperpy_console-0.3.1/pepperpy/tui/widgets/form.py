"""Form widgets for user input."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, cast

import structlog
from textual.containers import Container
from textual.widgets import Button, Static

from .base import EventData, PepperWidget
from .input import ValidatedInput

if TYPE_CHECKING:
    from collections.abc import Generator

    from textual.message import Message
    from textual.validation import Validator


logger = structlog.get_logger(__name__)


class FormField:
    """Form field configuration.

    Attributes:
        name (str): Field name
        label (str): Field label
        type (str): Field type
        required (bool): Whether the field is required
        validators (list[Callable]): Field validators

    """

    def __init__(
        self,
        name: str,
        label: str,
        type_name: Literal["text", "number", "password"] = "text",
        *,
        required: bool = False,
        validators: list[Validator] | None = None,
    ) -> None:
        """Initialize the form field.

        Args:
            name: Field name
            label: Field label
            type_name: Field type
            required: Whether the field is required
            validators: Field validators

        """
        self.name = name
        self.label = label
        self.type_name = type_name
        self.required = required
        self.validators = validators or []


class Form(PepperWidget, Container):
    """Form widget for user input.

    Attributes:
        fields (List[FormField]): Form fields
        values (Dict[str, Any]): Form values

    """

    def __init__(
        self,
        *args: tuple[()],
        fields: list[FormField],
        **kwargs: dict[str, EventData],
    ) -> None:
        """Initialize the form.

        Args:
            fields: Form fields
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        """
        super().__init__(*args, **kwargs)
        self.fields = fields
        self.values: dict[str, str | int | float | bool | None] = {}
        self._inputs: dict[str, ValidatedInput] = {}

    def compose(self) -> Generator[Static | ValidatedInput | Button, None, None]:
        """Compose the form.

        Yields:
            Form widgets.

        """
        for field in self.fields:
            yield Static(field.label)
            input_widget = ValidatedInput(
                field_type=field.type_name,
                required=field.required,
                validators=field.validators,
            )
            self._inputs[field.name] = input_widget
            yield input_widget

        yield Button("Submit", id="submit")

    def get_values(self) -> dict[str, str | int | float | bool | None]:
        """Get the form values.

        Returns:
            Form values.

        """
        values = {}
        for field in self.fields:
            input_widget = self._inputs[field.name]
            values[field.name] = input_widget.get_value()
        return values

    def set_values(
        self,
        values: dict[str, str | int | float | bool | None],
    ) -> None:
        """Set the form values.

        Args:
            values: Form values.

        """
        for field in self.fields:
            if field.name in values:
                input_widget = self._inputs[field.name]
                input_widget.set_value(values[field.name])

    def validate(self) -> bool:
        """Validate the form.

        Returns:
            Whether the form is valid.

        """
        is_valid = True
        for field in self.fields:
            input_widget = self._inputs[field.name]
            if not input_widget.validate(input_widget.value):
                is_valid = False
        return is_valid

    async def on_button_pressed(self, event: Message) -> None:
        """Handle button press events.

        Args:
            event: Button press message.

        """
        button = cast("Button", event.control)
        if button.id == "submit":
            if self.validate():
                self.values = self.get_values()
                await self.emit_event("submit", {"values": self.values})
            else:
                await self.emit_event("error", {"message": "Form validation failed"})
