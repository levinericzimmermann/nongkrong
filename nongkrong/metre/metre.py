class TimeFlow(object):
    def __init__(self, *metre):
        self.__metres = tuple(metre)
        pass

    @property
    def len_metres(self) -> int:
        return sum(len(m) for m in self.__metres)

    def make_mdc(self, cadence, time_lv=0) -> tuple:
        try:
            assert time_lv in (0, 1, 2, 3)
        except AssertionError:
            msg = "time_lv has to be 0 (element), 1 (unit),  2 (compound) or 3 (metre)."
            raise ValueError(msg)

        try:
            real = sum(cadence.delay)
            if time_lv == 0:
                expected = self.size
            elif time_lv == 1:
                expected = self.amount_units
            elif time_lv == 2:
                expected = self.amount_compounds
            elif time_lv == 3:
                expected = self.amount_metres
            assert real == expected
        except AssertionError:
            msg = "Cadence has to be as long as the TimeFLow - object."
            msg += " Cadence duration: {0}. Expected duration {1}.".format(
                real, expected
            )
            raise ValueError(msg)


class Metre(object):
    def __init__(self, *compound):
        self.__compounds = tuple(compound)

    def __repr__(self) -> str:
        return str(self.__compounds)

    def __getitem__(self, idx) -> "Compound":
        return self.__compounds[idx].copy()

    def __setitem__(self, idx, compound) -> "Metre":
        pass

    def flat(self) -> tuple:
        pass

    def copy(self) -> "Metre":
        pass

    def reverse(self) -> "Metre":
        pass

    def append(self, compound) -> "Metre":
        pass

    def insert(self, idx, compound) -> "Metre":
        pass

    @property
    def size(self) -> int:
        pass


class Compound(object):
    def __init__(self, *unit):
        self.__units = tuple(unit)

    @property
    def size(self) -> int:
        pass

    def copy(self) -> "Compound":
        pass


class Unit(object):
    def __init__(self, size: int):
        self.__size = size

    @property
    def size(self) -> int:
        return self.__size
