from nongkrong.harmony import subfunctions
from nongkrong.harmony import functions


"""This module implements harmonic functions called InterFunctions.

InterFunctions represent harmonic functions, that interpolate between
two pitches of the form:

    d * l  ->  l * b

For instance:

    3 * 5  ->  5 * 7
    where: d = 3, l = 5, b = 7

    or

    3 * 9  ->  9 * 5
    where: d = 3, l = 9, b = 5

Condition:

    d, l and b have to be unique numbers (d != l, d != b, b != l).

While the actual pitch of an InterFunction can vary widely,
the symbolic meaning of this pitch always refers to either d, l or b.
To represent the difference between actual pitch and symbolic
meaning, InterFunction - objects contain one Signifier and
one Signified. Signifier is the real pitch, that will be played,
while Signified represents a simple pitch containing only
one Prime number, that's either d, l or b.

Additionaly InterFunctions contain the nationality - argument,
that's either 0 or 1. The nationality is specifing, if the
InterFunction rather belongs to the first function (d * l)
or more to the second function (b * l).
For a Signified that is equal to d, nationality has to be 0.
For a Signified that is equal to b, nationality has to be 1.
For a Signified that is equal to l, nationality could be 0 or 1.

The interfunctions - module already implements all relevant InterFunctions.
They can be found in the interfunctions.INTERFUNCTIONS dict.

Their naming convention:

    Basic functions:

        d -> InterFunction with Signifier 'd' and Signified 'd'
        ol -> InterFunction with Signifier 'l' and Signified 'd'
        lo -> InterFunction with Signifier 'l' and Signified 'b'
        b -> InterFunction with Signifier 'b' and Signified 'b'

    For every basic function, there are additional more complex
    functions. Their Signified is the same as in the refering
    basic function. Here they are represented with basic function d:

        d2 -> d ** 2
        d0 -> 1/1
        d00 -> mel.TheEmptyPitch
        d_to_b ->
            Pitch with one prime that's (from frequency) close
            to d and going in direction of b.
        d_off_b ->
            Pitch with one prime that's (from frequency) close
            to d and going in different direction than b.
        d_to_l ->
            Same with l
        d_off_l ->
            Same with l


Those InterFunctions are musically supposed to be represented
by two instruments:
    1. Siter Barung
    2. Siter Panerus
"""


class InterFunction(subfunctions.SubFunction):
    def __init__(
        self,
        name: str,
        signifier: subfunctions.Sign,
        signified: subfunctions.Sign,
        nationality: int,
    ):
        InterFunction.__check_for_valid_nationality(signified, nationality)

        self.__nationality = nationality
        subfunctions.SubFunction.__init__(self, name, signifier, signified)

    @staticmethod
    def __check_for_valid_nationality(signified, nationality) -> None:
        try:
            assert nationality in (0, 1)
        except AssertionError:
            msg = "Invalide Value {0} for 'nationality' - attribute. ".format(
                nationality
            )
            msg += "Can only be 0 or 1."
            raise ValueError(msg)

        position = signified.position
        bad_cases = (
            position == 0 and nationality == 1,
            position == 2 and nationality == 0,
        )
        if any(bad_cases):
            msg = "Invalide combination of position {0} and nationality {1}".format(
                position, nationality
            )
            msg += "For position 0 and position 2 "
            msg += "only nationality 0 or 1 are allowed."
            raise ValueError(msg)

    @property
    def nationality(self) -> int:
        return self.__nationality


def __mk_interfunctions() -> dict:
    def mk_interfunction_dict(data):
        return {d[0]: InterFunction(*d) for d in data}

    def mk_clear_if() -> dict:
        return mk_interfunction_dict(
            (
                (basic_names[0], single_sigs[0], single_sigs[0], 0),
                (basic_names[1], single_sigs[1], single_sigs[1], 0),
                (basic_names[2], single_sigs[1], single_sigs[1], 1),
                (basic_names[3], single_sigs[2], single_sigs[2], 1),
            )
        )

    def mk_double_if() -> dict:
        double_names = tuple("{0}2".format(n) for n in basic_names)
        return mk_interfunction_dict(
            (
                (double_names[0], double_sigs[0], single_sigs[0], 0),
                (double_names[1], double_sigs[1], single_sigs[1], 0),
                (double_names[2], double_sigs[1], single_sigs[1], 1),
                (double_names[3], double_sigs[2], single_sigs[2], 1),
            )
        )

    def mk_neutral_if() -> dict:
        neutral_names = tuple("{0}0".format(n) for n in basic_names)
        return mk_interfunction_dict(
            (
                (neutral_names[0], neutral_sig, single_sigs[0], 0),
                (neutral_names[1], neutral_sig, single_sigs[1], 0),
                (neutral_names[2], neutral_sig, single_sigs[1], 1),
                (neutral_names[3], neutral_sig, single_sigs[2], 1),
            )
        )

    def mk_empty_if() -> dict:
        empty_names = tuple("{0}00".format(n) for n in basic_names)
        return mk_interfunction_dict(
            (
                (empty_names[0], empty_sig, single_sigs[0], 0),
                (empty_names[1], empty_sig, single_sigs[1], 0),
                (empty_names[2], empty_sig, single_sigs[1], 1),
                (empty_names[3], empty_sig, single_sigs[2], 1),
            )
        )

    def mk_to_if() -> dict:
        to_names = tuple("{0}_to_{1}".format(n0, n1) for n0, n1 in to_and_off_names)
        return mk_interfunction_dict(
            (
                (to_names[0], to_sigs[0], single_sigs[0], 0),
                (to_names[1], to_sigs[1], single_sigs[0], 0),
                (to_names[2], to_sigs[2], single_sigs[1], 0),
                (to_names[3], to_sigs[3], single_sigs[1], 0),
                (to_names[4], to_sigs[2], single_sigs[1], 1),
                (to_names[5], to_sigs[3], single_sigs[1], 1),
                (to_names[6], to_sigs[4], single_sigs[2], 1),
                (to_names[7], to_sigs[5], single_sigs[2], 1),
            )
        )

    def mk_off_if() -> dict:
        off_names = tuple("{0}_off_{1}".format(n0, n1) for n0, n1 in to_and_off_names)
        return mk_interfunction_dict(
            (
                (off_names[0], off_sigs[0], single_sigs[0], 0),
                (off_names[1], off_sigs[1], single_sigs[0], 0),
                (off_names[2], off_sigs[2], single_sigs[1], 0),
                (off_names[3], off_sigs[3], single_sigs[1], 0),
                (off_names[4], off_sigs[2], single_sigs[1], 1),
                (off_names[5], off_sigs[3], single_sigs[1], 1),
                (off_names[6], off_sigs[4], single_sigs[2], 1),
                (off_names[7], off_sigs[5], single_sigs[2], 1),
            )
        )

    def dic_maker(func) -> dict:
        di = {}
        for fu in func:
            di.update(fu())
        return di

    def mk_to_and_off_names(basic_names) -> tuple:
        to_and_off_ps = ((0, 1), (0, 3), (1, 0), (1, 3), (2, 0), (2, 3), (3, 0), (3, 1))
        names = []
        for idx0, idx1 in to_and_off_ps:
            name0 = basic_names[idx0]
            if idx1 == 1:
                name1 = "l"
            else:
                name1 = basic_names[idx1]
            names.append((name0, name1))
        return names

    single_sigs = subfunctions.SINGLE_SIGNS
    double_sigs = subfunctions.DOUBLE_SIGNS
    neutral_sig = subfunctions.TheNeutralSign
    empty_sig = subfunctions.TheEmptySign
    to_and_off_ps = ((0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1))
    to_sigs = tuple(
        subfunctions.InterpolationSign(p0, p1, True) for p0, p1 in to_and_off_ps
    )
    off_sigs = tuple(
        subfunctions.InterpolationSign(p0, p1, False) for p0, p1 in to_and_off_ps
    )

    basic_names = ("d", "ol", "lo", "b")
    to_and_off_names = mk_to_and_off_names(basic_names)

    interfunctions = dic_maker(
        (mk_clear_if, mk_double_if, mk_neutral_if, mk_empty_if, mk_to_if, mk_off_if)
    )
    return interfunctions


INTERFUNCTIONS = __mk_interfunctions()


class InterfuncLine(subfunctions.SubfuncLine):
    """Container for multiple InterFunction - objects.

    Can be initalised from objects itself or via the
    from_str - method from a string that contains
    InterFunction - names.
    """

    _functions_dict = INTERFUNCTIONS

    @staticmethod
    def get_primes(mode, func0: functions.Function, func1: functions.Function) -> tuple:
        def get_primes(f) -> tuple:
            return tuple(f._Function__key(mode))

        if func0 == func1:
            msg = "Func0: {0}, Func1: {1}. ".format(func0, func1)
            msg += "Both functions are not allowed to be the same! "
            msg += "For two equal functions the Interpolation has to be "
            msg += "described with the harmony.abodefunctions module."
            raise ValueError(msg)

        p0, p1 = tuple(get_primes(f) for f in (func0, func1))
        L = tuple(p for p in p0 if p in p1)[0]
        d = tuple(p for p in p0 if p not in p1)[0]
        b = tuple(p for p in p1 if p not in p0)[0]
        return d, L, b
