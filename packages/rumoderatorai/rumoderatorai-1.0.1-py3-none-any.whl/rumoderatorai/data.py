from typing import Final

import platform

import aiohttp


__version__ = "1.0.1"

HEADERS: Final[dict[str, str]] = {
    "User-Agent": f"RuModeratorAI Python Library/{__version__} (Python {platform.python_version()}) via aiohttp/{aiohttp.__version__}"
}
