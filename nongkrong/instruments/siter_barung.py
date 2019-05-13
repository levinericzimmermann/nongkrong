from nongkrong.instruments import instruments
from nongkrong.render import notation

from mu.mel import ji

import functools
import operator


def __mk_siter_barung():
    def mk_pitches(inverse=False):
        pitches0 = tuple(ji.r(p ** 2, 1) for p in (3, 5, 7, 9))
        pitches1 = tuple(ji.r(p, 1) for p in (17, 9, 5, 11, 3, 7))
        pitches2 = tuple(ji.r(1, 1) for p in (1,))
        octaves = (ji.r(1, 2), ji.r(1, 1), ji.r(2, 1))
        pitches = (pitches0, pitches1, pitches2)
        if inverse:
            pitches = tuple(tuple(p.inverse() for p in pi) for pi in pitches)
        return functools.reduce(
            operator.add,
            tuple(
                tuple(p.normalize(2) + o for p in pi) for pi, o in zip(pitches, octaves)
            ),
        )

    pitches0 = mk_pitches(False)
    pitches1 = mk_pitches(True)
    pitches = (pitches0, pitches1)
    pitch2notation = tuple(
        instruments.mk_p2n(p, idx) for idx, p in enumerate(pitches)
    )
    pitch2notation = instruments.combine_p2n(*pitch2notation)

    notation_styles = tuple(
        notation.MelodicLineStyle("Large", label, False, True, True)
        for label in ("+", "-")
    )
    vertical_line = notation.VerticalLine(0.5, "", 1)
    vertical_line_style = notation.VerticalLineStyle(
        vertical_line, vertical_line, vertical_line
    )
    render_engines = (None, None)

    return instruments.Instrument(
        "Siter_barung",
        pitch2notation,
        notation_styles,
        render_engines,
        vertical_line_style,
    )


SITER_BARUNG = __mk_siter_barung()
