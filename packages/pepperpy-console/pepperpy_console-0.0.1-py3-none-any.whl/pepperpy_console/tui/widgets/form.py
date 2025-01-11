"""Form widgets for data input."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

import structlog
from textual.containers import Container
from textual.widgets import Button, Label

from .base import PepperWidget
from .input import ValidatedInput

logger = structlog.get_logger(__name__)


@dataclass
class FormField:
    """Form field configuration.

    Attributes:
        name (str): Field name
        label (str): Display label
        type (Type): Field type
        required (bool): Whether field is required
        default (Any): Default value
        validators (List[callable]): Value validators
    """

    name: str
    label: str
    type: Type
    required: bool = True
    default: Any = None
    validators: List[callable] = None

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.validators is None:
            self.validators = []


class PepperForm(PepperWidget, Container):
    """Form widget for data input.

    Attributes:
        fields (List[FormField]): Form fields
        values (Dict[str, Any]): Current field values
    """

    DEFAULT_CSS = """
    PepperForm {
        layout: vertical;
        background: $boost;
        border: tall $primary;
        padding: 2;
        margin: 1;
        min-width: 60;
        max-width: 100;
        height: auto;
    }

    PepperForm Label {
        color: $text;
        margin: 0 1;
        padding: 0;
        text-style: bold;
        width: 100%;
    }

    PepperForm Button {
        margin: 1 1 0 0;
        min-width: 16;
        background: $primary;
        color: $text;
        border: tall $primary;
        height: 3;
    }

    PepperForm Button:hover {
        background: $primary-lighten-2;
        border: tall $accent;
    }

    PepperForm Button.-primary {
        background: $primary;
        color: $text;
    }

    PepperForm Button.-error {
        background: $error;
        color: $text;
    }

    PepperForm Button.-error:hover {
        background: $error-lighten-2;
        border: tall $error;
    }
    """

    def __init__(self, *args: Any, fields: List[FormField], **kwargs: Any) -> None:
        """Initialize the form.

        Args:
            *args: Positional arguments
            fields: Form fields
            **kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.fields = fields
        self.values: Dict[str, Any] = {}
        self._inputs: Dict[str, ValidatedInput] = {}

    def compose(self) -> None:
        """Compose the form layout."""
        for field in self.fields:
            yield Label(field.label + (" *" if field.required else ""))
            input_widget = ValidatedInput(
                type=field.type,
                required=field.required,
                validators=field.validators,
                value=field.default,
                placeholder=f"Enter {field.label.lower()}...",
            )
            self._inputs[field.name] = input_widget
            yield input_widget

        yield Button("Submit", variant="primary", id="submit")
        yield Button("Clear", variant="error", id="clear")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "submit":
            self.submit()
        elif event.button.id == "clear":
            self.clear()

    async def submit(self) -> None:
        """Submit the form."""
        if await self.validate():
            await self.events.emit("submit", self.values)

    def clear(self) -> None:
        """Clear all fields."""
        for input_widget in self._inputs.values():
            input_widget.clear()
        self.values.clear()

    async def validate(self) -> bool:
        """Validate all fields.

        Returns:
            bool: Whether validation passed
        """
        valid = True
        self.values.clear()

        for field in self.fields:
            input_widget = self._inputs[field.name]
            if await input_widget.validate():
                self.values[field.name] = input_widget.typed_value
            else:
                valid = False

        if not valid:
            await self.events.emit("validation_failed", self.values)

        return valid

    def get_value(self, field_name: str) -> Optional[Any]:
        """Get a field value.

        Args:
            field_name: Field name

        Returns:
            Optional[Any]: Field value if found
        """
        return self.values.get(field_name)
