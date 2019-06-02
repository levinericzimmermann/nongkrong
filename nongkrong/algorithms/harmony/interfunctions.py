from nongkrong.algorithms.harmony import functions as f_ag
from nongkrong.harmony import functions
from nongkrong.harmony import modes
from nongkrong.harmony import interfunctions
from nongkrong.harmony import shortwriting as sw
from nongkrong.harmony import subfunctions

from mu.mel import ji


import itertools


def interpolate_from_d_to_b_lancar_style(
    mode: modes.Mode,
    nationalities: tuple,
    func0: functions.Function,
    func1: functions.Function,
) -> interfunctions.InterfuncLine:
    def are_interfunctions_strong(interfunc0, interfunc1, func0, func1) -> tuple:
        primes_inter = interfunctions.InterfuncLine.get_primes(mode, func0, func1)
        primes_mode = (mode.x, mode.y, mode.z, mode.U)
        return tuple(
            primes_mode.index(p) < 2 for p in (primes_inter[0], primes_inter[2])
        )

    def are_interfunctions_melodically_close(mode, func0, func1) -> bool:
        """Test if there is only one weak siter pitch between both
        interfunctions (for instance for 3/2 and 5/4 True, since
        there is only 11/8 inbetween, while False for 3/2 and 9/8,
        since 19/16, 5/4, 11/8 inbetween)
        """
        primes_inter = interfunctions.InterfuncLine.get_primes(mode, func0, func1)
        primes = primes_inter[0], primes_inter[2]
        spitches = "3 5 7 9"
        if mode.gender:
            pitches = (ji.r(p, 1) for p in primes)
        else:
            pitches = (ji.r(1, p) for p in primes)
            spitches = "!- {0}".format(spitches)
        scale = tuple(sorted(sw.translate(spitches, False)))
        positions = tuple(scale.index(p.normalize(2)) for p in pitches)
        return abs(positions[0] - positions[1]) == 1

    def solve_1to0(interfunc0, interfunc1, func0, func1) -> tuple:
        return (interfunc0,)

    def solve_0to1(interfunc0, interfunc1, func0, func1) -> tuple:
        return (interfunc1,)

    def solve_1to1(interfunc0, interfunc1, func0, func1) -> tuple:
        return interfunc0, interfunc1

    def solve_2to1(interfunc0, interfunc1, func0, func1) -> tuple:
        strongness = are_interfunctions_strong(interfunc0, interfunc1, func0, func1)
        closeness = are_interfunctions_melodically_close(mode, func0, func1)
        if all(strongness):
            return interfunc0, interfunctions.INTERFUNCTIONS["d0"], interfunc1
        elif closeness:
            return interfunc0, interfunctions.INTERFUNCTIONS["d_to_b"], interfunc1
        else:
            return interfunc0, interfunctions.INTERFUNCTIONS["d"], interfunc1

    def solve_3to1(interfunc0, interfunc1, func0, func1) -> tuple:
        closeness = are_interfunctions_melodically_close(mode, func0, func1)
        if closeness:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_off_b"],
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunc1,
            )
        else:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunc1,
            )

    def solve_1to2(interfunc0, interfunc1, func0, func1) -> tuple:
        strongness = are_interfunctions_strong(interfunc0, interfunc1, func0, func1)
        if all(strongness):
            return interfunc0, interfunctions.INTERFUNCTIONS["b0"], interfunc1
        else:
            return interfunc0, interfunctions.INTERFUNCTIONS["b_to_d"], interfunc1

    def solve_1to3(interfunc0, interfunc1, func0, func1) -> tuple:
        strongness = are_interfunctions_strong(interfunc0, interfunc1, func0, func1)
        if all(strongness):
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["b0"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunc1,
            )
        else:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )

    def solve_2to2(interfunc0, interfunc1, func0, func1) -> tuple:
        strongness = are_interfunctions_strong(interfunc0, interfunc1, func0, func1)
        closeness = are_interfunctions_melodically_close(mode, func0, func1)
        if closeness:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunc1,
            )
        elif strongness[0]:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunc1,
            )
        else:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunc1,
            )

    def solve_3to2(interfunc0, interfunc1, func0, func1) -> tuple:
        strongness = are_interfunctions_strong(interfunc0, interfunc1, func0, func1)
        closeness = are_interfunctions_melodically_close(mode, func0, func1)
        if all(strongness):
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b0"],
                interfunc1,
            )
        elif strongness[0]:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunc1,
            )
        elif not closeness or any(
            (func1 == functions.FUNCTIONS["m"], func1 == functions.FUNCTIONS["M"])
        ):
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunc1,
            )
        else:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_off_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunc1,
            )

    def solve_2to3(interfunc0, interfunc1, func0, func1) -> tuple:
        strongness = are_interfunctions_strong(interfunc0, interfunc1, func0, func1)
        closeness = are_interfunctions_melodically_close(mode, func0, func1)
        if all(strongness):
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b0"],
                interfunc1,
            )
        elif closeness and strongness[1]:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b0"],
                interfunc1,
            )
        elif closeness:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )
        elif strongness[0]:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )
        else:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )

    def solve_3to3(interfunc0, interfunc1, func0, func1) -> tuple:
        strongness = are_interfunctions_strong(interfunc0, interfunc1, func0, func1)
        closeness = are_interfunctions_melodically_close(mode, func0, func1)
        if closeness and strongness[0]:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b0"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunc1,
            )
        elif strongness[0]:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b0"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunc1,
            )
        elif closeness:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_off_b"],
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )
        else:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )

    def solve_4to3(interfunc0, interfunc1, func0, func1) -> tuple:
        strongness = are_interfunctions_strong(interfunc0, interfunc1, func0, func1)
        closeness = are_interfunctions_melodically_close(mode, func0, func1)
        if all(strongness):
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b0"],
                interfunc1,
            )
        elif strongness[0] and closeness:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )
        elif strongness[1] and closeness:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_off_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b0"],
                interfunc1,
            )
        elif closeness:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_off_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )
        else:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["d_off_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )

    def solve_3to4(interfunc0, interfunc1, func0, func1) -> tuple:
        strongness = are_interfunctions_strong(interfunc0, interfunc1, func0, func1)
        closeness = are_interfunctions_melodically_close(mode, func0, func1)
        if all(strongness):
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b0"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b0"],
                interfunc1,
            )
        elif strongness[1] and closeness:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_off_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b0"],
                interfunc1,
            )
        elif strongness[1]:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b0"],
                interfunc1,
            )
        elif strongness[0]:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )
        elif closeness:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_off_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )
        else:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )

    def solve_4to4(interfunc0, interfunc1, func0, func1) -> tuple:
        strongness = are_interfunctions_strong(interfunc0, interfunc1, func0, func1)
        closeness = are_interfunctions_melodically_close(mode, func0, func1)
        if strongness[1] and closeness:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_off_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b0"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )
        elif all(strongness):
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b0"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunc1,
            )
        elif closeness:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_off_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunc1,
            )
        elif strongness[0]:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["d0"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )
        elif strongness[1]:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_off_b"],
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b0"],
                interfunc1,
            )
        else:
            return (
                interfunc0,
                interfunctions.INTERFUNCTIONS["d_off_b"],
                interfunctions.INTERFUNCTIONS["d_to_b"],
                interfunctions.INTERFUNCTIONS["d"],
                interfunctions.INTERFUNCTIONS["b_to_d"],
                interfunctions.INTERFUNCTIONS["b"],
                interfunctions.INTERFUNCTIONS["b_off_d"],
                interfunc1,
            )

    interfunc0 = interfunctions.INTERFUNCTIONS["d"]
    interfunc1 = interfunctions.INTERFUNCTIONS["b"]

    solutions_per_nationalities = {
        (0, 1): solve_0to1,
        (1, 0): solve_1to0,
        (1, 1): solve_1to1,
        (2, 1): solve_2to1,
        (1, 2): solve_1to2,
        (1, 3): solve_1to3,
        (2, 2): solve_2to2,
        (3, 2): solve_3to2,
        (3, 1): solve_3to1,
        (2, 3): solve_2to3,
        (3, 3): solve_3to3,
        (4, 3): solve_4to3,
        (3, 4): solve_3to4,
        (4, 4): solve_4to4,
    }

    nationalities = tuple(nationalities)

    try:
        solution_maker = solutions_per_nationalities[nationalities]
    except KeyError:
        msg = "For nationalities {0} there hasn't been any ".format(nationalities)
        msg += "solution defined yet."
        raise NotImplementedError(msg)

    return interfunctions.InterfuncLine(
        *solution_maker(interfunc0, interfunc1, func0, func1)
    )


def __mk_interpolate_from_l_to_l():
    def mk_l_to_l_pattern() -> tuple:
        l_to_l_pattern = (
            (0,),
            (1,),
            (0, 0),
            (0, 1),
            (1, 1),
            (1, 0, 0),
            (1, 1, 0),
            (1, 1, 1),
            (1, 1, 0, 0),
            (1, 1, 1, 0),
            (1, 1, 1, 1),
            (1, 1, 1, 0, 0),
            (1, 1, 1, 1, 0),
            (1, 1, 1, 1, 1),
        )

        return tuple(
            itertools.cycle(set(itertools.permutations(sol))) for sol in l_to_l_pattern
        )

    l_to_l_pattern = mk_l_to_l_pattern()

    interpolations_l_to_l = (
        itertools.cycle(
            (("l", "l_to_d", "l"), ("l", "l_off_d", "l"), ("l", "l0", "l"))
        ),
        itertools.cycle(
            (("l", "l_off_d", "l_to_d", "l"), ("l", "l_to_d", "l_off_d", "l"))
        ),
    )

    def interpolate_from_l_to_l_lancar_style(
        mode: modes.Mode,
        nationalities: tuple,
        func0: functions.Function,
        func1: functions.Function,
    ) -> interfunctions.InterfuncLine:
        def interpolate_between_l_and_l(nationalities) -> tuple:
            size = sum(nationalities)

            if size == 1:
                res = (interfunctions.INTERFUNCTIONS["ol"],)
            elif size == 2:
                res = (
                    interfunctions.INTERFUNCTIONS["ol"],
                    interfunctions.INTERFUNCTIONS["lo"],
                )
            else:
                idx = size - 3
                try:
                    pattern = next(l_to_l_pattern[idx])
                except IndexError:
                    msg = "Amount units too big to interpolate between two l."
                    raise ValueError(msg)
                ifs = []
                is_first = True
                for p in pattern:
                    if is_first:
                        to_extend = next(interpolations_l_to_l[p])
                        is_first = False
                    else:
                        to_extend = next(interpolations_l_to_l[p])[1:]
                    ifs.extend(to_extend)

                nationalities = ((0,) * nationalities[0]) + ((1,) * nationalities[1])
                converted_ifs = []
                for nationality, ifname in zip(nationalities, ifs):
                    if nationality == 0:
                        ifname = "ol{0}".format(ifname[1:])
                    else:
                        ifname = "lo{0}".format(ifname[1:])
                    converted_ifs.append(interfunctions.INTERFUNCTIONS[ifname])

                res = converted_ifs
            return interfunctions.InterfuncLine(*res)

        return interpolate_between_l_and_l(nationalities)

    return interpolate_from_l_to_l_lancar_style


def __mk_detect_if_prime_and_interfunction_func():
    """Generate function that return 2-element tuple.
    Each element represents one interfunction. One element is
    composed by one 2-element-tuple, where those elements contain:
        1. Prime number of mode that shall be played (x, y, z or U)
        2. real InterFunction object

    necessary input:
        mode: modes.Mode, next_mode: modes.Mode, funcs: tuple, idx0: int
    """

    def is_left_neighbour(mode0, mode1) -> bool:
        return all(
            (
                mode0.U == mode1.U,
                mode0.z == mode1.z,
                mode0.x == mode1.y,
                mode0.y == mode1.x,
            )
        )

    def is_parallel(mode0, mode1) -> bool:
        return all(
            (
                mode0.U == mode1.z,
                mode0.z == mode1.U,
                mode0.x == mode1.x,
                mode0.y == mode1.y,
            )
        )

    def convert_mode_primes2interfunc_names(mode, func0, func1, *prime) -> tuple:
        primes_inter = interfunctions.InterfuncLine.get_primes(mode, func0, func1)
        mode_primes = (mode.x, mode.y, mode.z, mode.U)
        interfunc_names = ("d", "l", "b")
        return tuple(interfunc_names[primes_inter.index(mode_primes[p])] for p in prime)

    def return_primes_and_interfunctions(
        prime0: int, is_played0: bool, prime1: int, is_played1: bool
    ):
        """Simple solution for relationship where always the same
        solution will be returned"""

        def func(mode, next_mode, funcs, idx0, idx1) -> tuple:
            func0, func1 = funcs[idx0], funcs[idx1]
            localp0, localp1 = int(prime0), int(prime1)

            if idx1 + 1 == len(funcs) and mode != next_mode:
                func1 = f_ag.convert_function_due_to_modulation(func1, mode, next_mode)
                localp1 = f_ag.convert_relevant_prime_due_to_modulation(
                    localp1, mode, next_mode
                )

            data = []
            for idx, p, is_played in (
                (0, localp0, is_played0),
                (1, localp1, is_played1),
            ):
                ifn = convert_mode_primes2interfunc_names(mode, func0, func1, p)[0]
                if ifn == "l":
                    if idx == 0:
                        ifn = "ol"
                    else:
                        ifn = "lo"
                if not is_played:
                    ifn = "{0}00".format(ifn)
                iff = interfunctions.INTERFUNCTIONS[ifn]
                data.append((p, iff))
            return tuple(data)

        return func

    def return_primes_and_interfunctions_for_m2o():
        basic = return_primes_and_interfunctions(1, False, 1, True)

        def func(mode, next_mode, funcs, idx0, idx1) -> tuple:

            conditions = (idx1 + 2 == len(funcs), is_left_neighbour(mode, next_mode))

            if all(conditions):
                primes = (2, 0)
                func0, func1 = funcs[idx0], funcs[idx1]
                interfuncs = tuple(
                    interfunctions.INTERFUNCTIONS[name]
                    for name in convert2valid_l_names(
                        convert_mode_primes2interfunc_names(mode, func0, func1, *primes)
                    )
                )
                return tuple(zip(primes, interfuncs))

            else:
                return basic(mode, next_mode, funcs, idx0, idx1)

        return func

    def convert2valid_l_names(res) -> tuple:
        assert len(res) == 2
        res = list(res)
        if res[0] == "l":
            res[0] = "ol"
        if res[1] == "l":
            res[1] = "lo"
        return tuple(res)

    def return_primes_and_interfunctions_for_o2M():
        basic = return_primes_and_interfunctions(1, True, 1, False)

        def func(mode, next_mode, funcs, idx0, idx1) -> tuple:

            is_last = idx1 + 1 == len(funcs)
            conditions_mod_ln = (is_last, is_left_neighbour(mode, next_mode))
            conditions_mod_parallel = (is_last, is_parallel(mode, next_mode))

            if all(conditions_mod_ln):
                primes = (0, 0)
                func0, func1 = funcs[idx0], functions.FUNCTIONS["w"]
                interfuncs = tuple(
                    interfunctions.INTERFUNCTIONS[name]
                    for name in convert2valid_l_names(
                        convert_mode_primes2interfunc_names(mode, func0, func1, *primes)
                    )
                )
                return tuple(zip(primes, interfuncs))

            elif all(conditions_mod_parallel):
                primes = (1, 1)
                func0, func1 = funcs[idx0], functions.FUNCTIONS["om"]
                interfuncs = tuple(
                    interfunctions.INTERFUNCTIONS[name]
                    for name in convert2valid_l_names(
                        convert_mode_primes2interfunc_names(mode, func0, func1, *primes)
                    )
                )
                return tuple(zip(primes, interfuncs))

            else:
                return basic(mode, next_mode, funcs, idx0, idx1)

        return func

    resolution_dict = {
        ("M", "o"): return_primes_and_interfunctions(1, False, 1, True),
        ("o", "M"): return_primes_and_interfunctions_for_o2M(),
        ("m", "o"): return_primes_and_interfunctions_for_m2o(),
        ("o", "m"): return_primes_and_interfunctions(1, True, 1, False),
        ("M", "w"): return_primes_and_interfunctions(2, False, 2, True),
        ("m", "w"): return_primes_and_interfunctions(2, True, 2, True),
        ("w", "m"): return_primes_and_interfunctions(2, True, 2, True),
        ("w", "o"): return_primes_and_interfunctions(2, True, 1, True),
        ("o", "w"): return_primes_and_interfunctions(1, True, 2, True),
        ("m", "n"): return_primes_and_interfunctions(2, True, 2, False),
        ("n", "m"): return_primes_and_interfunctions(2, False, 2, True),
        ("m", "om"): return_primes_and_interfunctions(2, True, 3, True),
        ("om", "m"): return_primes_and_interfunctions(3, True, 2, True),
        ("w", "n"): return_primes_and_interfunctions(2, True, 2, False),
        ("n", "w"): return_primes_and_interfunctions(2, False, 2, True),
        ("w", "ow"): return_primes_and_interfunctions(2, True, 3, True),
        ("ow", "w"): return_primes_and_interfunctions(3, True, 2, True),
        ("o", "om"): return_primes_and_interfunctions(1, True, 1, False),
        ("om", "o"): return_primes_and_interfunctions(1, False, 1, True),
        ("o", "ow"): return_primes_and_interfunctions(1, True, 3, True),
        ("ow", "o"): return_primes_and_interfunctions(3, True, 1, True),
    }

    resolution_dict = {
        tuple(functions.FUNCTIONS[fn] for fn in key): resolution_dict[key]
        for key in resolution_dict
    }

    def func(mode: modes.Mode, next_mode: modes.Mode, funcs: tuple, idx0: int) -> tuple:
        idx1 = idx0 + 1
        subfunctions = funcs[idx0], funcs[idx1]
        return resolution_dict[subfunctions](mode, next_mode, funcs, idx0, idx1)

    return func


def split_nationalities(
    amount_units: int, func0: functions.Function, func1: functions.Function
) -> tuple:
    def detect_function_hierarchy(func0, func1) -> bool:
        """return True if func0 > func1"""
        hierarchy = {"n": 0, "om": 1, "ow": 2, "m": 3, "w": 4, "o": 5, "M": 6}
        hierarchy = {functions.FUNCTIONS[name]: hierarchy[name] for name in hierarchy}
        return hierarchy[func0] > hierarchy[func1]

    half = amount_units // 2
    modulo = amount_units % 2
    if modulo == 0:
        return half, half
    else:
        if detect_function_hierarchy(func0, func1):
            return half + modulo, half
        else:
            return half, half + modulo


def interpolate_between_functions_lancar_style(
    mode: modes.Mode,
    func0: functions.Function,
    func1: functions.Function,
    interfunc0: interfunctions.InterFunction,
    interfunc1: interfunctions.InterFunction,
    amount_units: int,
) -> interfunctions.InterfuncLine:
    nationalities = split_nationalities(amount_units, func0, func1)
    nationalities = list(nationalities)

    add_beginning = False
    if interfunc0.signifier == subfunctions.TheEmptySign:
        nationalities[0] -= 1
        add_beginning = True

    add_end = False
    if interfunc1.signifier == subfunctions.TheEmptySign:
        nationalities[1] -= 1
        add_end = True

    if interfunc0.signified == interfunc1.signified:
        interpolate_function = interpolate_from_l_to_l_lancar_style
    else:
        interpolate_function = interpolate_from_d_to_b_lancar_style

    if sum(nationalities) > 0:
        interpolation = interpolate_function(mode, nationalities, func0, func1)
        interpolation = tuple(interpolation.subfunctions)
    else:
        interpolation = tuple([])

    if add_beginning:
        interpolation = (interfunc0,) + interpolation

    if add_end:
        interpolation = interpolation + (interfunc1,)

    interpolation = interfunctions.InterfuncLine(*interpolation)

    return interpolation


interpolate_from_l_to_l_lancar_style = __mk_interpolate_from_l_to_l()
detect_interfunctions_frame_lancaran = __mk_detect_if_prime_and_interfunction_func()
