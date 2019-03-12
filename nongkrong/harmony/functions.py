from mu.mel import ji

import functools
import operator


class Function(object):
    """Harmonic function, descriped by the two prime numbers it contains.
    """

    def __init__(self, name: str, key, gong: bool) -> None:
        self.__name = name
        self.__key = key
        self.__gong = gong

    def __repr__(self) -> str:
        return self.__name

    @property
    def gong(self) -> bool:
        return self.__gong

    @property
    def identity(self) -> tuple:
        return self.__key.identifier

    def __call__(self, mode) -> ji.JIPitch:
        """Return real pitch depending on the corresponding mode.

        This pitch is in no specific octave yet.
        """
        primes = functools.reduce(operator.mul, self.__key(mode))
        if mode.gender:
            return ji.r(primes, 1)
        else:
            return ji.r(1, primes)


class Identifier(object):
    """
    """

    def __init__(self, p0: str, p1: str) -> None:
        self.__identifier = (p0, p1)

    @property
    def identifier(self) -> tuple:
        return self.__identifier

    def __call__(self, mode) -> tuple:
        """Return the relevant prime numbers from the mode."""
        return tuple(getattr(mode, identity) for identity in self.__identifier)


__FUNC_NAME_AND_IDENTIFIER = (
    ("m", "y", "z"),  # tonica
    ("w", "x", "z"),  # subdominant
    ("o", "x", "y"),  # dominant
    ("n", "N", "z"),
    ("om", "N", "y"),
    ("ow", "N", "x"),
)

for __information in __FUNC_NAME_AND_IDENTIFIER:
    __name, __p0, __p1 = __information
    __identifier = Identifier(__p0, __p1)
    globals().update(
        {
            __name: Function(__name, __identifier, False),
            __name.upper(): Function(__name.upper(), __identifier, True),
        }
    )
