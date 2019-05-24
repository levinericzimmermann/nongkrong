import abc
import numpy as np

from nongkrong.render import notation


def bpm2factor(bpm) -> float:
    return 60 / bpm


class TempoLine(object):
    divisions_per_element = 64

    def __init__(self, items):
        self.__content = items

    def __repr__(self) -> str:
        return str(self.__content)

    def __len__(self) -> int:
        return len(self.__content)

    def convert2tempo_per_unit(self, time_flow) -> tuple:
        data = []
        current_tempo = 1
        last_stable_tempo = 1
        for usize, item in zip(time_flow.unit_size, self.__content):
            if item:
                local_tempo = item.calculate_tempo(current_tempo, last_stable_tempo)
                current_tempo = local_tempo[1]
                if type(item) != ChangeTempo:
                    last_stable_tempo = current_tempo
            else:
                local_tempo = tuple(float(current_tempo) for i in range(2))

            interpolation = np.linspace(
                local_tempo[0],
                local_tempo[1],
                usize * self.divisions_per_element,
                dtype=float,
            )
            interpolation = tuple(
                item / self.divisions_per_element for item in interpolation
            )

            data.append(interpolation)
        return tuple(data)

    def convert2latex_per_unit(self, time_flow) -> tuple:
        data = []
        for counter, usize, item in zip(
            range(len(self.__content)), time_flow.unit_size, self.__content
        ):
            if item is not None:
                msg_before = None
                if counter > 0:
                    prior = self.__content[counter - 1]
                    if isinstance(prior, ChangeTempo):
                        msg_before = prior.msg
                content, amount_signs = item.mk_latex_content(usize, msg_before)
                has_content = True
            else:
                content = ("",) * usize
                amount_signs = 0
                has_content = False
            data.append((content, amount_signs, has_content))
        return tuple(data)


class AbstractTempo(abc.ABC):
    @abc.abstractmethod
    def calculate_tempo(self, prior_tempo=1) -> tuple:
        raise NotImplementedError

    @abc.abstractmethod
    def mk_latex_content(self, unitsize: int, msg_before: str) -> str:
        raise NotImplementedError


class SetTempo(AbstractTempo):
    def __init__(self, name: str, factor: float):
        self.__name = name
        self.__factor = factor

    @property
    def factor(self) -> float:
        return self.__factor

    @property
    def name(self) -> str:
        return self.__name

    def calculate_tempo(self, prior_tempo=1, last_stable_tempo=1) -> tuple:
        return self.factor, self.factor

    def mk_latex_content(self, unitsize: int, msg_before=None) -> tuple:
        name = r"\textit{" + self.name + r"}"
        return notation.MultiColumn(name, unitsize), len(self.name)


LARGHISSIMO = SetTempo("Larghissimo", bpm2factor(24))
LARGO = SetTempo("Largo", bpm2factor(45))
LENTO = SetTempo("Lento", bpm2factor(58))
ADAGIO = SetTempo("Adagio", bpm2factor(70))
ANDANTE = SetTempo("Andante", bpm2factor(90))
MODERATO = SetTempo("Moderato", bpm2factor(110))
ALLEGRO = SetTempo("Allegro", bpm2factor(133))
VIVACE = SetTempo("Vivace", bpm2factor(165))
PRESTO = SetTempo("Presto", bpm2factor(190))


class ChangeTempo(AbstractTempo):
    faster = r"\textit{acc.}"
    slower = r"\textit{rit.}"

    def __init__(self, factor: float):
        assert factor != 1
        self.__factor = factor

    @property
    def msg(self) -> str:
        if self.factor < 1:
            return self.faster
        else:
            return self.slower

    @property
    def factor(self) -> float:
        return self.__factor

    def calculate_tempo(self, prior_tempo=1, last_stable_tempo=1) -> tuple:
        return prior_tempo, self.factor * prior_tempo

    def mk_latex_content(self, unitsize: int, msg_before=None) -> tuple:
        if msg_before and msg_before == self.msg:
            msg = r"+"
        else:
            msg = self.msg
        return (msg,) + ((r"+",) * (unitsize - 1)), unitsize


class __ATempo(AbstractTempo):
    def __init__(self):
        self.__name = r"\textit{A tempo}"

    def calculate_tempo(self, prior_tempo=1, last_stable_tempo=1) -> tuple:
        return last_stable_tempo, last_stable_tempo

    def mk_latex_content(self, unitsize: int, msg_before=None) -> tuple:
        return notation.MultiColumn(self.__name, unitsize), len("A tempo")


ATEMPO = __ATempo()
