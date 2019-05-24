import itertools

from nongkrong.instruments import instruments
from nongkrong.harmony import shortwriting as sw
from nongkrong.render import notation
from nongkrong.render import sound

from mu.mel import ji


def __mk_tak():
    def mk_re():
        def mk_tak_cycle():
            names = tuple("samples/klapper/{0}.wav".format(idx) for idx in range(5))
            return itertools.cycle(tuple((n, 1, 0.59) for n in names))

        def mk_schlitz_kurz_cycle():
            names = tuple(
                "samples/schlitztrommel/kurz/{0}.wav".format(idx) for idx in range(6)
            )
            return itertools.cycle(tuple((n, 1, 1.1) for n in names))

        def mk_schlitz_lang_cycle():
            names = tuple(
                "samples/schlitztrommel/lang/{0}.wav".format(idx) for idx in range(5)
            )
            return itertools.cycle(tuple((n, 1, 1.1) for n in names))

        short_pitch = ji.r(1, 1)
        long_pitch = ji.r(1, 2)
        tak_pitch = ji.r(3, 2)
        pitch2sample = {
            tak_pitch: mk_tak_cycle(),
            short_pitch: mk_schlitz_kurz_cycle(),
            long_pitch: mk_schlitz_lang_cycle(),
        }

        return sound.SampleEngine(pitch2sample)

    pitches = sw.translate("1 .1 3", False)

    pitch2notation = instruments.mk_p2n(pitches, 0)

    notation_styles = tuple(
        notation.MelodicLineStyle("Large", "", True, True, True) for i in range(1)
    )
    vertical_line = notation.VerticalLine(0.5, "", 1)
    vertical_line_style = notation.VerticalLineStyle(
        vertical_line, vertical_line, vertical_line
    )

    re = mk_re()
    render_engines = (re,)

    return instruments.Instrument(
        "Tak", pitch2notation, notation_styles, render_engines, vertical_line_style
    )


TAK = __mk_tak()
