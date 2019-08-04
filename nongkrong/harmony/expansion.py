import abc
import functools
import itertools
import operator

from mu.mel import ji
from mu.mel import mel
from mu.sco import old
from mu.rhy import indispensability
from mu.utils import tools

from nongkrong.harmony import expattern
from nongkrong.harmony import modes
from nongkrong.harmony import abodefunctions
from nongkrong.harmony import interfunctions
from nongkrong.harmony import subfunctions


"""This module implements harmonic expansions of SubFunctions.

Those SubFunctions could be in form of
    (1) InterFunctions
    (2) AbodeFunctions

Between two SubFunctions, an additional harmonic field can be placed.
This additional harmonic field can be descriped by Expansion - Objects.
Therefore Expansion - Objects symbolize an additional nested structure
between two SubFunctions (while SubFunctions, on the other hand,
are nested within Functions).

Depending on the harmonic situation, we can differentiate between three
different forms (classes) of Exploration - Objects:
    (1) stable fields
    (2) unstable flipping fields
    (3) unstable shifting fields (positive shift vs. negative shift)

The harmonic movement of prime numbers in those different fields could be descriped as
    (1) a/b -> a/b
    (2) a/b -> b/a (flip)
    (3) a/b -> x/b (positive shift) or a/b -> a/x (negative shift)

The specific harmonic situation, that's responsible for deciding if (1), (2)
or (3) shall be used, can be found in the respective SubFunctions.
    (1) Can be used if the Singifier of the following SubFunction could be paired
        with the Signified of the current SubFunction
    (2) Has to be used if the next Exploration is a flipped version of the current one
    (3) Has to be used if neither (1) nor (2) is True


Expansions are musically represented by the following instruments:
    (1) Kecapi
"""


class AbstractExpansion(abc.ABC):
    def __init__(self, main_prime: int, side_prime: int):
        self.__main_prime = main_prime
        self.__side_prime = side_prime

    @staticmethod
    def get_value_of_essence(essence: int, mode: modes.Mode) -> int:
        if mode.x == essence:
            return 2
        elif mode.y == essence:
            return 1
        else:
            return 0

    @staticmethod
    def get_pitch_essence(pitch: ji.JIPitch) -> int:
        component = pitch.components[1]
        if not component.gender:
            component = component.inverse()
        return int(component.float)

    @staticmethod
    def transform_primes2pitches(primes: tuple, mode: modes.Mode) -> ji.JIPitch:
        if not mode.gender:
            primes = tuple(reversed(primes))
        return ji.r(primes[0], primes[1]).normalize() + ji.r(2, 1)

    @property
    def main_prime(self) -> int:
        return self.__main_prime

    @property
    def side_prime(self) -> int:
        return self.__side_prime

    @abc.abstractmethod
    def solve(self, a: int, b: int, x: int, mode: modes.Mode, rhythm: tuple) -> tuple:
        raise NotImplementedError


class StableEx(AbstractExpansion):
    @staticmethod
    def sort_by_closeness_to_reference(
        reference: ji.JIPitch, pitches: tuple, mode: modes.Mode
    ) -> tuple:
        essences = (AbstractExpansion.get_pitch_essence(p - reference) for p in pitches)
        pairs = (
            (p, AbstractExpansion.get_value_of_essence(essence, mode))
            for p, essence in zip(essences, pitches)
        )
        sorted_pairs = sorted(pairs, key=operator.itemgetter(1), reverse=True)
        return tuple(p[0] for p in sorted_pairs)

    def solve(
        self,
        a: int,
        b: int,
        x: int,
        mode: modes.Mode,
        rhythm: tuple,
        splinter: expattern.Splinter,
    ) -> tuple:
        primes = (a, b, x)

        main_prime = primes[self.main_prime]
        side_prime = primes[self.side_prime]
        unused_prime = tuple(p for p in primes if p not in (main_prime, side_prime))[0]

        keys = {
            "o": mel.TheEmptyPitch,
            "a": AbstractExpansion.transform_primes2pitches(
                (main_prime, side_prime), mode
            ),
        }

        high_pitches = (
            ji.r(1, side_prime),
            ji.r(main_prime, side_prime * unused_prime),
        )
        if not mode.gender:
            high_pitches = tuple(p.inverse() for p in high_pitches)

        high_pitches = tuple(hp.normalize() + ji.r(4, 1) for hp in high_pitches)
        high_pitches_sorted = StableEx.sort_by_closeness_to_reference(
            keys["a"], high_pitches, mode
        )

        keys.update({"a.": high_pitches_sorted[0], "b.": high_pitches_sorted[1]})

        if high_pitches_sorted[0] == high_pitches[0]:
            first_side_pitch_primes = (main_prime, unused_prime)
            second_side_pitch_primes = (unused_prime, side_prime)
        else:
            first_side_pitch_primes = (unused_prime, side_prime)
            second_side_pitch_primes = (main_prime, unused_prime)

        if not mode.gender:
            first_side_pitch_primes = tuple(reversed(first_side_pitch_primes))
            second_side_pitch_primes = tuple(reversed(second_side_pitch_primes))

        first_side_pitch = ji.r(*first_side_pitch_primes).normalize() + ji.r(2, 1)
        second_side_pitch = ji.r(*second_side_pitch_primes).normalize() + ji.r(2, 1)

        keys.update({"b": first_side_pitch, "b-": second_side_pitch})

        if mode.gender:
            low_pitches = (
                ji.r(main_prime, 1),
                ji.r(main_prime * unused_prime, side_prime),
            )
        else:
            low_pitches = (
                ji.r(1, main_prime),
                ji.r(side_prime, main_prime * unused_prime),
            )

        low_pitches = tuple(lp.normalize() for lp in low_pitches)
        low_pitches_sorted = StableEx.sort_by_closeness_to_reference(
            keys["a"], low_pitches, mode
        )

        keys.update({".a": low_pitches_sorted[0], ".b": low_pitches_sorted[1]})

        return splinter.solve(keys)


class FlippedEx(AbstractExpansion):
    @staticmethod
    def find_high_pitch(primes0: tuple, primes1: tuple, mode: modes.Mode) -> ji.JIPitch:
        if primes0[0] == primes1[0]:
            if mode.gender:
                p = ji.r(primes0[0], primes0[1] * primes1[1])
            else:
                p = ji.r(primes0[0], 1)
        elif primes0[1] == primes1[1]:
            if mode.gender:
                p = ji.r(1, primes0[1])
            else:
                p = ji.r(primes0[0] * primes1[0], primes0[1])
        else:
            msg = "Unknown combination of primes: {0} and {1}.".format(primes0, primes1)
            raise ValueError(msg)

        return p.normalize() + ji.r(4, 1)

    @staticmethod
    def get_prime_interval(high: ji.JIPitch, middle: ji.JIPitch) -> int:
        return AbstractExpansion.get_pitch_essence(high - middle)

    @staticmethod
    def rate_intervals(intervals: tuple, mode: modes.Mode) -> int:
        return sum(
            AbstractExpansion.get_value_of_essence(inter, mode) for inter in intervals
        )

    @staticmethod
    def detect_data_for_pitches(pitches: tuple, mode: modes.Mode) -> tuple:
        transformed_pitches = tuple(
            AbstractExpansion.transform_primes2pitches(p, mode) for p in pitches[1:-1]
        )
        high_pitches = tuple(
            FlippedEx.find_high_pitch(p0, p1) for p0, p1 in zip(pitches, pitches[1:])
        )
        intervals = tuple(
            FlippedEx.get_prime_interval(h, m)
            for h, m in zip(
                high_pitches, transformed_pitches + (transformed_pitches[-1],)
            )
        )
        interval_ranking = FlippedEx.rate_intervals(intervals, mode)
        return (transformed_pitches, high_pitches, interval_ranking)

    def solve(self, a: int, b: int, x: int, mode: modes.Mode, rhythm: tuple) -> tuple:
        try:
            assert all((rhythm[0] >= 5, rhythm[1] >= 1))
        except AssertionError:
            msg = "Rhythmical structure has to be bigger than (4, 0)."
            raise ValueError(msg)

        primes = (a, b, x)
        a, b = primes[self.main_prime], primes[self.side_prime]
        x = tuple(p for p in (mode.x, mode.y, mode.z) if p not in (a, b))[0]

        data0 = FlippedEx.detect_data_for_pitches(
            ((x, b), (a, b), (a, x), (b, x), (b, a), (x, a)), mode
        )
        data1 = FlippedEx.detect_data_for_pitches(
            ((a, x), (a, b), (x, b), (x, a), (b, a), (b, x)), mode
        )

        if data0[2] > data1[2]:
            data = data0
        else:
            data = data1

        if rhythm[1] == 1:
            rhythms_middle = tools.euclid(rhythm[0], 5)
            rhythms_else = rhythm[0]
            middle = tuple(
                old.Tone(p, r)
                for p, r in zip((mel.TheEmptyPitch,) + data[0], rhythms_middle)
            )
            return ((old.Rest(rhythms_else),), middle, (old.Rest(rhythms_else),))
        else:
            complete_duration = rhythm[0] * rhythm[1]
            amount_pitches = len(data[0]) + len(data[1]) + 1  # middle + high + rest
            rhythmic_ranking = indispensability.bar_indispensability2indices(
                indispensability.indispensability_for_bar(rhythm)
            )[:amount_pitches]
            positions_middle = rhythmic_ranking[::2]
            positions_high = (0,) + rhythmic_ranking[1::2]
            low_line = (old.Rest(complete_duration),)

            middle_line = (
                old.Tone(p, r)
                for p, r in zip(
                    (mel.TheEmptyPitch,) + data[0],
                    (
                        b - a
                        for a, b in zip(
                            positions_middle,
                            positions_middle[1:] + (complete_duration,),
                        )
                    ),
                )
            )

            high_line = (
                old.Tone(p, r)
                for p, r in zip(
                    (mel.TheEmptyPitch,) + data[1],
                    (
                        b - a
                        for a, b in zip(
                            positions_high, positions_high[1:] + (complete_duration,)
                        )
                    ),
                )
            )

            return (low_line, middle_line, high_line)


class ShiftedEx(AbstractExpansion):
    @abc.abstractmethod
    def detect_start_and_stop_primes(
        self, a: int, b: int, x: int, mode: modes.Mode
    ) -> tuple:
        raise NotImplementedError

    @staticmethod
    def detect_middle_pitches(
        pitch0: ji.JIPitch, pitch1: ji.JIPitch, rhythm0: int
    ) -> tuple:
        pitches = [mel.TheEmptyPitch]
        rep = rhythm0 - 1
        if rhythm0 // 2 == 0:
            pitches += [pitch0]
            rep -= 1
        cyc = itertools.cycle((pitch0, pitch1))
        pitches += [next(cyc) for n in range(rep)]
        return tuple(pitches)

    @staticmethod
    def make_high_line(pitches: tuple, rhythm: tuple) -> tuple:
        def convert_pattern2pitches(pattern: tuple) -> tuple:
            return tuple(pitches[idx] if idx else mel.TheEmptyPitch for idx in pattern)

        if rhythm[1] == 1:
            return (old.Rest(rhythm[0] * rhythm[1]),)
        elif rhythm[1] == 2:
            pattern0 = (0, 1, 0, None)
            pattern1 = (0, None, 0, 2)
            amount_pattern = (rhythm[0] - 1) // 2
            pattern_cycle = itertools.cycle(
                tuple(convert_pattern2pitches(p) for p in (pattern0, pattern1))
            )
            pitch_line = functools.reduce(
                operator.add, tuple(next(pattern_cycle) for n in range(amount_pattern))
            )
            if rhythm[0] % 2 == 0:
                pitch_line = (pitches[0], mel.TheEmptyPitch) + pitch_line
            pitch_line = (mel.TheEmptyPitch,) + pitch_line + (pitches[-1],)

            try:
                assert len(pitch_line) == rhythm[0] * rhythm[1]
            except AssertionError:
                raise AssertionError(
                    "exp: {0} but {1}".format(len(pitch_line), rhythm[0] * rhythm[1])
                )

            return tuple(
                old.Melody(old.Tone(p, 1) for p in pitch_line)
                .tie_pauses()
                .discard_rests()
            )
        elif rhythm[1] == 3:
            patternA = (mel.TheEmptyPitch, pitches[1], pitches[0])
            patternB = (mel.TheEmptyPitch, pitches[2], pitches[0])
            dead_pattern = (mel.TheEmptyPitch, mel.TheEmptyPitch, pitches[0])

            pattern_type_cycle = itertools.cycle((1, 0, 0))
            choice_cycle = itertools.cycle((0, 1))
            choices = tuple(
                next(choice_cycle) for n in range(((rhythm[0] - 1) // 2) * 2)
            )
            if rhythm[0] % 2 == 0:
                choices = (0,) + choices
            choices = (1,) + choices

            pattern_types = (next(pattern_type_cycle) for n in choices)

            pitch_line = functools.reduce(
                operator.add,
                tuple(
                    (patternA, patternB)[choice] if ptype == 0 else dead_pattern
                    for choice, ptype in zip(choices, pattern_types)
                ),
            )

            try:
                assert len(pitch_line) == rhythm[0] * rhythm[1]
            except AssertionError:
                raise AssertionError(
                    "exp: {0} but {1}".format(len(pitch_line), rhythm[0] * rhythm[1])
                )

            return tuple(
                old.Melody(old.Tone(p, 1) for p in pitch_line)
                .tie_pauses()
                .discard_rests()
            )
        else:
            msg = "No solution for rhythmic structure {0} available".format(rhythm)
            raise ValueError(msg)

    def solve(self, a: int, b: int, x: int, mode: modes.Mode, rhythm: tuple) -> tuple:
        primes0, primes1 = self.detect_start_and_stop_primes(a, b, x, mode)
        pitch0, pitch1 = tuple(
            AbstractExpansion.transform_primes2pitches(p, mode)
            for p in (primes0, primes1)
        )
        high_pitches = self.detect_high_pitches(primes0, primes1, mode)
        complete_duration = rhythm[0] * rhythm[1]
        low_line = old.Rest(complete_duration)
        middle_line = tuple(
            old.Tone(p, rhythm[1])
            for p in ShiftedEx.detect_middle_pitches(pitch0, pitch1, rhythm[0])
        )
        high_line = ShiftedEx.make_high_line(high_pitches, rhythm)
        return (low_line, middle_line, high_line)


class ShiftedExPos(ShiftedEx):
    @staticmethod
    def detect_high_pitches(primes0, primes1, mode):
        pitches = (
            ji.r(1, primes0[1]),
            ji.r(primes0[0], primes0[1] * primes1[0]),
            ji.r(primes1[0], primes1[1] * primes0[0]),
        )

        if not mode.gender:
            pitches = tuple(p.inverse() for p in pitches)

        return tuple(p.normalize() + ji.r(4, 1) for p in pitches)

    def detect_start_and_stop_primes(
        self, a: int, b: int, x: int, mode: modes.Mode
    ) -> tuple:
        primes = (a, b, x)
        prime00, prime01 = primes[self.main_prime], primes[self.side_prime]
        prime10 = [p for p in primes if p not in (prime00, prime01)][0]
        return (prime00, prime01), (prime10, int(prime01))


class ShiftedExNeg(ShiftedEx):
    @staticmethod
    def detect_high_pitches(primes0, primes1, mode):
        pitches = (
            ji.r(primes0[0], primes0[1] * primes1[1]),
            ji.r(1, primes0[1]),
            ji.r(1, primes1[1]),
        )

        if not mode.gender:
            pitches = tuple(p.inverse() for p in pitches)

        return tuple(p.normalize() + ji.r(4, 1) for p in pitches)

    def detect_start_and_stop_primes(
        self, a: int, b: int, x: int, mode: modes.Mode
    ) -> tuple:
        primes = (a, b, x)
        prime00, prime01 = primes[self.main_prime], primes[self.side_prime]
        prime11 = [p for p in primes if p not in (prime00, prime01)][0]
        return (prime00, prime01), (int(prime00), prime11)


class ExpansionLine(tuple):
    def __init__(self, expansions):
        tuple.__init__(self, expansions)

    @staticmethod
    def detect_main_and_side_prime_position_per_subfunction(subfuncs: tuple) -> tuple:
        def detect_positions_for_interfunctions(subfuncs: tuple) -> tuple:
            res_positions = []
            for ifunc in subfuncs:
                if ifunc.signified == subfunctions.SINGLE_SIGNS[0]:
                    res_positions.append(0, 1)
                elif ifunc.signified == subfunctions.SINGLE_SIGNS[2]:
                    res_positions.append(2, 1)
                elif all(
                    (
                        ifunc.signified == subfunctions.SINGLE_SIGNS[1],
                        ifunc.nationality == 0,
                    )
                ):
                    res_positions.append(1, 0)
                elif all(
                    (
                        ifunc.signified == subfunctions.SINGLE_SIGNS[1],
                        ifunc.nationality == 1,
                    )
                ):
                    res_positions.append(1, 2)
                else:
                    msg = "UNKNOWN SIGNIFIED AND NATIONALITY COMBINATION "
                    msg += "FOR SIGNIFIED {0} AND NATIONALITY {1}.".format(
                        ifunc.signified, ifunc.nationality
                    )
                    raise NotImplementedError(msg)

            return tuple(res_positions)

        def detect_positions_for_abodefunctions(subfuncs: tuple) -> tuple:
            res_positions = []
            for af in subfuncs:
                if af.signified == subfunctions.SINGLE_SIGNS[0]:
                    res_positions.append(0, 1)
                elif af.signified == subfunctions.SINGLE_SIGNS[1]:
                    res_positions.append(1, 0)
                else:
                    msg = "UNKNOWN ABODEFUNCTION {0} WITH SIGNIFIED {1}".format(
                        af, af.signified
                    )
                    raise NotImplementedError(msg)
            return tuple(res_positions)

        typ = type(subfuncs[0])
        if typ == interfunctions.InterFunction:
            return detect_positions_for_interfunctions(subfuncs)
        elif typ == abodefunctions.AbodeFunction:
            return detect_positions_for_abodefunctions(subfuncs)
        else:
            msg = "Unknown subfunction type {0}!".format(typ)
            raise NotImplementedError(msg)

    @classmethod
    def from_subfuncline(cls, sfl: tuple) -> "ExpansionLine":
        positions = ExpansionLine.detect_main_and_side_prime_position_per_subfunction(
            sfl
        )

        expansions = []
        for pos0, pos1, subfunc0, subfunc1 in zip(
            positions, positions[1:], subfunctions, subfunctions[1:]
        ):
            if pos0 == tuple(reversed(pos1)):  # flipped
                ex = FlippedEx(pos0)

            elif subfunc0.is_stable and subfunc1.is_stable:  # shifted
                if pos0[0] == pos1[0]:
                    ex = ShiftedExNeg(pos0)
                else:
                    ex = ShiftedExPos(pos0)

            else:
                ex = StableEx(pos0)

            expansions.append(ex)

        expansions.append(StableEx(positions[-1]))

        return cls(expansions)
