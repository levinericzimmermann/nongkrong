from nongkrong.instruments import instruments
from nongkrong.render import notation
from nongkrong.render import sound
from mu.mel import ji

import functools
import operator


def __mk_kecapi(inverse: bool, is_positive: bool):
    def mk_pitches(main, side, inverse=False):
        if main == 9:
            primes = (5, 7)
        else:
            primes = (3, 5, 7)
        special = functools.reduce(operator.mul, tuple(p for p in primes if p != main))
        if is_positive and not inverse:
            p0 = ji.r(main, 1)
            p1 = ji.r(main, special)
        elif not is_positive and not inverse:
            p0 = ji.r(main, special)
            p1 = ji.r(main, 1)
        elif is_positive and inverse:
            p0 = ji.r(special, main)
            p1 = ji.r(1, main)
        elif not is_positive and inverse:
            p0 = ji.r(1, main)
            p1 = ji.r(special, main)
        else:
            raise ValueError()

        p0 = p0.normalize(2)
        p1 = p1.normalize(2) + ji.r(4, 1)

        p_between = (ji.r(main, s) for s in side)
        if inverse:
            p_between = (p.inverse() for p in p_between)
        p_inbetween = tuple(p.normalize(2) + ji.r(2, 1) for p in p_between)
        return (p0,) + p_inbetween + (p1,)

    def mk_re():
        harp_range = tuple(range(20, 110))
        se = sound.PyteqEngine(
            preset='"Concert Harp Recording"', available_midi_notes=harp_range
        )
        return se

    primes = (9, 7, 5, 3)
    pitches = tuple(
        mk_pitches(p, tuple(s for s in primes if s != p), inverse) for p in primes
    )

    pitch2notation = tuple(instruments.mk_p2n(p, idx) for idx, p in enumerate(pitches))
    pitch2notation = instruments.combine_p2n(*pitch2notation)

    notation_styles = tuple(
        notation.MelodicLineStyle("Large", "", True, False, True) for i in range(4)
    )
    vertical_line = notation.VerticalLine(0.5, "", 1)
    vertical_line_style = notation.VerticalLineStyle(
        vertical_line, vertical_line, vertical_line
    )
    re = mk_re()
    render_engines = (re, re, re, re)

    if inverse:
        name = "Kecapi_minus"
    else:
        name = "Kecapi_plus"

    return instruments.Instrument(
        name, pitch2notation, notation_styles, render_engines, vertical_line_style
    )


KECAPI_PLUS_PLU = __mk_kecapi(False, True)
KECAPI_MINUS_PLU = __mk_kecapi(True, True)
KECAPI_PLUS_MIN = __mk_kecapi(False, False)
KECAPI_MINUS_MIN = __mk_kecapi(True, False)
