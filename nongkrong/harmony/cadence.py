from nongkrong.harmony import functions
from nongkrong.harmony import genesis
from nongkrong.harmony import modes
from nongkrong.harmony import modulations


class Cadence(object):
    def __init__(
        self,
        functions: tuple,
        modulation: modulations.AbstractModulation = modulations.ModOriginal,
        time: tuple = None,
    ) -> None:
        self.__functions = tuple(functions)
        self.__modulations = tuple(modulation for func in functions)
        if not time:
            time = tuple(None for func in functions)
        self.__time = time

    @property
    def functions(self):
        return self.__functions

    @property
    def time(self):
        return self.__time

    def __repr__(self) -> str:
        mod = self.__modulations[0]
        representation = "["
        for modulation, function, time in zip(
            self.__modulations, self.__functions, self.__time
        ):
            if modulation != mod:
                representation = representation[:-1]
                representation += "] ["
                mod = modulation
            rep_func = repr(function)
            if time:
                rep_func += str(time)
            representation += rep_func + " "
        representation = representation[:-1]
        representation += "]"
        return representation

    def __len__(self) -> int:
        return len(self.__functions)

    def __eq__(self, other) -> bool:
        try:
            tests = (
                self.__functions == other.__functions,
                self.__modulations == other.__modulations,
                self.__time == other.__time,
            )
            return all(tests)
        except AttributeError:
            return False

    def __getitem__(self, idx):
        return self.__functions[idx]

    @staticmethod
    def convert_str2functions(string) -> tuple:
        """Converts string to function objects.

        String is expected to have the form
        FUNC0 FUNC1 FUNC2 ...
        (functions seperated by space)
        For instance:
            "M o m n w o ox o M"
        """
        keys = string.split(" ")
        return tuple(functions.FUNCTIONS[key] for key in keys)

    @classmethod
    def from_str(cls, string) -> "Cadence":
        functions = Cadence.convert_str2functions(string)
        return cls(functions)

    @classmethod
    def from_file(cls, name) -> "Cadence":
        with open(name, "r") as f:
            return Cadence.from_str(f)

    @property
    def appearing_modulations(self) -> tuple:
        before = self.__modulations[0]
        collection = [before]
        for mod in self.__modulations:
            if mod != before:
                collection.append(mod)
                before = mod
        return tuple(collection)

    def add(
        self, functions: tuple, modulation=modulations.ModOriginal, time: tuple = None
    ) -> None:
        self.__functions += tuple(functions)
        self.__modulations += tuple(modulation for func in functions)
        if not time:
            time = tuple(None for func in functions)
        self.__time += time

    def insert(
        self,
        idx: int,
        functions: tuple,
        modulation=modulations.ModOriginal,
        time: tuple = None,
    ) -> None:
        if not time:
            time = tuple(None for func in functions)
        self.__functions = self.__functions[:idx] + functions + self.__functions[idx:]
        mod = tuple(modulation for func in functions)
        self.__modulations = self.__modulations[:idx] + mod + self.__modulations[idx:]
        self.__time = self.__time[:idx] + time + self.__time[idx:]

    def init_time(self, time: tuple):
        try:
            assert len(time) == len(self)
        except AssertionError:
            raise ValueError(
                "There has to be as many time arguments as there are functions"
            )
        self.__time = time

    def convert2pitches(self, mode: modes.Mode, gen: genesis.Genesis) -> tuple:
        modes = tuple(mod(mode, gen) for mod in self.__modulations)
        return tuple(func(mode) for func, mode in zip(self.__functions, modes))

    def convert2real_time(self, metre) -> tuple:
        pass

    def copy(self) -> "Cadence":
        return type(self)(
            tuple(self.__functions), tuple(self.__modulations), tuple(self.__time)
        )
