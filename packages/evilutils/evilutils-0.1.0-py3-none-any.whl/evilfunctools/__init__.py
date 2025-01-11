"""Extensions upon the `functools` library."""

from functools import cache, cached_property, partial, partialmethod, wraps

from .compose import compose
from .decorators import immediate, map_result

__all__ = [
    "partial",
    "partialmethod",
    "cache",
    "cached_property",
    "compose",
    "wraps",
    "immediate",
    "map_result",
]
