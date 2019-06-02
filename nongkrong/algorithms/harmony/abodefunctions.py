from nongkrong.harmony import abodefunctions
from nongkrong.harmony import functions
from nongkrong.harmony import modes
from nongkrong.harmony import subfunctions


import functools
import operator
import itertools


def __mk_detect_af_frame_lancaran():
    """Generate function that return 2-element tuple.
    Each element represents one abodefunction. One element is
    composed by one 2-element-tuple, where those elements contain:
        1. Prime number of mode that shall be played (x, y, z or U)
        2. real AbodeFunction object

    necessary input:
        mode: modes.Mode, next_mode: modes.Mode, functions: tuple, idx0: int
    """

    resolution_dict = {
        ("M", "m"): (False, True),
        ("m", "M"): (True, False),
        ("m", "m"): (True, True),
        ("w", "w"): (True, True),
        ("o", "o"): (True, True),
        ("n", "n"): (False, False),
        ("om", "om"): (True, True),
        ("ow", "ow"): (True, True),
    }

    resolution_dict = {
        tuple(functions.FUNCTIONS[fn] for fn in key): resolution_dict[key]
        for key in resolution_dict
    }

    def find_primes(mode, func0, func1) -> tuple:
        return abodefunctions.AbodefuncLine.get_primes(mode, func0, func1)

    def detect_abodefunctions_frame_lancaran(
        mode: modes.Mode, next_mode: modes.Mode, funcs: tuple, idx0: int
    ) -> tuple:

        idx1 = idx0 + 1
        func0, func1 = funcs[idx0], funcs[idx1]
        primes = find_primes(mode, func0, func1)

        prime_i = primes[0]

        try:
            resolution = resolution_dict[(func0, func1)]
        except KeyError:
            msg = "Functions {0} and {1}: ".format(func0, func1)
            msg += "No AbodeFunction - resolution has been defined for "
            msg += "this particular combination."
            raise NotImplementedError(msg)

        result = []
        for r in resolution:
            if r:
                af = abodefunctions.ABODEFUNCTIONS["i"]
            else:
                af = abodefunctions.ABODEFUNCTIONS["i00"]
            result.append((prime_i, af))

        return tuple(result)

    return detect_abodefunctions_frame_lancaran


def __mk_interpolate_from_i_to_i_func():
    cycle_2 = itertools.cycle(
        (
            (
                abodefunctions.ABODEFUNCTIONS["i"],
                abodefunctions.ABODEFUNCTIONS["i_to_j"],
            ),
            (
                abodefunctions.ABODEFUNCTIONS["i"],
                abodefunctions.ABODEFUNCTIONS["i_off_j"],
            ),
        )
    )

    cycle_3_strong = itertools.cycle(
        (
            (
                abodefunctions.ABODEFUNCTIONS["i"],
                abodefunctions.ABODEFUNCTIONS["i0"],
                abodefunctions.ABODEFUNCTIONS["i_to_j"],
            ),
            (
                abodefunctions.ABODEFUNCTIONS["i"],
                abodefunctions.ABODEFUNCTIONS["i0"],
                abodefunctions.ABODEFUNCTIONS["i_off_j"],
            ),
        )
    )

    cycle_3_weak = itertools.cycle(
        (
            (
                abodefunctions.ABODEFUNCTIONS["i"],
                abodefunctions.ABODEFUNCTIONS["i_off_j"],
                abodefunctions.ABODEFUNCTIONS["i_to_j"],
            ),
            (
                abodefunctions.ABODEFUNCTIONS["i"],
                abodefunctions.ABODEFUNCTIONS["i_to_j"],
                abodefunctions.ABODEFUNCTIONS["i_off_j"],
            ),
        )
    )

    def detect_valid_combinations(size) -> tuple:
        if size % 2 == 0:
            res = ((2,) * (size // 2),)
            if size % 3 == 0:
                res += ((3,) * (size // 3),)
            return res
        else:
            remaing_size = size - 3
            amount_2 = remaing_size // 2
            elements = (3,) + ((2,) * amount_2)
            res = tuple(set(itertools.permutations(elements)))
            if size % 3 == 0:
                res += ((3,) * (size // 3),)
            return res

    valid_combinations = tuple(
        detect_valid_combinations(size + 2) for size in range(12)
    )
    valid_combinations = tuple(itertools.cycle(comb) for comb in valid_combinations)

    def interpolate_from_i_to_i(
        mode: modes.Mode,
        amount_units: int,
        func0: functions.Function,
        func1: functions.Function,
    ) -> abodefunctions.AbodefuncLine:
        def get_for2(is_i_strong: bool) -> tuple:
            if is_i_strong:
                return (
                    abodefunctions.ABODEFUNCTIONS["i"],
                    abodefunctions.ABODEFUNCTIONS["i0"],
                )
            else:
                return next(cycle_2)

        def get_for3(is_i_strong: bool) -> tuple:
            if is_i_strong:
                return next(cycle_3_strong)
            else:
                return next(cycle_3_weak)

        primes_abode = abodefunctions.AbodefuncLine.get_primes(mode, func0, func1)
        primes_mode = (mode.x, mode.y, mode.z, mode.U)
        is_i_strong = primes_mode.index(primes_abode[0]) < 2

        if amount_units == 2:
            data = (
                abodefunctions.ABODEFUNCTIONS["i"],
                abodefunctions.ABODEFUNCTIONS["i"],
            )
        else:
            combo = next(valid_combinations[amount_units - 3])
            afuncs = []
            for c in combo:
                if c == 2:
                    add = get_for2(is_i_strong)
                elif c == 3:
                    add = get_for3(is_i_strong)
                else:
                    raise NotImplementedError(c)
                afuncs.append(add)
            afuncs = functools.reduce(operator.add, afuncs)
            data = afuncs + (abodefunctions.ABODEFUNCTIONS["i"],)

        return abodefunctions.AbodefuncLine(*data)

    return interpolate_from_i_to_i


def interpolate_between_functions_lancar_style(
    mode: modes.Mode,
    func0: functions.Function,
    func1: functions.Function,
    abodefunc0: abodefunctions.AbodeFunction,
    abodefunc1: abodefunctions.AbodeFunction,
    amount_units: int,
) -> abodefunctions.AbodefuncLine:

    add_beginning = False
    if abodefunc0.signifier == subfunctions.TheEmptySign:
        amount_units -= 1
        add_beginning = True

    add_end = False
    if abodefunc1.signifier == subfunctions.TheEmptySign:
        amount_units -= 1
        add_end = True

    interpolation = interpolate_from_i_to_i(mode, amount_units, func0, func1)
    interpolation = tuple(interpolation.subfunctions)

    if add_beginning:
        interpolation = (abodefunc0,) + interpolation
    if add_end:
        interpolation = interpolation + (abodefunc1,)

    return abodefunctions.AbodefuncLine(*interpolation)


detect_abodefunctions_frame_lancaran = __mk_detect_af_frame_lancaran()
interpolate_from_i_to_i = __mk_interpolate_from_i_to_i_func()
