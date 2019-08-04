from nongkrong.instruments import instruments
from nongkrong.harmony import shortwriting as sw
from nongkrong.render import notation
from nongkrong.render import sound

from mu.mel import ji

import functools
import itertools
import operator


def __mk_kendang():
    def mk_re(pitches):
        def mk_pitch2samples(pitch):
            basic_path = "samples/kendang/new/"
            normalized_pitch = pitch.normalize(2)

            if normalized_pitch == ji.r(8, 7):
                basic_path += "0_"
            elif normalized_pitch == ji.r(5, 4):
                basic_path += "1_"
            elif normalized_pitch == ji.r(8, 5):
                basic_path += "2_"
            elif normalized_pitch == ji.r(7, 4):
                basic_path += "3_"
            else:
                basic_path += "4_"

            octave = pitch.octave

            if octave == 0:
                basic_path += "hand"
            elif octave == 1:
                basic_path += "tak"
            elif octave == -1:
                basic_path += "stick"
            else:
                msg = "Unknonw octave {0} of pitch {1}".format(octave, pitch)
                raise ValueError(msg)

            return itertools.cycle(
                ("{0}{1}.wav".format(basic_path, idx), 1) for idx in range(2)
            )

        pitch2sample = {pitch: mk_pitch2samples(pitch) for pitch in pitches}

        return sound.SampleEngine(pitch2sample)

    pitches = (
        sw.translate(".7- .7+ .5- .5+ .1", False),
        sw.translate("7- 7+ 5- 5+ 1", False),
        sw.translate("7-. 7+. 5-. 5+. 1.", False),
    )

    pitch2notation = tuple(
        instruments.mk_p2n(p, idx, False) for idx, p in enumerate(pitches)
    )
    pitch2notation = instruments.combine_p2n(*pitch2notation)

    notation_styles = tuple(
        notation.MelodicLineStyle("Large", "", True, True, True) for i in range(1)
    )
    vertical_line = notation.VerticalLine(0.5, "", 1)
    vertical_line_style = notation.VerticalLineStyle(
        vertical_line, vertical_line, vertical_line
    )

    re0 = mk_re(functools.reduce(operator.add, pitches))
    render_engines = (re0,)

    return instruments.Instrument(
        "Kendang", pitch2notation, notation_styles, render_engines, vertical_line_style
    )


KENDANG = __mk_kendang()
