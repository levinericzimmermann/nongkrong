from mu.sco import old

from nongkrong.harmony import modes


class Splinter(object):
    def __init__(
        self, rhythmic_structure: tuple, low: str, middle: str, high: str
    ) -> None:
        self.__rhythmic_structure = rhythmic_structure
        self.__low = tuple(
            "." + info if info != "o" else info
            for info in Splinter.convert_to_items(low)
        )
        self.__middle = Splinter.convert_to_items(middle)
        self.__high = tuple(
            info + "." if info != "o" else info
            for info in Splinter.convert_to_items(high)
        )

        duration = rhythmic_structure[0] * rhythmic_structure[1]

        assert len(self.__low) == duration
        assert len(self.__middle) == duration
        assert len(self.__high) == duration

        self.__duration = duration

    @property
    def duration(self):
        return self.__duration

    @property
    def low(self) -> tuple:
        return self.__low

    @property
    def middle(self) -> tuple:
        return self.__middle

    @property
    def high(self) -> tuple:
        return self.__high

    @staticmethod
    def convert_to_items(line) -> tuple:
        return tuple(info for info in line.split(" ") if info)

    @staticmethod
    def convert2line(solution: dict, keys: tuple) -> tuple:
        pitches = (solution[key] for key in keys)
        return tuple(
            old.Melody(old.Tone(p, 1) for p in pitches).tie_pauses().discard_rests()
        )

    def solve(self, solution: dict) -> tuple:
        return tuple(
            Splinter.convert2line(solution, keys)
            for keys in (self.low, self.middle, self.high)
        )

    @property
    def rhythmic_structure(self) -> tuple:
        return self.__rhythmic_structure

    @property
    def density(self) -> float:
        def detect_density_for_line(line):
            return len(tuple(item for item in line if item != "o")) / self.duration

        summed = sum(
            detect_density_for_line(line) for line in (self.low, self.middle, self.high)
        )
        return summed / 3


class Pattern(object):
    def __init__(self, *splinter: Splinter) -> None:
        rs = splinter[0].rhythmic_structure
        for idx, s in enumerate(splinter[1:]):
            try:
                assert s.rhythmic_structure == rs
            except AssertionError:
                msg = "All Splinter have to have the same rhythmic_structure."
                msg = "Splinter {0} has the different structure {1}.".format(
                    idx + 1, s.rhythmic_structure
                )
                raise ValueError(msg)

        self.__rhythmic_structure = rs
        self.__splinter = splinter

    @property
    def rhythmic_structure(self) -> tuple:
        return self.__rhythmic_structure

    @property
    def size(self) -> int:
        return len(self.__splinter)

    @property
    def parts(self) -> tuple:
        return self.__splinter


class PatternEnvironment(object):
    def __init__(self, *pattern: Pattern) -> None:
        pass

    def solve(
        self, a: int, b: int, x: int, expansions: tuple, mode: modes.Mode
    ) -> tuple:
        pass
