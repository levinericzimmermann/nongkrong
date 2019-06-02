from nongkrong.harmony import shortwriting as sw

from mu.mel import ji
from mu.sco import old

import abc
import itertools


class Pattern(abc.ABC):
    main = "a"
    side = "b"

    def __init__(self, pitch_line: str, rhythms: tuple):
        self.__line = pitch_line
        self.__rhythms = rhythms

    @property
    def line(self) -> str:
        return self.__line

    @property
    def rhythms(self) -> tuple:
        return self.__rhythms

    def __call__(self, gender: bool, main_prime: int, side_prime: int) -> old.JICadence:
        pitches = sw.translate(
            self.__line,
            decodex={self.main: str(main_prime), self.side: str(side_prime)},
            inverse=not gender,
        )
        return old.JICadence([old.Chord(h, r) for h, r in zip(pitches, self.__rhythms)])


class LancaranStyleForInstrument(abc.ABC):
    """General Style description for Kendang and Kecapi styles"""

    @abc.abstractproperty
    def pattern(self) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError

    def detect_pattern(
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
        size = len(stresses)
        pattern = []
        for idx, stress, dsp in zip(range(size), stresses, does_siter_play):
            pattern.append(
                self.choose_pattern(
                    stress,
                    dsp,
                    idx,
                    size,
                    gender,
                    previous_signified,
                    current_signified,
                    following_signified,
                    previous_side_prime,
                    current_side_prime,
                    following_side_prime,
                )
            )

        return tuple(pattern)


class LancaranStyle(object):
    def __init__(
        self,
        stresses_generator,
        siter_style,
        kecapi_plus_style,
        kecapi_minus_style,
        kendang_style,
    ) -> None:
        self.__stresses_generator = stresses_generator
        self.__siter_style = siter_style
        self.__kecapi_plus_style = kecapi_plus_style
        self.__kecapi_minus_style = kecapi_minus_style
        self.__kendang_style = kendang_style

    @property
    def stresses_generator(self):
        return self.__stresses_generator

    @property
    def siter_style(self):
        return self.__siter_style

    @property
    def kecapi_plus_style(self):
        return self.__kecapi_plus_style

    @property
    def kecapi_minus_style(self):
        return self.__kecapi_minus_style

    @property
    def kendang_style(self):
        return self.__kendang_style

    def mk_siter_cadence(
        self,
        siter_panerus_pitch,
        gender,
        previous_signified: int,
        previous_side_prime: int,
        current_signified: int,
        current_side_prime: int,
        following_signified: int,
        following_side_prime: int,
        stresses,
    ) -> old.JICadence:
        siter_pitches = self.siter_style.convert2interpolation(
            gender,
            previous_signified,
            previous_side_prime,
            current_signified,
            current_side_prime,
            following_signified,
            following_side_prime,
            stresses,
        )
        siter_pitches = tuple(ji.JIHarmony([p]) for p in siter_pitches)
        siter_pitches = (ji.JIHarmony(siter_panerus_pitch),) + siter_pitches
        return old.JICadence([old.Chord(h, 1) for h in siter_pitches])

    def convert2cadences(
        self,
        unitsize: int,
        siter_panerus_pitch: ji.JIPitch,
        gender: bool,
        previous_signified: int,
        previous_side_prime: int,
        current_signified: int,
        current_side_prime: int,
        following_signified: int,
        following_side_prime: int,
    ) -> tuple:
        stresses = self.stresses_generator(unitsize)

        siter_cadence = self.mk_siter_cadence(
            siter_panerus_pitch,
            gender,
            previous_signified,
            previous_side_prime,
            current_signified,
            current_side_prime,
            following_signified,
            following_side_prime,
            stresses,
        )

        does_siter_play = self.siter_style.is_played_or_not_per_pitch(stresses)

        other_cadences = (
            style.create_cadence(
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
            for style in (
                self.kecapi_plus_style,
                self.kecapi_minus_style,
                self.kendang_style,
            )
        )
        return (siter_cadence,) + tuple(other_cadences)


class StressesMaker(abc.ABC):
    @abc.abstractmethod
    def __call__(self, unitsize) -> tuple:
        raise NotImplementedError


class SimpleStressesMaker(StressesMaker):
    def __init__(self, amount_unstable_per_period: int) -> None:
        assert amount_unstable_per_period >= 1
        self.__period = self.mk_period(amount_unstable_per_period)

    @staticmethod
    def mk_period(amount_unstable_per_period) -> tuple:
        period = (False,) * amount_unstable_per_period
        return tuple(period + (True,))

    @property
    def period(self) -> tuple:
        return self.__period

    def __call__(self, unitsize) -> tuple:
        period = itertools.cycle(self.period)
        stresses = [next(period) for i in range(unitsize - 1)]
        if stresses[-1] is True:
            stresses[-1] = False
        return tuple(reversed(stresses))


class MultiStressesMaker(StressesMaker):
    def __init__(self, seed: int):
        import random as msm_random

        msm_random.seed(seed)
        self.__random = msm_random
        self.__sm = (
            SimpleStressesMaker(1),
            SimpleStressesMaker(2),
            SimpleStressesMaker(3),
        )

    def __call__(self, unitsize) -> tuple:
        probabilities = [0.7, 0.3, 0.2]
        if unitsize % 4 == 0 and unitsize > 4:
            probabilities[2] = 2
        elif unitsize % 3 == 0:
            probabilities[1] += 1.2

        return self.__random.choices(self.__sm, probabilities, k=1)[0](unitsize)
