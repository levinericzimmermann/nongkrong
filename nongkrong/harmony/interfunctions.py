from mu.mel import mel
from mu.mel import ji


from nongkrong.harmony import functions
from nongkrong.harmony import shortwriting as sw


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


class Sign(object):
    _scales = tuple(
        tuple(
            sorted(sw.translate("{0} {1}".format(pre, "17 9 19 5 11 3 13 7 1."), False))
        )
        for pre in (r"!+", r"!-")
    )

    def __init__(self, pitch_conversion_function):
        self.__pcf = pitch_conversion_function

    def convert2pitch(self, gender: bool, d: int, l: int, b: int) -> ji.JIPitch:
        return self.__pcf(gender, d, l, b)

    def __repr__(self) -> str:
        return "SIGN"

    @property
    def scales(self) -> tuple:
        return Sign._scales

    @staticmethod
    def test_pos(pos):
        try:
            assert pos in (0, 1, 2)
        except AssertionError:
            msg = "Invalide value {0} for 'pos'. ".format(pos)
            msg += "Argument 'pos' can only be 0, 1 or 2."
            raise ValueError(msg)


class _SingularSign(Sign):
    def __init__(self, octave: int, exponent: int, pos: int):
        Sign.test_pos(pos)

        assert exponent >= 0

        self.__pos = pos

        def f(gender, d, l, b):
            def get_pitch():
                prime = (d, l, b)[pos]
                if gender:
                    return ji.r(prime ** exponent, 1)
                else:
                    return ji.r(1, prime ** exponent)

            if octave > 0:
                oc = ji.r(2 ** octave, 1)
            else:
                oc = ji.r(1, 2 ** abs(octave))

            return get_pitch().normalize(2) + oc

        Sign.__init__(self, f)

    @property
    def position(self) -> int:
        return self.__pos


class SingleSign(_SingularSign):
    """Sign representing pitch composed from one prime.

    'pos' argument declares which of the three present primes
    (d, l or b) shall be used.
    """

    def __init__(self, pos: int):
        _SingularSign.__init__(self, 0, 1, pos)

    def __repr__(self) -> str:
        return "SingleSIGN {0}".format(self.position)


class DoubleSign(_SingularSign):
    """Sign representing pitch composed from one prime ** 2.

    'pos' argument declares which of the three present primes
    (d, l or b) shall be used.
    """

    def __init__(self, pos: int):
        _SingularSign.__init__(self, -1, 2, pos)

    def __repr__(self) -> str:
        return "DoubleSIGN {0}".format(self.position)


class TripleSign(_SingularSign):
    """Sign representing pitch composed from one prime ** 3.

    'pos' argument declares which of the three present primes
    (d, l or b) shall be used.
    """

    def __init__(self, pos: int):
        _SingularSign.__init__(self, -1, 3, pos)


class InterpolationSign(Sign):
    """Sign representing pitch that's interpolating between two pitches.

    This class needs two 'pos' arguments (pos_start and pos_stop).
    'pos' argument declares which of the three present primes
    (d, l or b) shall be used. The first 'pos' argument declares
    the prime from which the interpolation shall start. The second
    'pos' argument declare the prime, to which the first prime
    shall interpolate to.

    If 'is_close' argument is True, the resulting pitch will be
    ordered inbetween prime0 and prime1.
    If 'is_close' argument is False, the resulting pitch will be
    ordered:
        1. RES_Pitch P0_Pitch P1_Pitch
        or 2. P1_Pitch P0_Pitch RES_Pitch
    """

    def __init__(self, pos_start: int, pos_stop: int, is_close: bool):
        assert is_close in (True, False)
        assert pos_start != pos_stop

        Sign.test_pos(pos_start)
        Sign.test_pos(pos_stop)

        def f(gender, d, l, b):
            def get_pitches():
                def mk_pos(prime):
                    return ji.r(prime, 1)

                def mk_neg(prime):
                    return ji.r(1, prime)

                prime_start, prime_stop = tuple(
                    (d, l, b)[pos] for pos in (pos_start, pos_stop)
                )

                if gender:
                    mk_p = mk_pos
                else:
                    mk_p = mk_neg
                return tuple(
                    mk_p(prime).normalize(2) for prime in (prime_start, prime_stop)
                )

            if gender:
                reference_scale = self.scales[0]
            else:
                reference_scale = self.scales[1]

            idx0, idx1 = tuple(reference_scale.index(pitch) for pitch in get_pitches())
            if idx0 > idx1:
                if is_close:
                    return reference_scale[idx0 - 1]
                else:
                    return reference_scale[idx0 + 1]
            else:
                if is_close:
                    return reference_scale[idx0 + 1]
                else:
                    return reference_scale[idx0 - 1]

        Sign.__init__(self, f)

        self.__pos0 = pos_start
        self.__pos1 = pos_stop

    def __repr__(self) -> str:
        return "InterSIGN {0} {1}".format(self.__pos0, self.__pos1)


class NeutralSign(Sign):
    """Sign representing neutral pitch 1/1"""

    def __init__(self):
        def f(gender, d, l, b):
            return ji.r(1, 1)

        Sign.__init__(self, f)

    def __repr__(self) -> str:
        return "NeutralSIGN"


class EmptySign(Sign):
    """Sign representing empty pitch (rest)"""

    def __init__(self):
        def f(gender, d, l, b):
            return mel.TheEmptyPitch

        Sign.__init__(self, f)

    def __repr__(self) -> str:
        return "EmptySIGN"


class InterFunction(object):
    def __init__(self, name: str, signifier: Sign, signified: Sign, nationality: int):
        InterFunction.__check_for_valid_signified(signified)
        InterFunction.__check_for_valid_nationality(signified, nationality)

        self.__name = name
        self.__signifier = signifier
        self.__signified = signified
        self.__nationality = nationality

    @staticmethod
    def __check_for_valid_signified(signified) -> None:
        t = type(signified)
        if not t == SingleSign:
            msg = "Invalide type for signified {0} (type: {1}) ".format(signified, t)
            msg = "Signified has to be of type 'SingleSign'."
            raise TypeError(msg)

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

    def __repr__(self) -> str:
        return self.__name

    @property
    def name(self) -> str:
        return self.__name

    @property
    def signifier(self) -> Sign:
        return self.__signifier

    @property
    def signified(self) -> Sign:
        return self.__signified

    @property
    def nationality(self) -> int:
        return self.__nationality


def __mk_interfunctions():
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

    single_sigs = tuple(SingleSign(p) for p in range(3))
    double_sigs = tuple(DoubleSign(p) for p in range(3))
    neutral_sig = NeutralSign()
    empty_sig = EmptySign()
    to_and_off_ps = ((0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1))
    to_sigs = tuple(InterpolationSign(p0, p1, True) for p0, p1 in to_and_off_ps)
    off_sigs = tuple(InterpolationSign(p0, p1, False) for p0, p1 in to_and_off_ps)

    basic_names = ("d", "ol", "lo", "b")
    to_and_off_names = mk_to_and_off_names(basic_names)

    interfunctions = dic_maker(
        (mk_clear_if, mk_double_if, mk_neutral_if, mk_empty_if, mk_to_if, mk_off_if)
    )
    return interfunctions


INTERFUNCTIONS = __mk_interfunctions()


class InterfuncLine(object):
    """Container for multiple InterFunction - objects.

    Can be initalised from objects itself or via the
    from_str - method from a string that contains
    InterFunction - names.
    """

    def __init__(self, *interfunction: InterFunction):
        self.__interfunctions = interfunction

    def __repr__(self) -> str:
        return str(self.__interfunctions)

    @classmethod
    def from_str(cls, line: str) -> "InterfuncLine":
        ifuncs = []
        for interfunc in line.split(" "):
            if interfunc:
                try:
                    ifuncs.append(INTERFUNCTIONS[interfunc])
                except KeyError:
                    msg = "Interfunction {0} doesn't exist.".format(interfunc)
                    raise KeyError(msg)
        return cls(*ifuncs)

    @property
    def interfunctions(self) -> tuple:
        return self.__interfunctions

    @property
    def signifiers(self) -> tuple:
        return tuple(i.signifier for i in self.interfunctions)

    @property
    def signifieds(self) -> tuple:
        return tuple(i.signified for i in self.interfunctions)

    @property
    def signifieds_position(self) -> tuple:
        return tuple(i.signified.position for i in self.interfunctions)

    @property
    def nationalities(self) -> tuple:
        return tuple(i.nationality for i in self.interfunctions)

    @staticmethod
    def get_dlb(mode, func0: functions.Function, func1: functions.Function) -> tuple:
        def get_primes(f) -> tuple:
            return tuple(f._Function__key(mode))

        if func0 != func1:
            msg = "Both functions are not allowed to be the same!"
            raise ValueError(msg)

        p0, p1 = tuple(get_primes(f) for f in (func0, func1))
        L = tuple(p for p in p0 if p in p1)[0]
        d = tuple(p for p in p0 if p not in p1)[0]
        b = tuple(p for p in p1 if p not in p0)[0]
        return d, L, b

    @staticmethod
    def __convert2pitch(
        ls, mode, func0: functions.Function, func1: functions.Function
    ) -> tuple:
        d, l, b = InterfuncLine.get_dlb(mode, func0, func1)
        return tuple(s.convert2pitch(mode.gender, d, l, b) for s in ls)

    def convert_signifiers2pitches(
        self, mode, func0: functions.Function, func1: functions.Function
    ) -> tuple:
        return InterfuncLine.__convert2pitch(self.signifiers, mode, func0, func1)

    def convert_signifieds2pitches(
        self, mode, func0: functions.Function, func1: functions.Function
    ) -> tuple:
        return InterfuncLine.__convert2pitch(self.signifieds, mode, func0, func1)
