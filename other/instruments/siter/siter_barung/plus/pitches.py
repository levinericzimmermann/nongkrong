from nongkrong.harmony import shortwriting as sw
from mu.mel import ji

CONCERT_PITCH = 260

pitches = ".3++ .7++ .5++ .3+++ 9 19 5 11 3 13 7 1."
pitches = sw.translate(pitches, False)

name = "PLUS"


if __name__ == "__main__":
    import pyteqNew as pyteq

    for p_idx, pitch in enumerate(sorted(pitches)):
        local_name = name + str(p_idx)
        melody = [
            pyteq.MidiTone(ji.JIPitch(pitch, multiply=CONCERT_PITCH), 4, 4, volume=1)
        ]
        harp_range = tuple(n for n in range(20, 125))
        f = pyteq.Pianoteq(melody, available_midi_notes=harp_range)
        f.export2wav(local_name, preset='"Erard Player"')
