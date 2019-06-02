from nongkrong.harmony import functions
from nongkrong.harmony import subfunctions


"""This module implements harmonic functions called AbodeFunctions.

AbodeFunctions represent harmonic functions, that interpolate between
two equal pitches of the form:

    i * j  ->  i * j

For instance:

    3 * 5  ->  3 * 5
    where: i = 5, j = 3

i and j are not set arbitarily, but the decision which prime number will
get initalised to which variable depend on the particular mode
of the corresponding function. The interval (i -> i * j) will be more
important than the interval (j -> i * j) for the specific mode.

For instance in mode (5+7+3) the function 5 * 7:

    7 will be declared as 'i'
    5 will be declared as 'j'

    because 7/4 to 5 * 7 will return the interval 8/5
    which is the most imporant function in the mode 5+7+3.


The naming convention for different AbodeFunction objects
is equal to the naming convention of InterFunction objects,
where

    Basic functions:
        i -> AbodeFunction with Signifier 'i' and Signified 'i'
        j -> AbodeFunction with Signifier 'j' and Signified 'j'

    And additional more complex functions.
    Their Signified is the same as in the refering
    basic function.

        i2 -> i ** 2
        i0 -> 1/1
        i00 -> mel.TheEmptyPitch
        i_to_j ->
            Pitch with one prime that's (from frequency) close
            to i and going in direction of j.
        i_off_j ->
            Pitch with one prime that's (from frequency) close
            to i and going in different direction than j.
"""


class AbodeFunction(subfunctions.SubFunction):
    def __init__(
        self, name: str, signifier: subfunctions.Sign, signified: subfunctions.Sign
    ):
        AbodeFunction.__check_for_valid_sign(signifier)
        AbodeFunction.__check_for_valid_sign(signified)

        subfunctions.SubFunction.__init__(self, name, signifier, signified)

    @staticmethod
    def __check_for_valid_sign(sign):
        is_valid = True
        if isinstance(sign, subfunctions._SingularSign):
            try:
                assert sign.position in (0, 1)
            except AssertionError:
                is_valid = False
        elif isinstance(sign, subfunctions.InterpolationSign):
            try:
                tests = tuple(pos in (0, 1) for pos in (sign.pos_start, sign.pos_stop))
                assert all(tests)
            except AssertionError:
                is_valid = False

        if not is_valid:
            msg = "Only position 0 - 1 is allowed for Signs in AbodeFunction!"
            raise ValueError(msg)

    @property
    def nationality(self) -> int:
        return 0


def _mk_abodefunctions() -> dict:
    def mk_functions_for_n(pos, name, other_pos, other_name):
        def mk_name_and_signifier():
            return {
                name: subfunctions.SINGLE_SIGNS[pos],
                "{0}2".format(name): subfunctions.DOUBLE_SIGNS[pos],
                "{0}0".format(name): subfunctions.TheNeutralSign,
                "{0}00".format(name): subfunctions.TheEmptySign,
                "{0}_to_{1}".format(name, other_name): subfunctions.InterpolationSign(
                    pos, other_pos, True
                ),
                "{0}_off_{1}".format(name, other_name): subfunctions.InterpolationSign(
                    pos, other_pos, False
                ),
            }

        def mk_signified():
            return subfunctions.SINGLE_SIGNS[pos]

        name_and_sig = mk_name_and_signifier()
        signified = mk_signified()
        return {
            name: AbodeFunction(name, name_and_sig[name], signified)
            for name in name_and_sig
        }

    names = ((0, "i"), (1, "j"))
    dicts = (
        mk_functions_for_n(d0[0], d0[1], d1[0], d1[1])
        for d0, d1 in zip(names, reversed(names))
    )
    final_dic = {}
    for d in dicts:
        final_dic.update(d)
    return final_dic


ABODEFUNCTIONS = _mk_abodefunctions()


class AbodefuncLine(subfunctions.SubfuncLine):
    """Container for multiple AbodeFunction - objects.

    Can be initalised from objects itself or via the
    from_str - method from a string that contains
    AbodeFunction - names.
    """

    _functions_dict = ABODEFUNCTIONS

    @staticmethod
    def get_primes(mode, func: functions.Function, func1: functions.Function) -> tuple:
        def get_primes(f) -> tuple:
            return tuple(f._Function__key(mode))

        primes = get_primes(func)
        mode_primes = (mode.x, mode.y, mode.z, mode.U)
        prime_idx0 = mode_primes.index(primes[0])
        prime_idx1 = mode_primes.index(primes[1])
        if prime_idx1 < prime_idx0:
            return primes
        else:
            return tuple(reversed(primes))
