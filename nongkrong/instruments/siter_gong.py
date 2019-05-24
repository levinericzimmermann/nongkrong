from nongkrong.instruments import instruments
from nongkrong.render import notation
from nongkrong.render import sound

from mu.mel import ji

import functools
import itertools
import operator


def __mk_siter_gong_complete():
    def mk_combination_pitches(comb: int, octave: ji.JIPitch):
        pitches = (
            tuple(
                ji.r(functools.reduce(operator.mul, com), 1)
                for com in itertools.combinations((3, 5, 7, 9), comb)
            ),
        )
        pitches += (tuple(p.inverse().normalize(2) + octave for p in pitches[0]),)
        return (tuple(p.normalize(2) + octave for p in pitches[0]), pitches[1])

    def mk_re():
        return sound.PyteqEngine(preset='"Cimbalom hard"')

    pitches_gong = mk_combination_pitches(3, ji.r(1, 4))
    pitches_tong = mk_combination_pitches(2, ji.r(1, 2))
    pitches = pitches_gong + pitches_tong

    pitch2notation = tuple(instruments.mk_p2n(p, idx) for idx, p in enumerate(pitches))
    pitch2notation = instruments.combine_p2n(*pitch2notation)

    notation_styles = tuple(
        notation.MelodicLineStyle("Large", label, False, True, False)
        for label in ("g+", "g-", "t+", "t-")
    )
    vertical_line_metrical = notation.VerticalLine(1.6, "", 1)
    vertical_line_compound = notation.VerticalLine(0.9, "", 1)
    vertical_line_unit = notation.VerticalLine(0.15, "", 1)
    vertical_line_style = notation.VerticalLineStyle(
        vertical_line_metrical, vertical_line_compound, vertical_line_unit
    )

    re = mk_re()
    render_engines = (re, re, re, re)

    return instruments.Instrument(
        "Siter_gong",
        pitch2notation,
        notation_styles,
        render_engines,
        vertical_line_style,
    )


def __mk_siter_gong_simplified():
    def mk_combination_pitches(comb: int, octave: ji.JIPitch):
        pitches = (
            tuple(
                ji.r(functools.reduce(operator.mul, com), 1)
                for com in itertools.combinations((3, 5, 7, 9), comb)
                if tuple(sorted(com)) != (3, 9)
            ),
        )
        pitches += (tuple(p.inverse().normalize(2) + octave for p in pitches[0]),)
        return tuple(p.normalize(2) + octave for p in pitches[0]), pitches[1]

    def mk_re():
        return sound.PyteqEngine(preset='"Cimbalom hard"')

    pitch_gong_plus = ji.r(3 * 5 * 7, 1).normalize(2) + ji.r(1, 4)
    pitch_gong_minus = pitch_gong_plus.inverse().normalize(2) + ji.r(1, 4)
    pitches_tong = mk_combination_pitches(2, ji.r(1, 2))
    pitches = (
        pitches_tong[0] + (pitch_gong_plus,),
        pitches_tong[1] + (pitch_gong_minus,),
    )

    pitch2notation = tuple(instruments.mk_p2n(p, idx) for idx, p in enumerate(pitches))
    pitch2notation = instruments.combine_p2n(*pitch2notation)

    notation_styles = tuple(
        notation.MelodicLineStyle("Large", label, False, True, False)
        for label in ("+", "-")
    )
    vertical_line_metrical = notation.VerticalLine(1.6, "", 1)
    vertical_line_compound = notation.VerticalLine(0.9, "", 1)
    vertical_line_unit = notation.VerticalLine(0.15, "", 1)
    vertical_line_style = notation.VerticalLineStyle(
        vertical_line_metrical, vertical_line_compound, vertical_line_unit
    )

    re = mk_re()
    render_engines = (re, re)

    return instruments.Instrument(
        "Siter_gong",
        pitch2notation,
        notation_styles,
        render_engines,
        vertical_line_style,
    )


SITER_GONG = __mk_siter_gong_simplified()
