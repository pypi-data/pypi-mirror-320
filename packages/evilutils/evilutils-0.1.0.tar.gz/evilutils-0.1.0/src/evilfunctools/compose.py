from collections.abc import Callable
from functools import partial, wraps
from typing import overload

__all__ = ["compose"]

type Fn[_AT, _RT] = Callable[[_AT], _RT]

type PartialComposition[**P, RT, MT] = Callable[[Callable[P, RT]], Callable[P, MT]]
type AnyComposition[**P, RT, MT] = Callable[P, MT] | PartialComposition[P, RT, MT]


@overload
def compose[**P, RT, MT](F: Fn[RT, MT]) -> PartialComposition[P, RT, MT]:
    """
    A partial composition of F. This overload can be used as a decorator.
    """
    ...


@overload
def compose[**P, RT, MT](F: Fn[RT, MT], G: Callable[P, RT]) -> Callable[P, MT]:
    """
    A composition `F o G`.

    See also: `Function composition`_

    .. Function composition: https://en.wikipedia.org/wiki/Function_composition_(computer_science)
    """
    ...


def compose[**P, RT, MT](
    F: Fn[RT, MT], G: Callable[P, RT] | None = None
) -> AnyComposition[P, RT, MT]:
    """
    >>> double = lambda n: n * 2
    >>> @compose(double)
    ... def two() -> int:
    ...     return 1
    >>>
    >>> two()
    2

    >>> plus_one = lambda n: n + 1
    >>> plus_two = compose(plus_one, plus_one)
    >>> plus_two(2)
    4
    """

    if G is None:
        return partial(compose, F)

    @wraps(G)
    def composition(*args: P.args, **kwargs: P.kwargs) -> MT:
        return F(G(*args, **kwargs))

    return composition
