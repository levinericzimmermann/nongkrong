from nongkrong.harmony import abodefunctions
from nongkrong.harmony import functions
from nongkrong.harmony import modes
from nongkrong.harmony import interfunctions
from nongkrong.harmony import subfunctions


from nongkrong.algorithms.harmony import abodefunctions as af_ag
from nongkrong.algorithms.harmony import interfunctions as if_ag


def detect_subfunctions_frame_for_every_pair_lancaran(
    mode: modes.Mode, next_mode: modes.Mode, funcs: tuple
) -> tuple:
    def is_playable(info0, info1) -> bool:
        return all(
            (
                info0[0] == info1[0],
                info0[1].signifier != subfunctions.TheEmptySign,
                info1[1].signifier != subfunctions.TheEmptySign,
            )
        )

    def convert_unplayable_interfunction(interfunc) -> interfunctions.InterFunction:
        if interfunc.signifier != subfunctions.TheEmptySign:
            if interfunc == interfunctions.INTERFUNCTIONS["d"]:
                return interfunctions.INTERFUNCTIONS["d00"]
            elif interfunc == interfunctions.INTERFUNCTIONS["b"]:
                return interfunctions.INTERFUNCTIONS["b00"]
            elif interfunc == interfunctions.INTERFUNCTIONS["ol"]:
                return interfunctions.INTERFUNCTIONS["ol00"]
            elif interfunc == interfunctions.INTERFUNCTIONS["lo"]:
                return interfunctions.INTERFUNCTIONS["lo00"]
            else:
                msg = "Unknown InterFunction {0}".format(interfunc)
                raise NotImplementedError(msg)
        else:
            return interfunc

    def convert_unplayable_abodefunctions(abodefunc) -> abodefunctions.AbodeFunction:
        if abodefunc.signifier != subfunctions.TheEmptySign:
            if abodefunc == abodefunctions.ABODEFUNCTIONS["i"]:
                return interfunctions.INTERFUNCTIONS["i00"]
            else:
                msg = "Unknown AbodeFunction {0}".format(abodefunc)
                raise NotImplementedError(msg)
        else:
            return abodefunc

    def convert_unplayable_subfunction(sf) -> subfunctions.SubFunction:
        typ = type(sf)
        if typ == interfunctions.InterFunction:
            return convert_unplayable_interfunction(sf)
        elif typ == abodefunctions.AbodeFunction:
            return convert_unplayable_interfunction(sf)
        else:
            msg = "Unknown type {0} of SubFunction {1}".format(typ, sf)
            raise NotImplementedError(msg)

    suggestions = []
    for idx, func0, func1 in zip(range(len(funcs)), funcs, funcs[1:]):
        if func0.identity == func1.identity:
            frame_func = af_ag.detect_abodefunctions_frame_lancaran
        else:
            frame_func = if_ag.detect_interfunctions_frame_lancaran
        suggestions.append(frame_func(mode, next_mode, funcs, idx))

    size_suggestions = len(suggestions)
    results = [[] for i in range(size_suggestions)]
    results[0].append(suggestions[0][0][1])

    for idx, sug0, sug1 in zip(range(size_suggestions), suggestions, suggestions[1:]):
        playable_or_not = is_playable(sug0[1], sug1[0])
        sf0, sf1 = sug0[1][1], sug1[0][1]
        if playable_or_not:
            sf0 = convert_unplayable_subfunction(sf0)
            sf1 = convert_unplayable_subfunction(sf1)

        results[idx].append(sf0)
        results[idx + 1].append(sf1)

    results[-1].append(suggestions[-1][1][1])

    return tuple(tuple(r) for r in results)


def interpolate_between_functions_lancar_style(
    mode: modes.Mode,
    func0: functions.Function,
    func1: functions.Function,
    subfunc0: subfunctions.SubFunction,
    subfunc1: subfunctions.SubFunction,
    amount_units: int,
) -> subfunctions.SubfuncLine:
    typ = type(subfunc0)
    if typ == interfunctions.InterFunction:
        interpolate_func = if_ag.interpolate_between_functions_lancar_style
    elif typ == abodefunctions.AbodeFunction:
        interpolate_func = af_ag.interpolate_between_functions_lancar_style
    else:
        msg = "Unknown type {0} of SubFunction {1}".format(typ, subfunc0)
        raise NotImplementedError(msg)

    return interpolate_func(mode, func0, func1, subfunc0, subfunc1, amount_units)


def interpolate_between_every_function_pair_lancar_style(
    mode: modes.Mode,
    next_mode: modes.Mode,
    funcs: tuple,
    amount_units_per_interpolation: tuple,
) -> tuple:
    frames = detect_subfunctions_frame_for_every_pair_lancaran(mode, next_mode, funcs)
    res = []
    for func0, func1, frame, amount_units in zip(
        funcs, funcs[1:], frames, amount_units_per_interpolation
    ):
        interpol = interpolate_between_functions_lancar_style(
            mode, func0, func1, frame[0], frame[1], amount_units + 1
        )
        res.append(interpol)
    return tuple(res)
