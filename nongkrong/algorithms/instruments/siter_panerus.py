from nongkrong.harmony import modes
from nongkrong.instruments import SITER_PANERUS

from mu.mel import mel
from mu.mel import ji

import abc
import itertools


def mk_simple_conversion2pitches(
    mode: modes.Mode, funcs: tuple, subfunctions_per_interpol: tuple
) -> tuple:
    """Expect real functions (with applied modulation), not symbolic functions"""

    def filter_subfunc_pitch(pitch) -> ji.JIPitch:
        if pitch == ji.r(1, 1):
            pitch += ji.r(2, 1)
        if pitch in SITER_PANERUS.pitches:
            return pitch
        else:
            return mel.TheEmptyPitch

    res = []
    for func0, func1, subfuncline in zip(funcs, funcs[1:], subfunctions_per_interpol):
        subfunc_pitches = tuple(
            (filter_subfunc_pitch(p),)
            for p in subfuncline.convert_signifiers2pitches(mode, func0, func1)
        )[:-1]

        for h in subfunc_pitches:
            h = tuple(p for p in h if p)
            res.append(h)

    return tuple(res)


class _SiterStyle(abc.ABC):
    """Abstract Siter Style class"""

    def __init__(
        self,
        play_stable_pitch: bool,
        play_unstable_pitch: bool,
        play_only_first_and_last_pitch: bool,
    ):
        self.__play_stable_pitch = play_stable_pitch
        self.__play_unstable_pitch = play_unstable_pitch
        self.__play_only_first_and_last_pitch = play_only_first_and_last_pitch

    @property
    def play_stable_pitch(self) -> bool:
        return self.__play_stable_pitch

    @property
    def play_unstable_pitch(self) -> bool:
        return self.__play_unstable_pitch

    @property
    def play_only_first_and_last_pitch(self) -> bool:
        return self.__play_only_first_and_last_pitch

    def is_played_or_not_per_pitch(self, stresses: tuple) -> tuple:
        """Return tuple containing True or False.
        True if pitch get played,
        False if pitch doesn't get played.
        The tuple stresses also only contain bool
        values. True for stable and False for unstable.
        """
        is_played_or_not = []
        for stress in stresses:
            if stress and self.play_stable_pitch:
                is_played_or_not.append(True)
            elif not stress and self.play_unstable_pitch:
                is_played_or_not.append(True)
            else:
                is_played_or_not.append(False)

        lstresses = len(stresses)
        if self.play_only_first_and_last_pitch:

            if lstresses >= 2:
                middle = [False for i in range(lstresses - 2)]
                is_played_or_not = (
                    [is_played_or_not[0]] + middle + [is_played_or_not[-1]]
                )

            elif lstresses == 1:
                is_played_or_not = [True]
            else:
                is_played_or_not = []

        assert len(is_played_or_not) == len(stresses)

        return tuple(is_played_or_not)

    @abc.abstractmethod
    def convert2interpolation(
        self,
        gender: bool,
        previous_signified: int,
        previous_side_prime: int,
        current_signified: int,
        current_side_prime: int,
        following_signified: int,
        following_side_prime: int,
        stresses: tuple,
    ) -> ji.JIMel:
        raise NotImplementedError

    @staticmethod
    def mk_pitch_from_prime(prime, gender):
        if prime:
            if gender:
                p = ji.r(prime, 1)
            else:
                p = ji.r(1, prime)
            return p.normalize(2) + ji.r(2, 1)
        else:
            return mel.TheEmptyPitch


class StaticSiterStyle(_SiterStyle):
    def convert2interpolation(
        self,
        gender: bool,
        previous_signified: int,
        previous_side_prime: int,
        current_signified: int,
        current_side_prime: int,
        following_signified: int,
        following_side_prime: int,
        stresses: tuple,
    ) -> ji.JIMel:

        amount_hits = len(stresses)
        is_played_or_not_per_pitch = self.is_played_or_not_per_pitch(stresses)
        p0 = self.mk_pitch_from_prime(current_signified, gender)
        p1 = self.mk_pitch_from_prime(following_signified, gender)
        pitches = []
        for idx, is_played_or_not in enumerate(is_played_or_not_per_pitch):
            if is_played_or_not:
                if idx + 1 == amount_hits:
                    local_pitch = p0.copy()
                else:
                    local_pitch = p1.copy()
            else:
                local_pitch = mel.TheEmptyPitch
            pitches.append(local_pitch)
        return ji.JIMel(pitches)


class AlternatingSiterStyle(_SiterStyle):
    def convert2interpolation(
        self,
        gender: bool,
        previous_signified: int,
        previous_side_prime: int,
        current_signified: int,
        current_side_prime: int,
        following_signified: int,
        following_side_prime: int,
        stresses: tuple,
    ) -> ji.JIMel:

        is_played_or_not_per_pitch = self.is_played_or_not_per_pitch(stresses)
        p0 = self.mk_pitch_from_prime(previous_signified, gender)
        p1 = self.mk_pitch_from_prime(current_signified, gender)
        pitches = []
        for stress, is_played_or_not in zip(stresses, is_played_or_not_per_pitch):
            if is_played_or_not:
                if stress:
                    local_pitch = p1.copy()
                else:
                    local_pitch = p0.copy()
            else:
                local_pitch = mel.TheEmptyPitch
            pitches.append(local_pitch)

        return ji.JIMel(pitches)


class CircleSiterStyle(_SiterStyle):
    def __init__(self):
        _SiterStyle.__init__(self, True, True, False)

    def convert2interpolation(
        self,
        gender: bool,
        previous_signified: int,
        previous_side_prime: int,
        current_signified: int,
        current_side_prime: int,
        following_signified: int,
        following_side_prime: int,
        stresses: tuple,
    ) -> ji.JIMel:

        p0 = self.mk_pitch_from_prime(current_signified, gender)
        p1 = self.mk_pitch_from_prime(current_side_prime, gender)
        pitches_middle = [p1 for i in range(len(stresses) - 2)]
        pitches = [p0] + pitches_middle + [p0]
        return ji.JIMel(pitches)


class ToGongSiterStyle(_SiterStyle):
    def __init__(self):
        _SiterStyle.__init__(self, True, True, False)

    def convert2interpolation(
        self,
        gender: bool,
        previous_signified: int,
        previous_side_prime: int,
        current_signified: int,
        current_side_prime: int,
        following_signified: int,
        following_side_prime: int,
        stresses: tuple,
    ) -> ji.JIMel:

        amount_stresses = len(stresses)
        p0 = self.mk_pitch_from_prime(current_signified, gender)
        p1 = self.mk_pitch_from_prime(current_side_prime, gender)
        cycle = itertools.cycle((p0, p1))
        pitches = [next(cycle) for i in range(amount_stresses)]
        pitches[-1] = mel.TheEmptyPitch

        return ji.JIMel(pitches)


class EmptySiterStyle(_SiterStyle):
    def convert2interpolation(
        self,
        gender: bool,
        previous_signified: int,
        previous_side_prime: int,
        current_signified: int,
        current_side_prime: int,
        following_signified: int,
        following_side_prime: int,
        stresses: tuple,
    ) -> ji.JIMel:
        return ji.JIMel([mel.TheEmptyPitch for i in stresses])
