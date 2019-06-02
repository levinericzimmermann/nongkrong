from mu.mel import ji

import functools
import operator

"""This module implements harmonic functions.

Those harmonic functions are unlike traditional harmonic theory
not connected to a specific chord, but rather to a specific pitch.
Each mode has 3 main functions / pitches. Those are all pitches that can
be found in the GONG - note of the corresponding mode.
For the mode x*y*z, the 3 main functions are:
    o: x*y
    w: x*z
    m: y*z
Additionaly every outer function, that's not part of the mode, is defined as:
    n: U*z (connection between w and m)
    ow: U*x (connection between o and w)
    om: U*y (connection between o and m)
U is the fourth prime number, that is not part of the current mode.

Each of the inner functions (o, w, m) can be played simultanously with the GONG.
In this case they are written in upper letters (O, W, M).

Additionaly every function has two sidefunctions. Those sidefunctions
have the form a/b or b/a. They are named after their mother function
plus the prime number, that remains stable.
For instance:
    o: x*y
    ox: x/y
    oy: y/x
"""


class Function(object):
    """Harmonic function, descriped by the two prime numbers it contains.

    A harmonic function can be played with or without the gong.
    Every harmonic function has two sidefunctions.
    """

    def __init__(self, name: str, key, gong: bool) -> None:
        self.__name = name
        self.__key = key
        self.__gong = gong

    def __repr__(self) -> str:
        return self.__name

    def __eq__(self, other) -> bool:
        try:
            tests = (
                self.gong == other.gong,
                self.__key == other.__key,
                type(self) == type(other),
            )
            return all(tests)
        except AttributeError:
            return False

    def __hash__(self) -> int:
        return hash(self.identity)

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


class SideFunction(Function):
    def __init__(self, name: str, key) -> None:
        Function.__init__(self, name, key, False)

    def __call__(self, mode):
        """Return real pitch depending on the corresponding mode.

        This pitch is in no specific octave yet.
        """
        primes = self.__key(mode)
        if not mode.gender:
            primes = tuple(reversed(primes))
        return ji.r(primes[0], primes[1])


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

    def __eq__(self, other) -> bool:
        try:
            return self.identifier == other.identifier
        except AttributeError:
            return False


def __init_functions():
    func_name_and_identifier = (
        ("m", "y", "z"),  # tonica
        ("w", "x", "z"),  # subdominant
        ("o", "x", "y"),  # dominant
        ("n", "U", "z"),
        ("om", "U", "y"),
        ("ow", "U", "x"),
    )

    functions = {}

    for information in func_name_and_identifier:
        name, p0, p1 = information
        name_sf0 = name + p0
        name_sf1 = name + p1
        identifier = Identifier(p0, p1)
        identifier_sf1 = Identifier(p1, p0)
        to_update = {
            name: Function(name, identifier, False),
            name_sf0: SideFunction(name_sf0, identifier),
            name_sf1: SideFunction(name_sf1, identifier_sf1),
        }
        if name in ("m", "w", "o"):
            to_update.update(
                {name.upper(): Function(name.upper(), identifier, True)}
            )
        functions.update(to_update)

    return functions


FUNCTIONS = __init_functions()
