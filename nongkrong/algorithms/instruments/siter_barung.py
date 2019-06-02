from nongkrong.harmony import modes
from nongkrong.instruments import SITER_BARUNG

from mu.mel import mel
from mu.mel import ji
from mu.sco import old


def mk_simple_conversion(
    mode: modes.Mode, funcs: tuple, subfunctions_per_interpol: tuple
) -> old.JICadence:
    """Expect real functions (with applied modulation), not symbolic functions"""

    def get_from_func_pitch(func) -> ji.JIPitch:
        p = func(mode)
        if p.set_val_border(2).primes == (3,):  # 3 * 9 doesn't exist in current tuning
            return p.normalize(2) - ji.r(2, 1)
        else:
            return mel.TheEmptyPitch

    def filter_subfunc_pitch(pitch) -> ji.JIPitch:
        if pitch == ji.r(1, 1):
            pitch += ji.r(2, 1)
        if pitch in SITER_BARUNG.pitches:
            return pitch
        else:
            return mel.TheEmptyPitch

    res = []
    for func0, func1, subfuncline in zip(funcs, funcs[1:], subfunctions_per_interpol):
        fp = get_from_func_pitch(func0)
        subfunc_pitches = list(
            (filter_subfunc_pitch(p),)
            for p in subfuncline.convert_signifiers2pitches(mode, func0, func1)[:-1]
        )
        if fp:
            subfunc_pitches[0] = subfunc_pitches[0] + (fp,)
        for h in subfunc_pitches:
            h = tuple(p for p in h if p)
            res.append(h)

    return old.JICadence([old.Chord(ji.JIHarmony(h), 1) for h in res])
