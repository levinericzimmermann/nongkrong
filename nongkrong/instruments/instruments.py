from nongkrong.render import notation
# from nongkrong.render.sound import synthesis


class Instrument(object):
    """An Instrument helps to generate soundfiles and scores from cadences.
    """

    def __init__(
        self,
        name: str,
        pitch2notation: dict,
        notation_lines: tuple,
        vertical_line_style: notation.VerticalLineStyle,
        sound_engines: tuple,
    ):
        self.__len_engines = len(sound_engines)
        try:
            assert len(notation_lines) == self.__len_engines
        except AssertionError:
            msg = "There has to be as many sound engines as there are notation lines."
            raise ValueError(msg)

        self.__name = name
        self.__available_pitches = tuple(sorted(pitch2notation.keys()))
        self.__pitch2notation = pitch2notation
        self.__notation_lines = notation_lines
        self.__sound_engines = sound_engines

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
    def sound_engine(self) -> dict:
        return self.__sound_engine

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
        self.sound_engine(mdc)

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
