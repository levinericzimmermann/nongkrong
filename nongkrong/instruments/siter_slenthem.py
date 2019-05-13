from nongkrong.instruments import instruments
from nongkrong.render import notation

from mu.mel import ji

import functools
import itertools
import operator


def __mk_siter_slenthem():
    pitches = (
        tuple(
            ji.r(functools.reduce(operator.mul, com), 1)
            for com in itertools.combinations((3, 5, 7, 9), 2)
        ),
    )
    pitches += (tuple(p.inverse().normalize(2) + ji.r(1, 2) for p in pitches[0]),)
    pitches = (tuple(p.normalize(2) + ji.r(1, 2) for p in pitches[0]), pitches[1])

    pitch2notation = tuple(
        instruments.mk_p2n(p, idx) for idx, p in enumerate(pitches)
    )
    pitch2notation = instruments.combine_p2n(*pitch2notation)

    notation_styles = tuple(
        notation.MelodicLineStyle("Large", label, False, True, False)
        for label in ("+", "-")
    )
    vertical_line = notation.VerticalLine(0.5, "", 1)
    vertical_line_style = notation.VerticalLineStyle(
        vertical_line, vertical_line, vertical_line
    )
    render_engines = (None, None)

    return instruments.Instrument(
        "Siter slenthem",
        pitch2notation,
        notation_styles,
        render_engines,
        vertical_line_style,
    )


SITER_SLENTHEM = __mk_siter_slenthem()
