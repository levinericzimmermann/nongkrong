from nongkrong.harmony import shortwriting as sw
from nongkrong.algorithms.forms import lancaran_inter2polation

from mu.mel import ji
from mu.sco import old


import functools
import itertools
import operator
import random as _KECAPI_RANDOM

_KECAPI_RANDOM.seed(10)


class KecapiPattern(lancaran_inter2polation.Pattern):
    """Decodex:
        a is main prime
        b is side prime
        C and D are (3, 5, 7) but a != C and a != D and b != C
        c and d are (3, 5, 7) but b != C and b != D and a != c

        A is main prime, but if main prime == 9, A == 3
        B is side prime, but if side prime == 9, B == 3

    Example 3/7 in positive mode 3+5+7:
        a -> 3
        A -> 3

        C -> 5
        D -> 7

        b -> 7
        B -> 7

        c -> 5
        d -> 3

    Example 9/7 in positive mode 9+5+7:
        a -> 9
        A -> 3

        C -> 5
        D -> 7

        b -> 7
        B -> 7

        c -> 5
        d -> 3
    """

    transformed_main_prime = "A"
    transformed_side_prime = "B"
    not_current_main_prime0 = "C"
    not_current_main_prime1 = "D"
    not_current_side_prime0 = "c"
    not_current_side_prime1 = "d"

    def __call__(self, gender: bool, main_prime: int, side_prime: int) -> old.JICadence:
        if not main_prime:
            main_prime = 3
        if not side_prime:
            side_prime = 5

        not_current_main_primes = tuple(p for p in (3, 5, 7) if p != main_prime)
        if len(not_current_main_primes) == 3:
            not_current_main_primes = (5, 7)

        if not_current_main_primes[0] == side_prime:
            not_current_main_primes = tuple(reversed(not_current_main_primes))

        not_current_side_primes = tuple(p for p in (3, 5, 7) if p != side_prime)
        if len(not_current_side_primes) == 3:
            not_current_side_primes = (5, 7)

        if not_current_side_primes[0] == main_prime:
            not_current_side_primes = tuple(reversed(not_current_side_primes))

        if main_prime == 9:
            tranformed_mp = 3
        else:
            tranformed_mp = main_prime

        if side_prime == 9:
            tranformed_sp = 3
        else:
            tranformed_sp = side_prime

        pitches = sw.translate(
            self.line,
            decodex={
                self.main: str(main_prime),
                self.side: str(side_prime),
                self.not_current_main_prime0: str(not_current_main_primes[0]),
                self.not_current_main_prime1: str(not_current_main_primes[1]),
                self.not_current_side_prime0: str(not_current_side_primes[0]),
                self.not_current_side_prime1: str(not_current_side_primes[1]),
                self.transformed_main_prime: str(tranformed_mp),
                self.transformed_side_prime: str(tranformed_sp),
            },
            inverse=not gender,
        )
        return old.JICadence([old.Chord(h, r) for h, r in zip(pitches, self.rhythms)])


_plus_pattern = {
    "silent": KecapiPattern("x x", (0.5, 0.5)),
    "static_moveless": KecapiPattern("x a", (0.5, 0.5)),
    "static_stable": KecapiPattern("a+b-. a", (0.5, 0.5)),
    "static_stable_predict": KecapiPattern("(a+b-. a) x", (0.5, 0.5)),
    "static_stable_silent": KecapiPattern("a+b-. x", (0.5, 0.5)),
    "static_unstable": KecapiPattern("a+C-D-.. x", (0.5, 0.5)),
    "static_unstable_variation": KecapiPattern("a+C-D-.. a+b-.", (0.5, 0.5)),
    "static_unstable_easy": KecapiPattern("a+b-. x", (0.5, 0.5)),
    "alternating_stable": KecapiPattern("a+b-. a", (0.5, 0.5)),
    "alternating_stable_silent": KecapiPattern("a+b-. x", (0.5, 0.5)),
    "alternating_unstable": KecapiPattern("X a+b-.", (0.5, 0.5)),
    "to_gong_first": KecapiPattern("x a+b-.", (0.5, 0.5)),
    "to_gong_second": KecapiPattern("a+ a+c-.", (0.5, 0.5)),
    "to_gong_middle0": KecapiPattern("x b+", (0.5, 0.5)),
    "to_gong_middle1": KecapiPattern("x a+", (0.5, 0.5)),
    "to_gong_last": KecapiPattern("X", (1,)),
    "aba": KecapiPattern(
        "x a+b-. a+C-. b+C-. b+a-. b+C-. a+C-. a+b-.",
        (0.5, 0.75, 0.25, 0.5, 0.5, 0.75, 0.25, 0.5),
    ),
    "abba": KecapiPattern(
        "x a+b-. a+C-. b+C-. b+a-. b+ b+a-. b+C-. a+C-. a+b-.",
        (0.5, 0.5, 0.75, 0.25, 0.5, 0.5, 0.75, 0.25, 0.5, 0.5),
    ),
    "abbba": KecapiPattern(
        "x a+b-. a+C-. b+C-. b+a-. b+ b+a-. b+C-. a+C-. a+b-. a+",
        (1, 0.75, 0.25, 0.75, 0.25, 0.75, 0.25, 0.75, 0.25, 0.5, 0.5),
    ),
    "abbbba": KecapiPattern(
        "x a+b-. a+C-. b+C-. b+a-. b+ b+C-. b+ b+a-. b+C-. a+C-. a+b-. a+",
        (1, 0.75, 0.25, 0.75, 0.25, 0.75, 0.25, 0.75, 0.25, 0.75, 0.25, 0.5, 0.5),
    ),
}

_minus_pattern = {
    "silent": KecapiPattern("x x", (0.5, 0.5)),
    "static_moveless": KecapiPattern("x x", (0.5, 0.5)),
    "static_stable": KecapiPattern("b-.. x", (0.5, 0.5)),
    "static_stable_predict": KecapiPattern("b-.. x", (0.5, 0.5)),
    "static_stable_silent": KecapiPattern("b-.. x", (0.5, 0.5)),
    "static_unstable": KecapiPattern("a+b-. c+d+b-", (0.5, 0.5)),
    "static_unstable_variation": KecapiPattern("x c+d+b-", (0.5, 0.5)),
    "static_unstable_easy": KecapiPattern("b-.. x", (0.5, 0.5)),
    "alternating_stable": KecapiPattern("b-.. x", (0.5, 0.5)),
    "alternating_stable_silent": KecapiPattern("b-.. x", (0.5, 0.5)),
    "alternating_unstable": KecapiPattern("a+b-. c+d+b-", (0.5, 0.5)),
    "to_gong_first": KecapiPattern("x b-..", (0.5, 0.5)),
    "to_gong_second": KecapiPattern("x c-..", (0.5, 0.5)),
    "to_gong_middle0": KecapiPattern("A+B+c- c-..", (0.5, 0.5)),
    "to_gong_middle1": KecapiPattern("A+B+c- c-..", (0.5, 0.5)),
    "to_gong_last": KecapiPattern("A+B+c- A+B+c-", (0.5, 0.5)),
    "aba": KecapiPattern("x b-.. a+C-. C-.. b-.. C-.. b-..", (0.5, 0.5, 0.5, 0.5, 0.5, 1, 0.5)),
    "abba": KecapiPattern("x b-.. C-.. a-.. a-.. C-.. b-..", (0.5, 1, 0.5, 1, 0.5, 1, 0.5)),
    "abbba": KecapiPattern(
        "x b-.. C-.. a-.. a-.. C-.. b-..", (0.5, 1, 1, 1, 1, 1, 0.5)
    ),
    "abbbba": KecapiPattern(
        "x b-.. C-.. a-.. C-.. a-.. C-.. b-..", (0.5, 1, 1, 1, 1, 1, 1, 0.5)
    ),
}


class LancaranStyle(lancaran_inter2polation.LancaranStyleForInstrument):
    def create_cadence(
        self,
        stresses: tuple,
        does_siter_play: tuple,
        gender: bool,
        previous_signified: int,
        current_signified: int,
        following_signified: int,
        previous_side_prime: int,
        current_side_prime: int,
        following_side_prime: int,
    ) -> old.JICadence:
        chord0 = old.Chord(ji.JIHarmony([]), 0.5)

        stresses += (True,)
        does_siter_play += (False,)

        pattern = self.detect_pattern(
            stresses,
            does_siter_play,
            gender,
            previous_signified,
            current_signified,
            following_signified,
            previous_side_prime,
            current_side_prime,
            following_side_prime,
        )

        final_cadence = [chord0]
        for idx, pat in enumerate(pattern):
            pat = list(pat)
            if idx + 1 == len(pattern):
                final_cadence += pat[:1]
            else:
                final_cadence += pat
        return old.JICadence(final_cadence)


class StaticLancaranStyle_Full(lancaran_inter2polation.LancaranStyleForInstrument):
    apply_with_header_if_header_exist = True

    @staticmethod
    def divide_stresses(stresses) -> tuple:
        divided = []
        stresses_group = []
        for stress in stresses:
            stresses_group.append(stress)
            if stress:
                divided.append(tuple(stresses_group))
                stresses_group = []
        if stresses_group:
            divided.append(tuple(stresses_group))
        return tuple(divided)

    @staticmethod
    def convert_resolution_pattern(
        gender: bool,
        main_prime: int,
        side_prime: int,
        pattern: tuple,
        with_header: bool,
        with_tail: bool,
    ):
        header, body, tail = pattern

        cadence = old.JICadence([])

        if with_header:
            cadence += header(gender, main_prime, side_prime)

        cadence += body(gender, main_prime, side_prime)

        if with_tail:
            cadence += tail(gender, main_prime, side_prime)

        return cadence

    @staticmethod
    def convert_modulation_pattern(
        gender: bool,
        main_prime: int,
        side_prime: int,
        next_main_prime: int,
        next_side_prime: int,
        pattern: tuple,
        with_header: bool,
    ):
        header, body, tail = pattern

        cadence = old.JICadence([])

        if with_header:
            cadence += header(gender, main_prime, side_prime)

        cadence += body(gender, main_prime, side_prime)
        cadence += tail(gender, next_main_prime, next_side_prime)

        return cadence

    def create_cadence(
        self,
        stresses: tuple,
        does_siter_play: tuple,
        gender: bool,
        previous_signified: int,
        current_signified: int,
        following_signified: int,
        previous_side_prime: int,
        current_side_prime: int,
        following_side_prime: int,
    ) -> old.JICadence:

        if self.apply_with_header_if_header_exist:
            cadence = old.JICadence([])
        else:
            cadence = old.JICadence([old.Chord(ji.JIHarmony([]), 0.5)])

        divided_stresses = self.divide_stresses(stresses)
        amount_divisions = len(divided_stresses)
        is_with_modulation = current_signified != following_signified
        for idx, division in enumerate(divided_stresses):
            if idx == 0 and self.apply_with_header_if_header_exist:
                add_header = True
            else:
                add_header = False

            amount_stresses = len(division)
            is_with_resolution = not all(tuple(not s for s in division))
            conditions_for_modulation = (
                is_with_modulation,
                not is_with_resolution,
                idx + 1 == amount_divisions,
            )
            if all(conditions_for_modulation):
                pattern = self.pattern[1][amount_stresses]
                cadence += self.convert_modulation_pattern(
                    gender,
                    current_signified,
                    current_side_prime,
                    following_signified,
                    following_side_prime,
                    pattern,
                    add_header,
                )
            else:
                pattern_idx = int(amount_stresses)
                if is_with_resolution:
                    add_tail = True
                else:
                    pattern_idx += 1
                    add_tail = False

                pattern = self.pattern[0][pattern_idx]
                cadence += self.convert_resolution_pattern(
                    gender,
                    current_signified,
                    current_side_prime,
                    pattern,
                    add_header,
                    add_tail,
                )

        return old.JICadence(cadence)


class Plus_StaticLancaranStyle_Full_WithHeader(StaticLancaranStyle_Full):
    @property
    def pattern(self) -> dict:
        resolution_pattern = {
            2: (
                KecapiPattern("a+", (0.5,)),
                KecapiPattern("a+C-D-.. a+b-.", (1, 0.5)),
                KecapiPattern("a+", (0.5,)),
            ),
            3: (
                KecapiPattern("a+", (0.5,)),
                KecapiPattern("a+b-. a+C-. a+ c+b-. c+ x a+b-.", (0.25, 0.25, 0.5, 0.5, 0.5, 0.25, 0.25)),
                KecapiPattern("a+", (0.5,)),
            ),
            4: (
                KecapiPattern("a+", (0.5,)),
                KecapiPattern(
                    "x a+b-. a+ a+C-D-.. a+ a+C-. a+C-D-.. a+b-. a+ (a+ a+b-.)",
                    (0.5, 0.25, 0.25, 0.5, 0.25, 0.25, 0.25, 0.25, 0.5, 0.5),
                ),
                KecapiPattern("a+", (0.5,)),
            ),
        }
        modulation_pattern = {
            1: (
                KecapiPattern("a+", (0.5,)),
                KecapiPattern("x", (0.5,)),
                KecapiPattern("x a+b-.", (0.5, 0.5)),
            ),
            2: (
                KecapiPattern("a+", (0.5,)),
                KecapiPattern("a+b-.", (0.5,)),
                KecapiPattern("a+ a+C-. a+b-. x a+", (0.5, 0.25, 0.25, 0.5, 0.5)),
            ),
            3: (
                KecapiPattern("a+", (0.5,)),
                KecapiPattern(
                    "x a+b-. a+C-. a+C-D-.. a+b-.", (0.5, 0.5, 0.25, 0.25, 0.5)
                ),
                KecapiPattern(
                    "a+b-. a+C-D-.. a+C-. (a+ a+b-.)", (0.25, 0.25, 0.5, 0.5)
                ),
            ),
        }
        return (resolution_pattern, modulation_pattern)


class Plus_StaticLancaranStyle_Full_WithoutHeader(
    Plus_StaticLancaranStyle_Full_WithHeader
):
    apply_with_header_if_header_exist = False


class Minus_StaticLancaranStyle_Full_WithHeader(StaticLancaranStyle_Full):
    @property
    def pattern(self) -> dict:
        resolution_pattern = {
            2: (
                KecapiPattern("x", (0.5,)),
                KecapiPattern("a+b-. c+d+b- b-..", (0.5, 0.5, 0.5)),
                KecapiPattern("x", (0.5,)),
            ),
            3: (
                KecapiPattern("x b-..", (0.25, 0.25)),
                KecapiPattern(
                    "a+b-. c+d+b- b-.. x b-.. c+b-.",
                    (0.5, 0.25, 0.25, 0.75, 0.25, 0.5),
                ),
                KecapiPattern("x", (0.5,)),
            ),
            4: (
                KecapiPattern("a+b-.", (0.5,)),
                KecapiPattern(
                    "b-.. c+d+b- x a+C-. a+b+C- x b-.. c+d+b- b-..",
                    (0.5, 0.5, 0.25, 0.25, 0.5, 0.25, 0.25, 0.5, 0.5),
                ),
                KecapiPattern("x", (0.5,)),
            ),
        }

        modulation_pattern = {
            1: (
                KecapiPattern("x", (0.5,)),
                KecapiPattern("b-..", (0.5,)),
                KecapiPattern("c+d+b- b-..", (0.5, 0.5)),
            ),
            2: (
                KecapiPattern("x b-..", (0.25, 0.25)),
                KecapiPattern("a+b-. b-..", (0.75, 0.25)),
                KecapiPattern(
                    "c+b-. a+b-. c+d+b- b-.. a+b-.", (0.25, 0.25, 0.25, 0.25, 0.5)
                ),
            ),
            3: (
                KecapiPattern("x b-..", (0.25, 0.25)),
                KecapiPattern(
                    "c+b-. b-.. C-.. a+C-. b-..", (0.25, 0.5, 0.25, 0.75, 0.25)
                ),
                KecapiPattern("a+b-. C-.. a+b-. a+b-.", (0.75, 0.25, 0.25, 0.25)),
            ),
        }
        return (resolution_pattern, modulation_pattern)


class Minus_StaticLancaranStyle_Full_WithoutHeader(
    Minus_StaticLancaranStyle_Full_WithHeader
):
    apply_with_header_if_header_exist = False


class ToGongLancaranStyle(LancaranStyle):
    def create_cadence(
        self,
        stresses: tuple,
        does_siter_play: tuple,
        gender: bool,
        previous_signified: int,
        current_signified: int,
        following_signified: int,
        previous_side_prime: int,
        current_side_prime: int,
        following_side_prime: int,
    ) -> old.JICadence:
        amount_hits = len(stresses) + 1
        main_prime = current_signified
        side_prime = current_side_prime
        if amount_hits == 1:
            pattern = (self.pattern["silent"](gender, main_prime, side_prime),)
        elif amount_hits == 2:
            pattern = tuple(
                self.pattern[p](gender, main_prime, side_prime)
                for p in ("silent", "to_gong_last")
            )
        else:
            beginning = ("to_gong_first", "to_gong_second")
            ending = ("to_gong_last",)
            left = amount_hits - sum((len(beginning), len(ending)))
            cycle = itertools.cycle(("to_gong_middle0", "to_gong_middle1"))
            middle = tuple(next(cycle) for n in range(left))
            pattern = tuple(
                self.pattern[p](gender, main_prime, side_prime)
                for p in beginning + middle + ending
            )

        cadence = functools.reduce(operator.add, pattern)

        return old.JICadence(cadence)


class Plus_ToGongLancaranStyle(ToGongLancaranStyle):
    @property
    def pattern(self) -> dict:
        return _plus_pattern


class Minus_ToGongLancaranStyle(ToGongLancaranStyle):
    @property
    def pattern(self) -> dict:
        return _minus_pattern


class CircleLancaranStyle(lancaran_inter2polation.LancaranStyleForInstrument):
    @property
    def available_pattern_sizes(self) -> tuple:
        return tuple(self.pattern.keys())

    @property
    def pattern(self) -> dict:
        return {
            4: self.pattern_data["aba"],
            5: self.pattern_data["abba"],
            6: self.pattern_data["abbba"],
            7: self.pattern_data["abbba"],
        }

    def create_cadence(
        self,
        stresses: tuple,
        does_siter_play: tuple,
        gender: bool,
        previous_signified: int,
        current_signified: int,
        following_signified: int,
        previous_side_prime: int,
        current_side_prime: int,
        following_side_prime: int,
    ) -> old.JICadence:
        usize = len(stresses) + 1
        cadence = self.pattern[usize](gender, current_signified, current_side_prime)

        return old.JICadence(cadence)


class Plus_CircleLancaranStyle(CircleLancaranStyle):
    @property
    def pattern_data(self) -> tuple:
        return _plus_pattern


class Minus_CircleLancaranStyle(CircleLancaranStyle):
    @property
    def pattern_data(self) -> tuple:
        return _minus_pattern


class LoopLancaranStyle(lancaran_inter2polation.LancaranStyleForInstrument):
    @property
    def pattern(self) -> tuple:
        return None

    @property
    def loopsize(self) -> int:
        raise NotImplementedError

    def get_pattern(self, gender, main_prime, side_prime) -> tuple:
        raise NotImplementedError

    def create_cadence(
        self,
        stresses: tuple,
        does_siter_play: tuple,
        gender: bool,
        previous_signified: int,
        current_signified: int,
        following_signified: int,
        previous_side_prime: int,
        current_side_prime: int,
        following_side_prime: int,
    ) -> old.JICadence:
        usize = (len(stresses) + 1) * 2
        amount_pattern = usize / self.loopsize

        assert int(amount_pattern) == amount_pattern

        cadence = tuple(
            self.get_pattern(gender, current_signified, current_side_prime)
            for i in range(int(amount_pattern))
        )

        return old.JICadence(cadence)


class Plus_LoopLancaranStyle3(LoopLancaranStyle):
    @property
    def loopsize(self) -> int:
        return 3

    def get_pattern(self, gender, main_prime, side_prime) -> tuple:
        return KecapiPattern("x a+b-. a+", (0.5, 0.5, 0.5))(
            gender, main_prime, side_prime
        )


class Plus_LoopLancaranStyle4(LoopLancaranStyle):
    @property
    def loopsize(self) -> int:
        return 4

    def get_pattern(self, gender, main_prime, side_prime) -> tuple:
        return KecapiPattern("x a+b-. a+ a+b-.", (0.5, 0.5, 0.5, 0.5))(
            gender, main_prime, side_prime
        )


class Plus_LoopLancaranStyle5(LoopLancaranStyle):
    @property
    def loopsize(self) -> int:
        return 5

    def get_pattern(self, gender, main_prime, side_prime) -> tuple:
        return KecapiPattern("x a+b-. x a+ a+b-.", (0.5, 0.5, 0.5, 0.5, 0.5))(
            gender, main_prime, side_prime
        )


class Plus_LoopLancaranStyle6(LoopLancaranStyle):
    @property
    def loopsize(self) -> int:
        return 6

    def get_pattern(self, gender, main_prime, side_prime) -> tuple:
        return KecapiPattern(
            "x a+b-. a+C-. a+b-. a+ x", (0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
        )(gender, main_prime, side_prime)


class Plus_LoopLancaranStyle7(LoopLancaranStyle):
    @property
    def loopsize(self) -> int:
        return 7

    def get_pattern(self, gender, main_prime, side_prime) -> tuple:
        return KecapiPattern(
            "x a+b-. a+C-. a+b-. x a+ x", (0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
        )(gender, main_prime, side_prime)


class Minus_LoopLancaranStyle3(LoopLancaranStyle):
    @property
    def loopsize(self) -> int:
        return 3

    def get_pattern(self, gender, main_prime, side_prime) -> tuple:
        return KecapiPattern("x b-.. x", (0.5, 0.5, 0.5))(
            gender, main_prime, side_prime
        )


class Minus_LoopLancaranStyle4(LoopLancaranStyle):
    @property
    def loopsize(self) -> int:
        return 4

    def get_pattern(self, gender, main_prime, side_prime) -> tuple:
        return KecapiPattern("x a+b-. b-.. a+b-.", (0.5, 0.5, 0.5, 0.5))(
            gender, main_prime, side_prime
        )


class Minus_LoopLancaranStyle5(LoopLancaranStyle):
    @property
    def loopsize(self) -> int:
        return 5

    def get_pattern(self, gender, main_prime, side_prime) -> tuple:
        return KecapiPattern("x b-.. x x b-..", (0.5, 0.5, 0.5, 0.5, 0.5))(
            gender, main_prime, side_prime
        )


class Minus_LoopLancaranStyle6(LoopLancaranStyle):
    @property
    def loopsize(self) -> int:
        return 6

    def get_pattern(self, gender, main_prime, side_prime) -> tuple:
        return KecapiPattern("x b-.. x b-.. c+d+b- x", (0.5, 0.5, 0.5, 0.5, 0.5, 0.5))(
            gender, main_prime, side_prime
        )


class Minus_LoopLancaranStyle7(LoopLancaranStyle):
    @property
    def loopsize(self) -> int:
        return 7

    def get_pattern(self, gender, main_prime, side_prime) -> tuple:
        return KecapiPattern(
            "x b-.. x x b-.. x x", (0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
        )(gender, main_prime, side_prime)


class SilentLancaranStyle(LancaranStyle):
    @property
    def pattern(self) -> tuple:
        return _plus_pattern

    def choose_pattern(
        self,
        stress: bool,
        does_siter_play: bool,
        idx: int,
        size: int,
        gender: bool,
        previous_signified: int,
        current_signified: int,
        following_signified: int,
        previous_side_prime: int,
        current_side_prime: int,
        following_side_prime: int,
    ) -> old.JICadence:
        return self.pattern["silent"](gender, current_signified, current_side_prime)


class Plus_MovelessLancaranStyle_Simple(LancaranStyle):
    @property
    def pattern(self) -> tuple:
        return _plus_pattern

    def choose_pattern(
        self,
        stress: bool,
        does_siter_play: bool,
        idx: int,
        size: int,
        gender: bool,
        previous_signified: int,
        current_signified: int,
        following_signified: int,
        previous_side_prime: int,
        current_side_prime: int,
        following_side_prime: int,
    ) -> old.JICadence:
        if _KECAPI_RANDOM.random > 0.3:
            return self.pattern["static_moveless"](
                gender, current_signified, current_side_prime
            )
        else:
            return self.pattern["silent"](gender, current_signified, current_side_prime)


class StaticLancaranStyle_Simple(LancaranStyle):
    def choose_pattern(
        self,
        stress: bool,
        does_siter_play: bool,
        idx: int,
        size: int,
        gender: bool,
        previous_signified: int,
        current_signified: int,
        following_signified: int,
        previous_side_prime: int,
        current_side_prime: int,
        following_side_prime: int,
    ) -> old.JICadence:
        if stress:
            for_predict_conditions = (
                does_siter_play,
                _KECAPI_RANDOM.choices([True, False], [0.7, 0.3], k=1)[0],
            )
            for_silent_condition = (
                not does_siter_play,
                _KECAPI_RANDOM.choices([True, False], [0.5, 0.6], k=1)[0],
            )
            if all(for_predict_conditions):
                pattern = self.pattern["static_stable_predict"]
            elif all(for_silent_condition):
                pattern = self.pattern["static_stable_silent"]
            else:
                pattern = self.pattern["static_stable"]
        else:
            if idx + 2 == size and current_signified != following_signified:
                pattern = self.pattern["silent"]
            else:
                if idx == 0:
                    prob = [0.7, 0.3]
                else:
                    prob = [0.2, 0.64]
                use_easy_pattern = _KECAPI_RANDOM.choices([True, False], prob, k=1)[0]
                if use_easy_pattern:
                    pattern = self.pattern["static_unstable_easy"]
                else:
                    if _KECAPI_RANDOM.random() > 0.7:
                        pattern = self.pattern["static_unstable_variation"]
                    else:
                        pattern = self.pattern["static_unstable"]

        if idx + 2 >= size:
            main_prime = following_signified
            side_prime = following_side_prime
        else:
            main_prime = current_signified
            side_prime = current_side_prime

        return pattern(gender, main_prime, side_prime)


class Plus_StaticLancaranStyle_Simple(StaticLancaranStyle_Simple):
    @property
    def pattern(self) -> dict:
        return _plus_pattern


class Minus_StaticLancaranStyle_Simple(StaticLancaranStyle_Simple):
    @property
    def pattern(self) -> dict:
        return _minus_pattern


class FromGongLancaranStyle(LancaranStyle):
    def choose_pattern(
        self,
        stress: bool,
        does_siter_play: bool,
        idx: int,
        size: int,
        gender: bool,
        previous_signified: int,
        current_signified: int,
        following_signified: int,
        previous_side_prime: int,
        current_side_prime: int,
        following_side_prime: int,
    ) -> old.JICadence:
        if stress:
            pattern = self.pattern["static_moveless"]
        else:
            pattern = self.pattern["silent"]

        if idx + 2 >= size:
            main_prime = following_signified
            side_prime = following_side_prime
        else:
            main_prime = current_signified
            side_prime = current_side_prime

        return pattern(gender, main_prime, side_prime)


class Plus_FromGongLancaranStyle(FromGongLancaranStyle):
    @property
    def pattern(self) -> dict:
        return _plus_pattern


class Minus_FromGongLancaranStyle(FromGongLancaranStyle):
    @property
    def pattern(self) -> dict:
        return _minus_pattern


class AlternatingLancaranStyle_Simple(LancaranStyle):
    def choose_pattern(
        self,
        stress: bool,
        does_siter_play: bool,
        idx: int,
        size: int,
        gender: bool,
        previous_signified: int,
        current_signified: int,
        following_signified: int,
        previous_side_prime: int,
        current_side_prime: int,
        following_side_prime: int,
    ) -> old.JICadence:
        if stress:
            main_prime = current_signified
            side_prime = current_side_prime

            for_silent_condition = (
                not does_siter_play,
                _KECAPI_RANDOM.choices([True, False], [0.5, 0.6], k=1)[0],
            )
            if all(for_silent_condition):
                pattern = self.pattern["alternating_stable_silent"]
            else:
                pattern = self.pattern["alternating_stable"]
        else:
            main_prime = previous_signified
            side_prime = previous_side_prime
            pattern = self.pattern["alternating_unstable"]

        return pattern(gender, main_prime, side_prime)


class Plus_AlternatingLancaranStyle_Simple(AlternatingLancaranStyle_Simple):
    @property
    def pattern(self) -> dict:
        return _plus_pattern


class Minus_AlternatingLancaranStyle_Simple(AlternatingLancaranStyle_Simple):
    @property
    def pattern(self) -> dict:
        return _minus_pattern
