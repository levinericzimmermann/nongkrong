class TimeFlow(object):
    def __init__(self, *metre):
        self.__metres = tuple(metre)
        pass

    @property
    def amount_compounds(self) -> int:
        return sum(len(m) for m in self.__metres)

    @property
    def amount_units(self) -> int:
        return sum(m.amount_units for m in self.__metres)


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

    @property
    def amount_units(self) -> int:
        return sum(len(c) for c in self.__compounds)


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
