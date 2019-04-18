import abc

from nongkrong.attractors import attractors
from nongkrong.metre import metre
from nongkrong.render import notation
from nongkrong.render import sound


"""This module implements classes to organise compositions in hierarchical structures.

The tree-like structure can be sketched down as:
    Score <- Section <- Player <- Instrument
meaning
      a Score contains one or several Section - objects,
while a Section contains one or several Player - objects
while a Player contains one or several Instrument - objects.

Score and Section objects can render scores via lilypond (nongkrong.render.notation)
and sounds via pianoteq and csound (nongkrong.render.sound).
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

    def swallow(self, section: "SectionFactory") -> "Section":
        pass

    def get_unit_idx(self, metre_idx, compound_idx, unit_idx) -> int:
        pass

    def get_pitch(
        self, player: str, metre: int, compound: int, unit: int, element: int
    ):
        pass

    def get_nth_pitch(self, player, pitch):
        pass
