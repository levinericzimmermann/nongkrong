import abc
import itertools

from mu.mel import mel
from mu.mel import ji
from mu.sco import old

from nongkrong.attractors import attractors
from nongkrong.metre import metre
from nongkrong.render import notation
from nongkrong.render import sound


"""This module implements classes to organise compositions in hierarchical structures.

Those hierarchical structures are not meant to be changed by post processing. Once
initalised, they can't be altered anymore (immutable objects). Their main purpose is
to offer an interface between render engines of nongkrong and abstractions of musical
content in Python. The nongkrong library offers two different render engines:

    (1) Kepatihan notation via Latex (nongkrong.render.notation)
            -> render_score method
    (2) Soundfiles via Pianoteq and cSound (nongkrong.render.sound)
            -> render_sound method

The tree-like structure of nongkrong.score.score can be sketched down as:
    Score <- Section <- ((Instrument, MDC, Dynamics), TimeFlow, Tempo, ...)
meaning a Score contains one or several Section - objects,
while a Section contains one or several ((Instrument, MDC, ...), ...) objects.
"""


class Score(object):
    def __init__(self, name, *section) -> None:
        pass

    def render_score(self) -> None:
        pass

    def render_sound(self) -> None:
        pass


class SectionMaker(abc.ABC):
    def __init__(
        self,
        name: str,
        cadences_per_player: dict,
        timeflow: metre.TimeFlow,
        tempo: attractors.TempoLine = None,
        repetition: attractors.RepetitionLine = None,
        delay: attractors.DelayLine = None,
    ) -> None:
        self.__name = name
        pass

    @abc.abstractproperty
    def players(self):
        raise NotImplementedError

    @property
    def name(self) -> str:
        return str(self.__name)

    def render_score(self) -> None:
        notation.render()
        pass

    def render_sound(self) -> None:
        sound.render()
        pass


class MDC(object):
    """"Metre-divided Cadence (MDC).

    MDC describes a cadence that is hierarchically divided by the structure of a
    nongkrong.metre.TimeFlow object. This structure can be sketched down as:
        TIMEFLOW <- METRE <- COMPOUND <- UNIT <- ELEMENT
    where the highest level (TIMEFLOW) contains one or several METRE, one
    METRE contains one or several COMPOUND, etc.

    One Element is the smallest unit. Every ELEMENT represents excatly one beat.

    One Element could be:
        1. A harmony -> for instance (ji.r(1, 1), ji.r(3, 2)) or (ji.r(7, 4),)
        2. A rest (represented by an empty harmony) -> ()
        3. A deeper rhythmical division where one beat gets further divided in
            smaller Elements. This is represented with a tuple that contains
            exactly two elements -> ((...), (...)). Each of those elements can
            be (1) A harmony, (2) A rest or (3) a deeper rhythmical division.
            The internal limit of how deep a beat can be divided is 4 divisions
            / 16 Elements per beat.

    To initalise a new MDC, you need an mu.sco.old.Cadence objects, its respective
    TimeFlow and the time_level, with which the Cadence shall be interpreted. The
    class will automatically divide the Cadence and generate through the division
    a new MDC object. The time level argument sets what a unit of 1 delay or 1
    duration in Cadence.delay or Cadence.duration is supposed to mean.

    For
        ...time_lv == 0 -> 1 in cadence.delay equals one element in metre.Unit
        ...time_lv == 1 -> 1 in cadence.delay equals one metre.Unit
        ...time_lv == 2 -> 1 in cadence.delay equals one metre.Compound
        ...time_lv == 3 -> 1 in cadence.delay equals one metre.Metre

    Rhythmical values smaller than 1 are only allowed with time_lv == 0. Those
    values have to have the form
                        m * [1 / (2 ** x)].
    Therefore tuplets are not possible.

    Finally there is one last additional argument when initalising a MDC named
    is_pitch_sustained. It's of type bool (True or False) and changes the way
    how the translation function from cadence to Metre-divided-cadence works.
    For Instruments with a continous sustain (Flute, Bowed String, ...), the
    expected input is 'True', while Instruments with a disappearing tone (Drums,
    Xylophones, Plucked Strings) are expected to get the input 'False'.

    With input 'True' every event of the transforming cadence will only be set
    at the specific metrical starting point of a Chord or Tone while every other
    point will become transformed to a Rest (mel.TheEmptyPitch). In the translation
    method "convert2cadence" those rests will be deleted for a legato Interpretation.

    With input 'False' every event will become valid for its whole duration.
    Rests will stay rests: if there is a rest between two elements those
    two elements won't be played legato but with an interruption.
    """

    def __init__(
        self,
        cadence: old.Cadence,
        time_flow: metre.TimeFlow,
        time_lv: int = 0,
        is_pitch_sustained: bool = False,
    ):
        # testing if input is valid
        MDC.is_valid_time_lv(time_lv)
        MDC.is_cadence_as_long_as_timeflow(cadence, time_flow, time_lv)
        MDC.are_delay_values_of_cadence_valid(cadence, time_lv)

        # building inner structure
        self.__is_pitch_sustained = is_pitch_sustained
        self.__structure = self.convert_input2structure(cadence, time_flow, time_lv)

    @staticmethod
    def is_valid_time_lv(time_lv: int) -> None:
        try:
            assert time_lv in (0, 1, 2, 3)
        except AssertionError:
            msg = "time_lv has to be 0 (element), 1 (unit),  2 (compound) or 3 (metre)."
            raise ValueError(msg)

    @staticmethod
    def is_cadence_as_long_as_timeflow(
        cadence: old.Cadence, time_flow: metre.TimeFlow, time_lv: int
    ) -> None:
        try:
            real = sum(cadence.delay)
            if time_lv == 0:
                expected = time_flow.size
            elif time_lv == 1:
                expected = time_flow.unit_amount
            elif time_lv == 2:
                expected = time_flow.compound_amount
            elif time_lv == 3:
                expected = time_flow.metre_amount
            assert real == expected
        except AssertionError:
            msg = "Cadence has to be as long as its respective TimeFLow - object."
            msg += " Cadence duration: {0}. Expected duration {1}.".format(
                real, expected
            )
            raise ValueError(msg)

    @staticmethod
    def detect_division_depth_of_rhythmical_value(value: float) -> tuple:
        depth = tuple(1 / (2 ** (i + 1)) for i in range(4))
        for i in range(16):
            i += 1
            if value / i in depth:
                return depth, i

        msg = "Rhythmical Value {0} doesn't have the form (1 / 2**x) * m ".format(value)
        msg += "or is deeper than four divisions."
        raise ValueError(msg)

    @staticmethod
    def are_delay_values_of_cadence_valid(cadence: old.Cadence, time_lv: int) -> None:
        if time_lv > 0:
            for idx, delay in enumerate(cadence.delay):
                if int(delay) != float(delay):
                    msg = "For time_lv != 0 no rhythmical values containing steps < 1 "
                    msg += "are allowed. "
                    msg += "Delay {0} has forbidden value {1}.".format(idx, delay)
                    raise ValueError(msg)
        if time_lv == 0:
            for idx, delay in enumerate(cadence.delay):
                diff = float(delay) - int(delay)
                if diff:
                    MDC.detect_division_depth_of_rhythmical_value(diff)

    def divide_cadence_by_groups(self, cadence: old.Cadence, groups: tuple) -> tuple:
        def divide_recursively(
            remaining_cadence, remaining_groups, divided_cadences: list = []
        ) -> list:
            if remaining_cadence:
                new_cadence = type(remaining_cadence)([])
                surplus_element = None
                group_size = remaining_groups[0]
                acc = 0
                for idx, item in enumerate(remaining_cadence):
                    size = float(item.delay)
                    acc += size
                    if acc == group_size:
                        new_cadence.append(item)
                        break
                    elif acc < group_size:
                        new_cadence.append(item)
                    elif acc > group_size:
                        diff = acc - group_size
                        item0 = item.copy()
                        item0.delay -= diff
                        item0.duration -= diff
                        item1 = item.copy()
                        item1.delay = diff
                        item1.duration = diff
                        if self.is_pitch_sustained is False:
                            item1.pitch = ji.JIHarmony([])
                        new_cadence.append(item0)
                        surplus_element = item1
                        break
                divided_cadences.append(new_cadence)
                remaining_cadence = remaining_cadence[idx + 1 :]
                if surplus_element is not None:
                    remaining_cadence.insert(0, surplus_element)
                return divide_recursively(
                    remaining_cadence, remaining_groups[1:], divided_cadences
                )
            else:
                return divided_cadences

        return tuple(divide_recursively(cadence, groups, []))

    def divide_unit_by_elements(self, cadence) -> tuple:
        def divide_recursively(cadence, size=1):
            duration = float(cadence.duration)
            beats = duration / size
            try:
                assert float(beats) == int(beats)
            except AssertionError:
                msg = "{0} beats for size {1} in cadence {2}.".format(
                    beats, size, cadence
                )
                msg += " Attribute 'beats' has to be an integer number."
                raise ValueError(msg)
            beats = int(beats)
            group = tuple(size for i in range(beats))
            divided = self.divide_cadence_by_groups(cadence, group)
            result = []
            for div in divided:
                if len(div) == 1:
                    p = div[0].pitch
                    if len(p) == 0:
                        p = mel.TheEmptyPitch
                    result.append(p)
                else:
                    result.append(divide_recursively(div, size / 2))
            if size < 1:
                assert len(result) == 2
                if result[1] == mel.TheEmptyPitch and type(result[0]) != tuple:
                    return result[0]
            return tuple(result)

        return divide_recursively(cadence)

    def convert_input2structure(
        self, cadence: old.Cadence, time_flow: metre.TimeFlow, time_lv: int
    ) -> tuple:
        def recursive_divider(cadence, nested_structure, time_line) -> tuple:
            if nested_structure:
                structure = nested_structure[0]
                items = getattr(time_line, structure)
                sizes = getattr(time_line, "{0}_size".format(structure))
                divided_cadences = self.divide_cadence_by_groups(cadence, sizes)
                return tuple(
                    recursive_divider(cadence, nested_structure[1:], tl)
                    for cadence, tl in zip(divided_cadences, items)
                )
            else:
                return self.divide_unit_by_elements(cadence)

        # in case time_lv != 0, convert the cadences time values
        # (delay / duration) to the basic elementar lv
        if time_lv > 0:
            if time_lv == 3:
                size_per_item = time_flow.metre_size
            elif time_lv == 2:
                size_per_item = time_flow.compound_size
            elif time_lv == 1:
                size_per_item = time_flow.unit_size
            else:
                raise ValueError("Invalid time_lv {0}".format(time_lv))
            delays = tuple(float(d) for d in cadence.delay)
            delays_acc = tuple(
                int(item) for item in itertools.accumulate((0,) + delays)
            )
            for idx, start, end in zip(range(len(cadence)), delays_acc, delays_acc[1:]):
                cadence.delay[idx] = sum(size_per_item[start:end])
                cadence.dur[idx] = cadence.delay[idx]

        return recursive_divider(cadence, time_flow.nested_structure, time_flow)

    def convert2cadence(self, dynamics, tempo, repetitions, delays) -> old.JICadence:
        """
        """
        pass

    @property
    def is_pitch_sustained(self) -> bool:
        return self.__is_pitch_sustained

    def __repr__(self) -> str:
        return str(self.__structure)

    def __getitem__(self, idx) -> tuple:
        return tuple(self.__structure[idx])

    def flat(self) -> tuple:
        pass

    def divide_by_notation(self, instrument) -> tuple:
        pass

    def divide_by_sound_engine(self, instrument) -> tuple:
        pass


class MDNC(object):
    def __init__(self, mdc, pitch2notation):
        pass
