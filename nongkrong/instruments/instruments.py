from nongkrong.render import notation

import functools
import operator

# from nongkrong.render.sound import synthesis


class Instrument(object):
    """An Instrument contains one or several ways to make sounds and to notate music.

    One Instrument is connected to one person, who is supposed to play the respective
    instrument(s). The definition of instrument is therefore rather broad, meaning not
    only one specific way to make a sound is meant (hitting one drum), but rather a
    whole set of bodies, with which a player can produce music. For instance a drum
    set, with Snare drum, Bass drum and a cymbal would be considered as one instrument,
    since it can be played by one person.

    The different sounds are descriped with SoundEngine objects, that can be passed
    down as a tuple when initiating the object. For every type of sound there will
    also be a specific HorizontalLine - object, in which the respective pitches
    of the different sound sources will be notated.

    The pitches of the incoming cadence will be distributed with the help of
    a pitch2notation dict that has to be passed during initialisation.
    The keys of this dictionary contains Pitch - objects, while its corresponding
    values are tuples. Those tuples contain one element for one sound source. In this
    way the same pitch can be distributed to different sound sources. One element is
    made by two-element tuples. The first element is an integer
    that equals the index of the sound source that shall be played if this pitch
    occurs. The second index is a notation.Sign - object, that shall occur in
    the notation at the respective position.

    Last but not least every Instrument object also needs a specific
    VerticalLineStyle - object and a unique name. First one sets the style
    for the different visual metrical separator and second one helps
    to distinguish different instruments in a Section.
    """

    def __init__(
        self,
        name: str,
        pitch2notation: dict,
        horizontal_line_styles: tuple,
        sound_engines: tuple,
        vertical_line_style: notation.VerticalLineStyle,
    ):
        self.__len_engines = len(sound_engines)
        try:
            assert len(horizontal_line_styles) == self.__len_engines
        except AssertionError:
            msg = "There has to be as many sound engines as there are notation lines."
            raise ValueError(msg)

        self.__name = name
        self.__available_pitches = tuple(sorted(pitch2notation.keys()))
        self.__pitch2notation = pitch2notation
        self.__horizontal_line_styles = horizontal_line_styles
        self.__sound_engines = sound_engines
        self.__vertical_line_style = vertical_line_style

    @property
    def name(self) -> str:
        return self.__name

    @property
    def pitches(self) -> tuple:
        return tuple(self.__available_pitches)

    @property
    def pitch2notation(self) -> dict:
        return dict(self.__pitch2notation)

    @property
    def sound_engines(self) -> tuple:
        return self.__sound_engines

    @property
    def horizontal_line_styles(self) -> tuple:
        return self.__horizontal_line_styles

    @property
    def vertical_line_style(self) -> tuple:
        return self.__vertical_line_style


def mk_p2n(pitches: tuple, instr_number: int, autosort=True) -> dict:
    if autosort:
        pitches = tuple(sorted(pitches))
    return {
        pitch: ((instr_number, notation.SIGN_NUMBERS[idx]),)
        for idx, pitch in enumerate(pitches)
    }


def combine_p2n(*p2n):
    def detect_value(p2n, key):
        values = []
        for p2 in p2n:
            if key in p2.keys():
                values.extend(p2[key])
        return tuple(values)

    keys = functools.reduce(operator.add, tuple(tuple(p2.keys()) for p2 in p2n))
    return {key: detect_value(p2n, key) for key in keys}
