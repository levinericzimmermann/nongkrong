from nongkrong.harmony import modes

from mu.mel import mel
from mu.mel import ji
from mu.sco import old

import functools
import operator


def mk_simple_conversion(
    mode: modes.Mode, compounds_per_function: tuple, funcs: tuple
) -> old.JICadence:
    def define_gong(mode) -> ji.JIPitch:
        gong_pitch = ji.r(functools.reduce(operator.mul, (mode.x, mode.y, mode.z)), 1)
        if not mode.gender:
            gong_pitch = gong_pitch.inverse()
        return gong_pitch.normalize(2) - ji.r(4, 1)

    def get_pitch(f) -> ji.JIPitch:
        p = f(mode)
        if p.set_val_border(2).primes == (3,):  # 3 * 9 doesn't exist in current tuning
            return mel.TheEmptyPitch
        else:
            return f(mode).normalize() - ji.r(2, 1)

    gong = define_gong(mode)
    pitches = tuple(get_pitch(f) for f in funcs)
    pitches = ((gong, p) if f.gong else (p,) for f, p in zip(funcs, pitches))

    return old.JICadence(
        [
            old.Chord(ji.JIHarmony(tuple(pi for pi in p if pi)), delay)
            for p, delay in zip(pitches, compounds_per_function)
        ]
    )
