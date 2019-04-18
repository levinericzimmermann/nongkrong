from nongkrong.render import notation

# from nongkrong.render.sound import synthesis


class Instrument(object):
    """An Instrument contains one or several ways to make sounds and to notate music.

    One Instrument is connected to one person, who is supposed to play the respective
    instrument(s). The definition of instrument is therefore rather broad, meaning not
    only one specific way to make a sound (hitting one drum) is meant, but rather a
    whole set of bodies, with which a player can produce music. For instance a drum
    set, with Snare drum, Bass drum and a cymbal would be considered as one instrument,
    since it can be played by one person.

    The different sounds are descriped with SoundEngine objects, that can be passed
    down as a tuple when initiating the object. For every type of sound there will
    also be a specific HorizontalLine - object, in which the respective pitches
    of the different sound sources will be notated.

    The pitches of the incoming cadence will be distributed with the help of
    a pitch2notation dict that has to be passed down during initialisation.
    The keys of this dictionary contains Pitch - objects, while its corresponding
    values are made from two-element tuples. The first element is an integer
    that equals the index of the sound source that shall be played if this pitch
    occurs. The second index is a string, that shall occur in the notation at
    the respecitve position.

    Last but not least every Instrument object also needs a specific
    VerticalLineStyle - object and a unique name. First one sets the style
    for the different visual metrical separator and second one helps
    to distinguish different instruments in a Section.
    """

    def __init__(
        self,
        name: str,
        pitch2notation: dict,
        horizontal_lines: tuple,
        vertical_line_style: notation.VerticalLineStyle,
        sound_engines: tuple,
    ):
        self.__len_engines = len(sound_engines)
        try:
            assert len(horizontal_lines) == self.__len_engines
        except AssertionError:
            msg = "There has to be as many sound engines as there are notation lines."
            raise ValueError(msg)

        self.__name = name
        self.__available_pitches = tuple(sorted(pitch2notation.keys()))
        self.__pitch2notation = pitch2notation
        self.__horizontal_lines = horizontal_lines
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
    def horizontal_lines(self) -> tuple:
        return self.__horizontal_lines

    @property
    def vertical_line_style(self) -> tuple:
        return self.__vertical_line_style

    def convert_mdc2mdnc(self, mdc) -> tuple:
        lines = [[]] * self.__len_engines
        for metre in mdc:
            metre_per_line = [[]] * self.__len_engines
            for compound in metre:
                compound_per_line = [[]] * self.__len_engines
                for unit in compound:
                    unit_per_line = [[]] * self.__len_engines
                    for event in unit:
                        pass
                    for idx, upl in enumerate(unit_per_line):
                        compound_per_line[idx].append(upl)
                for idx, cpl in enumerate(compound_per_line):
                    metre_per_line[idx].append(cpl)
            for idx, mpl in enumerate(metre_per_line):
                lines[idx].append(mpl)
        return tuple(lines)

    def render_sound(
        self,
        name: str,
        mdc: tuple,
        dynamic=None,
        tempo=None,
        delay=None,
        repetition=None,
    ) -> None:
        mdc = repetition(delay(tempo(dynamic(mdc))))
        self.sound_engines(mdc)

    def render_score(
        self,
        name: str,
        mdc: tuple,
        dynamic=None,
        tempo=None,
        delay=None,
        repetition=None,
    ) -> None:
        mdnc = self.convert_mdc2mdnc(mdc)
        ln = notation.Notation(
            name, mdnc, dynamic, tempo, delay, repetition, self.notation_lines
        )
        ln.render()

    def render(
        self,
        name: str,
        mdc: tuple,
        dynamic=None,
        tempo=None,
        delay=None,
        repetition=None,
    ) -> None:
        self.render_sound(name, mdc, dynamic, tempo, delay, repetition)
        self.render_score(name, mdc, dynamic, tempo, delay, repetition)
