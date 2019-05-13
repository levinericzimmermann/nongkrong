from nongkrong.render import notation


class Delay(object):
    def __init__(
        self,
        duration: float,
        thickness: float = None,
        color: str = None,
        amount_lines: int = None,
    ):
        self.__duration = duration
        self.__thickness = thickness
        self.__color = color
        self.__amount = amount_lines

    @property
    def duration(self) -> float:
        return self.__duration

    @property
    def thickness(self) -> float:
        return self.__thickness

    @property
    def color(self) -> str:
        return self.__color

    @property
    def amount_lines(self) -> int:
        return self.__amount

    def adapt_vertical_line(
        self, vertical_line: notation.VerticalLine
    ) -> notation.VerticalLine:
        if self.thickness:
            thickness = self.thickness
        else:
            thickness = vertical_line.thickness
        if self.color:
            color = self.color
        else:
            color = vertical_line.color
        if self.amount_lines:
            amount_lines = self.amount_lines
        else:
            amount_lines = vertical_line.amount
        return notation.VerticalLine(thickness, color, amount_lines)
