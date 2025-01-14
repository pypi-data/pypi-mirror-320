# Exordium

Exordium is a custom VSCode-style logger for Python, providing colorful and informative log messages.

## Installation

You can install Exordium using pip:

```
pip install exordium
```

Or directly from the GitHub repository:

```
pip install git+https://github.com/ExoticCitron/exordium.git
```

## Usage

Here's a simple example of how to use Exordium:

```python
from exordium import get_logger

logger = get_logger(__name__)

logger.info("This is an info message")
logger.debug("This is a debug message")
logger.warning("This is a warning message")
logger.success("This is a success message")
logger.error("This is an error message")
logger.critical("This is a critical message")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
