# PepperPy Console

[![PyPI version](https://badge.fury.io/py/pepperpy-console.svg)](https://badge.fury.io/py/pepperpy-console)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/pepperpy-console/badge/?version=latest)](https://pepperpy-console.readthedocs.io/en/latest/?badge=latest)

A powerful Python library for building text-based user interfaces (TUI) with a focus on extensibility and ease of use.

## Features

- 🎨 **Theme Support**: Customizable appearance with built-in themes
- 🔌 **Plugin System**: Easy to extend with custom plugins
- 🎯 **CLI Framework**: Robust command-line interface system
- 📱 **TUI Components**: Rich set of text user interface widgets
- 🔄 **Event System**: Comprehensive event handling
- 🔒 **Type Safety**: Full type hints support
- ⚡ **Async Support**: Built with asyncio for modern Python applications

## Installation

```bash
pip install pepperpy-console
```

## Quick Start

```python
from pepperpy_console import PepperApp, PepperScreen, Static

class WelcomeScreen(PepperScreen):
    async def compose(self):
        yield Static("Welcome to PepperPy Console!")

class MyApp(PepperApp):
    async def on_mount(self):
        await self.push_screen(WelcomeScreen())

if __name__ == "__main__":
    app = MyApp()
    app.run()
```

## Documentation

Visit our [documentation](https://pepperpy-console.readthedocs.io/) for:

- [CLI System Guide](https://pepperpy-console.readthedocs.io/en/latest/cli/)
- [TUI Framework Guide](https://pepperpy-console.readthedocs.io/en/latest/tui/)
- [Theme System Guide](https://pepperpy-console.readthedocs.io/en/latest/themes/)
- [Examples](https://pepperpy-console.readthedocs.io/en/latest/examples/)
- [API Reference](https://pepperpy-console.readthedocs.io/en/latest/api/)

## Examples

### CLI Application

```python
from pepperpy_console import PepperApp, Command

class CLIApp(PepperApp):
    def __init__(self):
        super().__init__()
        self.setup_commands()

    def setup_commands(self):
        async def greet(name: str):
            return f"Hello, {name}!"

        self.commands.add_command(Command(
            name="greet",
            callback=greet,
            description="Greet someone"
        ))

app = CLIApp()
app.run()
```

### Data Table

```python
from pepperpy_console import (
    PepperApp,
    PepperScreen,
    PepperTable,
    Column
)

class DataScreen(PepperScreen):
    def __init__(self):
        super().__init__()
        self.table = PepperTable()

    def setup_table(self):
        self.table.add_column(Column("ID"))
        self.table.add_column(Column("Name"))
        self.table.add_row("1", "Item 1")

    async def compose(self):
        self.setup_table()
        yield self.table

app = PepperApp()
app.push_screen(DataScreen())
app.run()
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pepperpy-console.git
cd pepperpy-console
```

2. Install dependencies:
```bash
poetry install
```

3. Run tests:
```bash
poetry run pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Textual](https://github.com/Textualize/textual)
- Inspired by modern Python libraries and frameworks

## Support

- 📖 [Documentation](https://pepperpy-console.readthedocs.io/)
- 💬 [Discord Community](https://discord.gg/pepperpy)
- 📝 [GitHub Issues](https://github.com/yourusername/pepperpy-console/issues)
- 📧 [Email Support](mailto:support@pepperpy.com)
