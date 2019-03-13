from nongkrong.harmony import modes

import itertools


class Genesis(object):
    """Genesis implements the basic tuning of the complete composition.

    To initalise a Genesis object four prime numbers (a, b, c and d)
    are necessary. Each of those numbers has to be unique, repetitions
    are forbidden. Those four prime numbers are the basis of the
    melodic hexany (cps-scale).

    The Genesis - object contains all modes for the specific properties.
    The modes can be reached via the different index functions
    (modes, parallel, left_neighbour, right_neighbour and opposite).
    Those index functions expect
        a) another mode object
        b) a string, that symbolize a mode. The form of this string is
            * "a+b+c" for positve modes
            * "a-b-c" for negative modes
    """

    def __init__(self, a, b, c, d) -> None:
        self.__primes = tuple(sorted((a, b, c, d)))

        try:
            assert len(self.__primes) == len(set(self.__primes))
        except AssertionError:
            msg = "Each input value has to be unique. "
            msg += "Repetitions are not allowed!"
            raise ValueError(msg)

        self.__raw_modes = Genesis.__mk_modes(self.__primes)
        self.__modes = Genesis.__mk_dict(self.__raw_modes, lambda m, gen_modes: m)
        self.__parallel = Genesis.__mk_dict(self.__raw_modes, Genesis.__detect_parallel)
        self.__left_neighbour = Genesis.__mk_dict(
            self.__raw_modes, Genesis.__detect_left_neighbour
        )
        self.__right_neighbour = Genesis.__mk_dict(
            self.__raw_modes, Genesis.__detect_right_neighbour
        )
        self.__opposite = Genesis.__mk_dict(self.__raw_modes, Genesis.__detect_opposite)

    @property
    def __key(self) -> tuple:
        return tuple(self.__primes)

    def __repr__(self) -> str:
        return str("GENESIS: {0}|{1}|{2}|{3}".format(*self.__key))

    @staticmethod
    def __mk_modes(primes) -> tuple:
        combinations = itertools.combinations(primes, 3)
        gen_modes = []
        for combination in combinations:
            N = [p for p in primes if p not in combination][0]
            for permutation in itertools.permutations(combination):
                gen_modes.extend(
                    tuple(modes.Mode(*permutation, N, b) for b in (True, False))
                )
        return tuple(gen_modes)

    @staticmethod
    def __mk_dict(modes, assignment_function) -> dict:
        d = {}
        for mode in modes:
            key = assignment_function(mode, modes)
            d.update({k: mode for k in (key, repr(key))})
        return d

    @staticmethod
    def __detect_parallel(current_mode, all_modes) -> modes.Mode:
        for mode in all_modes:
            tests = (
                mode.x == current_mode.x,
                mode.y == current_mode.y,
                mode.z != current_mode.z,
                mode.gender == current_mode.gender,
            )
            if all(tests):
                return mode
        raise ValueError(
            "Parallel mode couldn't be found for {0}!".format(current_mode)
        )

    @staticmethod
    def __detect_left_neighbour(current_mode, all_modes) -> modes.Mode:
        for mode in all_modes:
            tests = (
                mode.x == current_mode.y,
                mode.y == current_mode.x,
                mode.z == current_mode.z,
                mode.gender == current_mode.gender,
            )
            if all(tests):
                return mode
        raise ValueError(
            "Left neighbour mode couldn't be found for {0}!".format(current_mode)
        )

    @staticmethod
    def __detect_right_neighbour(current_mode, all_modes) -> modes.Mode:
        for mode in all_modes:
            tests = (
                mode.x == current_mode.x,
                mode.y == current_mode.z,
                mode.z == current_mode.y,
                mode.gender == current_mode.gender,
            )
            if all(tests):
                return mode
        raise ValueError(
            "Right neigbour mode couldn't be found for {0}!".format(current_mode)
        )

    @staticmethod
    def __detect_opposite(current_mode, all_modes) -> modes.Mode:
        for mode in all_modes:
            tests = (
                mode.x == current_mode.x,
                mode.y == current_mode.y,
                mode.z == current_mode.z,
                mode.gender != current_mode.gender,
            )
            if all(tests):
                return mode
        raise ValueError(
            "Opposite mode couldn't be found for {0}!".format(current_mode)
        )

    def mode(self, key) -> modes.Mode:
        """Return corresponding mode."""
        return self.__modes[key]

    def parallel(self, key) -> modes.Mode:
        """Return parallel mode of the input key.

        The parallel mode is defined as
        a|b|c -> a|b|d.
        Eg. 3+7+5 -> 3+7+9
        """
        return self.__parallel[key]

    def left_neighbour(self, key) -> modes.Mode:
        """Return left neighbour of the input key.

        The left neighbour of a mode is defined as
        a|b|c -> b|a|c.
        Eg. 3+7+5 -> 7+3+5
        """
        return self.__left_neighbour[key]

    def right_neighbour(self, key) -> modes.Mode:
        """Return right neighbour of the input key.

        The right neighbour of a mode is defined as
        a|b|c -> a|c|b.
        Eg. 3+7+5 -> 3+5+7
        """
        return self.__right_neighbour[key]

    def opposite(self, key) -> modes.Mode:
        """Return opposite mode of the input key.

        An opposite mode is defined as the same mode in the
        inverse gender.
        Eg. 3+7+5 -> 3-7-5
        """
        return self.__opposite[key]
