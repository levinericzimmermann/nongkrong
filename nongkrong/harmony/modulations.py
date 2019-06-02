from nongkrong.harmony import modes


import abc


class AbstractModulation(abc.ABC):
    @abc.abstractmethod
    def __call__(self, mode, genesis) -> modes.Mode:
        raise NotImplementedError


class __ElementarModulation(AbstractModulation):
    def __init__(self, dict2grab) -> None:
        self.__dict2grab = dict2grab

    def __repr__(self) -> str:
        return "MOD: {0}".format(self.__dict2grab)

    def __eq__(self, other) -> bool:
        try:
            return self.__dict2grab == other.__dict2grab
        except AttributeError:
            return False

    def __call__(self, mode, genesis) -> modes.Mode:
        return getattr(genesis, self.__dict2grab)(mode)


ModOriginal = __ElementarModulation("mode")
ModParallel = __ElementarModulation("parallel")
ModLeftNeighbour = __ElementarModulation("left_neighbour")
ModRightNeighbour = __ElementarModulation("right_neighbour")
ModOpposite = __ElementarModulation("opposite")


class CompoundModulation(AbstractModulation):
    def __init__(self, *step):
        self.__steps = tuple(step)

    def __repr__(self) -> str:
        return "Compound_MOD: {0}".format(str(self.__steps))

    def __call__(self, mode, genesis) -> modes.Mode:
        for mod in self.__steps:
            mode = mod(mode, genesis)
        return mode

    def __eq__(self, other):
        try:
            if len(self.__steps) == 1 and type(other) == __ElementarModulation:
                return self.__steps[0] == other
            else:
                return self.__steps == other.__steps
        except AttributeError:
            return False
