from nongkrong.instruments import instruments
from nongkrong.harmony import shortwriting as sw
from nongkrong.render import notation
from nongkrong.render import sound

from mu.mel import ji

import itertools


def __mk_kendang():
    def mk_re(pitches):
        def mk_pitch2samples(pitch):
            basic_path = "samples/kendang/"
            samples_freq = (224.7, 204)
            if pitch.float > ji.r(2, 1).float:
                basic_path += "high/"
                samples_freq = tuple(f * 2 for f in samples_freq)
            else:
                basic_path += "low/"

            pitch_freq = pitch.float * sound.PyteqEngine.CONCERT_PITCH
            am_samples = tuple(tuple(r) for r in (range(5), range(4)))
            samples = []
            for idx, ams, fre in zip(range(2), am_samples, samples_freq):
                fac = pitch_freq / fre
                for num in ams:
                    na = "{0}{1}/{2}.wav".format(basic_path, idx, num)
                    samples.append((na, fac))
            return itertools.cycle(samples)

        pitch2sample = {pitch: mk_pitch2samples(pitch) for pitch in pitches}

        return sound.SampleEngine(pitch2sample)

    pitches = (
        sw.translate("7- 5+ 3- 3+. 5-. 7+", False),
        sw.translate("7-. 5+. 3-. 3+ 5- 7+.", False),
    )

    pitch2notation = tuple(
        instruments.mk_p2n(p, idx, False) for idx, p in enumerate(pitches)
    )
    pitch2notation = instruments.combine_p2n(*pitch2notation)

    notation_styles = tuple(
        notation.MelodicLineStyle("Large", "", True, True, True) for i in range(2)
    )
    vertical_line = notation.VerticalLine(0.5, "", 1)
    vertical_line_style = notation.VerticalLineStyle(
        vertical_line, vertical_line, vertical_line
    )

    re0 = mk_re(pitches[0] + pitches[1])
    render_engines = (re0, re0)

    return instruments.Instrument(
        "Kendang", pitch2notation, notation_styles, render_engines, vertical_line_style
    )


KENDANG = __mk_kendang()
