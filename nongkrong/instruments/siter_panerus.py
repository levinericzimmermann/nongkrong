from nongkrong.instruments import instruments
from nongkrong.render import notation
from nongkrong.render import sound

from mu.mel import ji

import functools
import operator


def __mk_siter_panerus():
    def mk_pitches(inverse=False):
        pitches0 = tuple(ji.r(p, 1) for p in (9, 19, 5, 11, 3, 13, 7))
        pitches1 = tuple(ji.r(p, 1) for p in (1, 9, 5, 3, 7))
        octaves = (ji.r(1, 1), ji.r(2, 1))
        pitches = (pitches0, pitches1)
        if inverse:
            pitches = tuple(tuple(p.inverse() for p in pi) for pi in pitches)
        return functools.reduce(
            operator.add,
            tuple(
                tuple(p.normalize(2) + o for p in pi) for pi, o in zip(pitches, octaves)
            ),
        )

    def mk_re():
        return sound.PyteqEngine(preset='"Cimbalom hard"')

    pitches0 = mk_pitches(False)
    pitches1 = mk_pitches(True)
    pitches = (pitches0, pitches1)
    pitch2notation = tuple(instruments.mk_p2n(p, idx) for idx, p in enumerate(pitches))

    pitch2notation_plus, pitch2notation_minus = pitch2notation
    pitch2notation = instruments.combine_p2n(*tuple(pitch2notation))

    notation_styles = tuple(
        notation.MelodicLineStyle("Large", label, False, True, True)
        for label in ("+", "-")
    )
    vertical_line = notation.VerticalLine(0.5, "", 1)
    vertical_line_style = notation.VerticalLineStyle(
        vertical_line, vertical_line, vertical_line
    )

    re = mk_re()
    render_engines = (re, re)

    full = instruments.Instrument(
        "Siter_panerus",
        pitch2notation,
        notation_styles,
        render_engines,
        vertical_line_style,
    )

    plus = instruments.Instrument(
        "Siter_panerus",
        pitch2notation_plus,
        notation_styles[:1],
        render_engines[:1],
        vertical_line_style,
    )

    minus = instruments.Instrument(
        "Siter_panerus",
        pitch2notation_plus,
        notation_styles[1:],
        render_engines[1:],
        vertical_line_style,
    )

    return full, plus, minus


SITER_PANERUS, SITER_PANERUS_PLUS, SITER_PANERUS_MINUS = __mk_siter_panerus()
