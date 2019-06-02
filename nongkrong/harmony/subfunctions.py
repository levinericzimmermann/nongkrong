import abc

from nongkrong.harmony import functions
from nongkrong.harmony import modes
from nongkrong.harmony import shortwriting as sw

from mu.mel import ji
from mu.mel import mel


class Sign(object):
    _scales = tuple(
        tuple(
            sorted(sw.translate("{0} {1}".format(pre, "17 9 19 5 11 3 13 7 1."), False))
        )
        for pre in (r"!+", r"!-")
    )

    def __init__(self, pitch_conversion_function):
        self.__pcf = pitch_conversion_function

    def __repr__(self) -> str:
        return "SIGN"

    @property
    def scales(self) -> tuple:
        return Sign._scales

    def convert2pitch(self, gender: bool, primes: tuple) -> ji.JIPitch:
        return self.__pcf(gender, primes)

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

        def f(gender, primes):
            def get_pitch():
                prime = primes[pos]
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

        def f(gender, primes):
            def get_pitches():
                def mk_pos(prime):
                    return ji.r(prime, 1)

                def mk_neg(prime):
                    return ji.r(1, prime)

                prime_start, prime_stop = tuple(
                    primes[pos] for pos in (pos_start, pos_stop)
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
        self.__is_close = is_close

    @property
    def is_close(self) -> bool:
        return self.__is_close

    def __repr__(self) -> str:
        return "InterSIGN {0} {1}".format(self.__pos0, self.__pos1)

    @property
    def pos_start(self) -> int:
        return self.__pos0

    @property
    def pos_stop(self) -> int:
        return self.__pos1


class NeutralSign(Sign):
    """Sign representing neutral pitch 1/1"""

    def __init__(self):
        def f(gender, primes):
            return ji.r(1, 1)

        Sign.__init__(self, f)

    def __repr__(self) -> str:
        return "NeutralSIGN"


class EmptySign(Sign):
    """Sign representing empty pitch (rest)"""

    def __init__(self):
        def f(gender, primes):
            return mel.TheEmptyPitch

        Sign.__init__(self, f)

    def __repr__(self) -> str:
        return "EmptySIGN"


TheNeutralSign = NeutralSign()
TheEmptySign = EmptySign()
SINGLE_SIGNS = tuple(SingleSign(i) for i in range(3))
DOUBLE_SIGNS = tuple(DoubleSign(i) for i in range(3))


class SubFunction(abc.ABC):
    def __init__(self, name: str, signifier: Sign, signified: Sign):
        SubFunction.__check_for_valid_signified(signified)
        self.__name = name
        self.__signifier = signifier
        self.__signified = signified

    @staticmethod
    def __check_for_valid_signified(signified) -> None:
        t = type(signified)
        if not t == SingleSign:
            msg = "Invalide type for signified {0} (type: {1}) ".format(signified, t)
            msg = "Signified has to be of type 'SingleSign'."
            raise TypeError(msg)

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

    @abc.abstractproperty
    def nationality(self) -> int:
        raise NotImplementedError


class SubfuncLine(abc.ABC):
    """Container for multiple InterFunction - objects.

    Can be initalised from objects itself or via the
    from_str - method from a string that contains
    InterFunction - names.
    """

    _functions_dict = {}

    def __init__(self, *subfunction: SubFunction):
        self.__subfunctions = subfunction

    def __len__(self) -> int:
        return len(self.__subfunctions)

    def __repr__(self) -> str:
        return str(self.__subfunctions)

    def __getitem__(self, idx) -> SubFunction:
        return self.subfunctions[idx]

    @classmethod
    def from_str(cls, line: str) -> "SubfuncLine":
        funcs = []
        for func in line.split(" "):
            if func:
                try:
                    funcs.append(cls._functions_dict[func])
                except KeyError:
                    msg = "Function {0} doesn't exist.".format(func)
                    raise KeyError(msg)
        return cls(*funcs)

    @property
    def subfunctions(self) -> tuple:
        return self.__subfunctions

    @property
    def signifiers(self) -> tuple:
        return tuple(i.signifier for i in self.subfunctions)

    @property
    def signifieds(self) -> tuple:
        return tuple(i.signified for i in self.subfunctions)

    @property
    def signifieds_position(self) -> tuple:
        return tuple(i.signified.position for i in self.subfunctions)

    @property
    def nationalities(self) -> tuple:
        return tuple(i.nationality for i in self.subfunctions)

    def get_primes(
        mode: modes.Mode, func0: functions.Function, func1: functions.Function
    ) -> tuple:
        raise NotImplementedError

    def __convert2pitch(
        self,
        ls: tuple,
        mode: modes.Mode,
        func0: functions.Function,
        func1: functions.Function,
    ) -> tuple:
        primes = self.get_primes(mode, func0, func1)
        return tuple(s.convert2pitch(mode.gender, primes) for s in ls)

    def convert_signifiers2pitches(
        self, mode, func0: functions.Function, func1: functions.Function
    ) -> tuple:
        return self.__convert2pitch(self.signifiers, mode, func0, func1)

    def convert_signifieds2pitches(
        self, mode, func0: functions.Function, func1: functions.Function
    ) -> tuple:
        return self.__convert2pitch(self.signifieds, mode, func0, func1)
