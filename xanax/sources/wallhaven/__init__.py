"""
Wallhaven source for xanax.

Provides synchronous and asynchronous clients for the Wallhaven API.
"""

from xanax.sources.wallhaven.async_client import AsyncWallhaven
from xanax.sources.wallhaven.client import Wallhaven

__all__ = [
    "Wallhaven",
    "AsyncWallhaven",
]
