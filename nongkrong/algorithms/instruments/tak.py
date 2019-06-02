from nongkrong.metre import metre

from mu.mel import ji
from mu.sco import old


import functools
import operator


def mk_loop_cadence(loopsize: int, meter: metre.Metre) -> old.JICadence:
    size = meter.size
    loop_amount = size // loopsize
    rest = size % loopsize
    harmony = ji.JIHarmony([ji.r(3, 2)])
    cadence = [old.Chord(harmony, loopsize) for i in range(loop_amount)]
    if rest:
        cadence.append(old.Chord(harmony, rest))
    return old.JICadence(cadence)


def mk_loop_cadence_with_tuk(loopsize: int, meter: metre.Metre) -> old.JICadence:
    size = meter.size
    loop_amount = size // loopsize
    rest = size % loopsize
    harmony0 = ji.JIHarmony([ji.r(3, 2)])
    harmony1 = ji.JIHarmony([ji.r(1, 1)])
    basic_cadence = [old.Chord(harmony0, 0.5)] + [
        old.Chord(harmony1, 1) for i in range(loopsize - 1)
    ]
    basic_cadence.append(old.Chord(harmony1, 0.5))
    print(old.JICadence(basic_cadence).duration)
    cadence = [basic_cadence for i in range(loop_amount)]
    cadence = functools.reduce(operator.add, cadence)
    if rest:
        cadence.append(old.Chord(harmony0, rest))
    return old.JICadence(cadence)
