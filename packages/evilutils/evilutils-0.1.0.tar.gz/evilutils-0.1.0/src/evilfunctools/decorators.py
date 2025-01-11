from collections.abc import Callable
from functools import partial
from typing import ParamSpec, TypeVar

from .compose import compose

__all__ = ["immediate", "map_result"]

P = ParamSpec("P")
RT = TypeVar("RT")
MT = TypeVar("MT")

TT = TypeVar("TT", bound=type)


def immediate(func: Callable[[], RT]) -> RT:
    """Immediately evaluate the given function, returning its output.

    >>> @immediate
    ... def VALUES():
    ...     return (0, 1)
    >>>
    >>> VALUES
    (0, 1)
    """
    return func()


def map_result(
    mapper: Callable[[RT], MT],
) -> Callable[[Callable[P, RT]], Callable[P, MT]]:
    """Map the returned value of a function using another function.

    This is especially designed with generators in mind, though one
    could easily find other uses.

    >>> @map_result(tuple)
    ... def __generate_values(a: int):
    ...     yield from (a, 1)
    >>>
    >>> __generate_values(0)
    (0, 1)
    """
    return partial(compose, mapper)
