import abc
import numpy as np

from nongkrong.render import notation


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
        for usize, item in zip(time_flow.unit_size, self.__content):
            if item:
                local_tempo = item.calculate_tempo(current_tempo)
                current_tempo = local_tempo[1]
            else:
                local_tempo = (current_tempo,) * 2
            interpolation = np.linspace(
                local_tempo[0],
                local_tempo[1],
                usize * self.divisions_per_element,
                dtype=float,
            )
            data.append(tuple(interpolation))
        return tuple(data)

    def convert2latex_per_unit(self, time_flow) -> tuple:
        data = []
        for counter, usize, item in zip(
            range(len(self.__content)), time_flow.unit_size, self.__content
        ):
            if item:
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

    def calculate_tempo(self, prior_tempo=1) -> tuple:
        return self.factor, self.factor

    def mk_latex_content(self, unitsize: int, msg_before=None) -> tuple:
        name = r"\textit{" + self.name + r"}}"
        return notation.MultiColumn(name, unitsize), len(self.name)


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

    def calculate_tempo(self, prior_tempo=1) -> tuple:
        return prior_tempo, self.factor * prior_tempo

    def mk_latex_content(self, unitsize: int, msg_before=None) -> tuple:
        if msg_before and msg_before == self.msg:
            msg = r"+"
        else:
            msg = self.msg
        return (msg,) + ((r"+",) * (unitsize - 1)), unitsize
