from nongkrong.algorithms.forms import lancaran_inter2polation

from mu.mel import ji
from mu.sco import old


import itertools
import random as __RANDOM_KENDANG

__RANDOM_KENDANG.seed(100)


class LancaranStyle(lancaran_inter2polation.LancaranStyleForInstrument):
    @property
    def pattern(self) -> dict:
        return {
            "silent": lancaran_inter2polation.Pattern("x", (1,)),
            "stable": lancaran_inter2polation.Pattern("a", (1,)),
            "stable_delayed": lancaran_inter2polation.Pattern("x a", (0.5, 0.5)),
            "stable_and_predict": lancaran_inter2polation.Pattern("a b.", (0.5, 0.5)),
            "stable_tricky": lancaran_inter2polation.Pattern(
                "a a. a", (0.25, 0.25, 0.5)
            ),
            "stable_tricky_delayed": lancaran_inter2polation.Pattern(
                "x a. a. a.", (0.25, 0.25, 0.25, 0.5)
            ),
            "unstable": lancaran_inter2polation.Pattern("b. b.", (0.5, 0.5)),
            "unstable_stable": lancaran_inter2polation.Pattern("b", (1,)),
            "unstable_delayed": lancaran_inter2polation.Pattern(
                "x b. b.", (0.25, 0.25, 0.5)
            ),
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
        chord0 = old.Chord(ji.JIHarmony([]), 1)

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
            final_cadence += pat

        return old.JICadence(final_cadence)


class MovelessLancaranStyle(LancaranStyle):
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
        main_prime = current_signified
        side_prime = current_side_prime
        pattern = self.pattern[
            __RANDOM_KENDANG.choice(
                (
                    "stable",
                    "stable_delayed",
                    "stable_and_predict",
                    "stable_tricky",
                    "stable_tricky_delayed",
                    "silent",
                    "silent",
                )
            )
        ]
        return pattern(gender, main_prime, side_prime)


class SilentLancaranStyle(LancaranStyle):
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
        main_prime = current_signified
        side_prime = current_side_prime
        pattern = self.pattern["silent"]
        return pattern(gender, main_prime, side_prime)


class StaticLancaranStyle_Both(LancaranStyle):
    unstable_iter = itertools.cycle(("unstable", "unstable_delayed", "unstable_stable"))
    stable_iter = itertools.cycle(("stable", "stable_tricky", "stable"))

    def unstable_pattern(self):
        return self.pattern[next(self.unstable_iter)]

    def stable_pattern(self):
        return self.pattern[next(self.stable_iter)]

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
            pattern = self.stable_pattern()
        else:
            pattern = self.unstable_pattern()

        if idx + 1 >= size:
            main_prime = following_signified
            side_prime = following_side_prime
        else:
            main_prime = current_signified
            side_prime = current_side_prime

        return pattern(gender, main_prime, side_prime)


class StaticLancaranStyle_OnlyStable(LancaranStyle):
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
            pattern = self.pattern["stable"]
        else:
            pattern = self.pattern["silent"]

        if idx + 1 >= size:
            main_prime = following_signified
            side_prime = following_side_prime
        else:
            main_prime = current_signified
            side_prime = current_side_prime

        return pattern(gender, main_prime, side_prime)


class StaticLancaranStyle_OnlyUnstable(LancaranStyle):
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
            pattern = self.pattern["silent"]
        else:
            pattern = self.pattern["unstable"]

        if idx + 1 >= size:
            main_prime = following_signified
            side_prime = following_side_prime
        else:
            main_prime = current_signified
            side_prime = current_side_prime

        return pattern(gender, main_prime, side_prime)


class AlternatingLancaranStyle_Stable(LancaranStyle):
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
            pattern = self.pattern["stable"]
            main_prime = previous_signified
            side_prime = previous_side_prime
        else:
            pattern = self.pattern["unstable"]
            main_prime = current_signified
            side_prime = current_side_prime

        return pattern(gender, main_prime, side_prime)
